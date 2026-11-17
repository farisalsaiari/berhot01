# BERHOT security and governance — actual guarantees vs plans

**Implemented for local text MVP**
- Explicit input allowlist, .txt and UTF-8 only, max file/batch sizes.
- SHA-256 source integrity check and immutable content-addressed output.
- Local path traversal and symlink checks at inspection time.
- Operator-declared retention + analysis rights; training always denied.
- Source originals left untouched; no hidden eval access or GPU tasks.

**Not implemented**
- Authentication of declared rights, lawful provenance or user approvals.
- Malware scanning, antivirus, PII detection and privacy redaction.
- Isolated execution of untrusted documents, production authorization.
- Independent evaluator, secret management, audit service, billing.
- Production R2, database migrations, model release approval, rollback.

Existing core/configs security, rights, training and release YAMLs are
DESIGN-ONLY. They do not enforce policy just because they exist.

**Public repository warning**
The current Git history includes example intake files that may look like
personal or corporate documents. New ignore rules prevent accidentally
adding more untracked intake, but do not remove already tracked content.
Audit rights and privacy before publishing. If removal is required,
obtain an explicit, reviewed migration and history-remediation plan.

Data from an unverified source must not become train-ready by renaming a
folder. Training release requires independently verified approvals and
lineage; customer data requires tenant-specific purpose/consent controls.
