# BERHOT infrastructure — planned secure runtimes

Existing infrastructure folders for [Cloudflare R2](cloudflare/README.md), [PostgreSQL](postgres/README.md), and [Docker](docker/README.md) are setup documentation/scaffolds, not deployed production resources.

Future [sandbox](sandbox/README.md), [scheduler](scheduler/README.md), [independent evaluation](evaluation/README.md) and [GPU training](training/README.md) directories describe the security boundaries required before unattended work.

No containers or services are launched, no cloud buckets created, and no secrets modified by this architecture scaffold. Read [security](../docs/security-and-governance.md) and [Pipeline](../docs/pipeline-end-to-end.md).
