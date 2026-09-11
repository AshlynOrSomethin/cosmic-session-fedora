# cosmic-session (Fedora 44 fork)

Fork of Fedora's `cosmic-session` dist-git package, tracking the `f44` branch,
with `cosmic-term` changed from a hard `Requires` to a `Suggests` so the
session doesn't pull in cosmic-term unconditionally.

A scheduled GitHub Actions workflow ([sync-fedora.yml](.github/workflows/sync-fedora.yml))
merges upstream Fedora f44 changes on top of this patch automatically. Each
push triggers a Copr rebuild via webhook, so the built package's release is
always the upstream Fedora release plus our own commit(s) on top.

Built package: https://copr.fedorainfracloud.org/coprs/AshlynOrSomethin/cosmic-session-fedora/
