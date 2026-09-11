#!/usr/bin/env python3
"""Recompute Release: in cosmic-session.spec as "<fedora-release>.1<dist>".

Queries Koji for the newest cosmic-session build known to Fedora 44
(preferring updates-testing, since that's freshest) and rewrites the spec's
Release field and %changelog so this fork's build NVR always outranks
Fedora's official one for the same Version.
"""
import re
import subprocess
import sys
import xmlrpc.client
from datetime import date

SPEC = "cosmic-session.spec"
TAGS = ["f44-updates", "f44-updates-testing", "f44"]


def _version_key(version):
    parts = re.split(r"[.~^]", version)
    return [(0, int(p)) if p.isdigit() else (1, p) for p in parts]


def latest_nvr():
    proxy = xmlrpc.client.ServerProxy(
        "https://koji.fedoraproject.org/kojihub", allow_none=True
    )
    candidates = []
    for tag in TAGS:
        builds = proxy.listTagged(tag, None, False, None, True, "cosmic-session")
        candidates.extend(builds)
    if not candidates:
        return None, None
    best = max(
        candidates,
        key=lambda b: (_version_key(b["version"]), _version_key(b["release"])),
    )
    return best["version"], best["release"]


def main():
    fedora_version, fedora_release = latest_nvr()
    if fedora_version is None:
        print("No Fedora build found for cosmic-session on f44*, skipping")
        return 0

    spec = open(SPEC).read()

    our_version = re.search(r"^Version:\s*(\S+)", spec, re.M).group(1)
    if fedora_version != our_version:
        print(
            f"Fedora version ({fedora_version}) differs from spec version "
            f"({our_version}); leaving Release alone, a version bump merge "
            "is expected to handle this"
        )
        return 0

    # Koji's release includes the dist tag (e.g. "1.fc44"); strip it since
    # our spec appends %{?dist} itself.
    fedora_release = re.sub(r"\.fc\d+$", "", fedora_release)

    new_release_line = f"Release:        {fedora_release}.1%{{?dist}}"
    old_release_match = re.search(r"^Release:.*$", spec, re.M)
    if old_release_match and old_release_match.group(0) == new_release_line:
        print("Release already up to date")
        return 0

    spec = re.sub(r"^Release:.*$", new_release_line, spec, count=1, flags=re.M)

    today = date.today().strftime("%a %b %d %Y")
    entry = (
        f"* {today} github-actions[bot] "
        "<41898282+github-actions[bot]@users.noreply.github.com> "
        f"- {fedora_version}-{fedora_release}.1\n"
        f"- Sync with Fedora's {fedora_version}-{fedora_release} build\n\n"
    )
    spec = re.sub(r"^%changelog\n", "%changelog\n" + entry, spec, count=1, flags=re.M)

    open(SPEC, "w").write(spec)
    print(f"Updated Release to {fedora_release}.1%{{?dist}}")
    subprocess.run(["git", "add", SPEC], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
