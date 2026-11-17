# AnalyseFuture

This directory preserves material that is useful for study or recovery but is not part of the active PDF Studio application. It is excluded from Docker build context and from Python package discovery. It is still tracked in Git, so it is **not** private storage or a security boundary.

`upstream-reference-snapshots/` contains the exact extracted files previously stored under `reference-archives/`; its README records original archive names and hashes. Do not execute or import these sources as product code without reviewing their exact license, provenance, dependencies, security, and output behavior. The 25 `issue6286` PDFs lack embedded provenance metadata.

The text reports here record the starting tree, every starting tracked path and its disposition, the 95 feature targets, branch findings, archive moves, security limits, and follow-up work. `WORK_PROGRESS.txt` is the handoff point if work is resumed. The active application remains in `app/`, with its normal `tests/`, `scripts/`, and `docs/` paths.
