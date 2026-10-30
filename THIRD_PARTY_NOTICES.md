# Upstream and third-party notices

The `iLED` dependency is the unmodified upstream 1.11.14 CPython 3.10 Linux
x86-64 wheel. Its package metadata declares `License: Proprietary`.

The original wheel is stored as a Release asset. Its SHA-256 is recorded in
`snapshot.json` and pinned in `pyproject.toml`. Native modules and embedded
resources are retained unchanged.

The integration installs an `iLED` entry point that uses the local activation
override from the captured environment. It also adds `CDLE/AutoRun/__init__.py`
to normalize native job-script headers. These modifications are documented
explicitly and are separate from the original wheel.

Upstream copyright and any third-party rights remain with their respective
owners. Consult the relevant owners for applicable license terms. VASP,
pseudopotential libraries, activation files and authentication credentials are
not included in this repository or the uploaded assets.
