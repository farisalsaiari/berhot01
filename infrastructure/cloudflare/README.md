# Cloudflare R2: future local-to-cloud mirror

The repository only defines *planned* mappings. These commands do not provision buckets or upload anything until you explicitly configure credentials and run them. Never commit access keys.

| Local payload root | Private R2 bucket | Object key |
| --- | --- | --- |
| `storage/data/` | `berhot-data` | Same relative path |
| `storage/memory/` | `berhot-memory` | Same relative path |
| `storage/artifacts/` | `berhot-artifacts` | Same relative path |

There is no extra `berhot-memory/` folder inside the bucket. Example: local `storage/memory/shared/knowledge/claims/v1/0001.json` corresponds to `s3://berhot-memory/shared/knowledge/claims/v1/0001.json`.

## Windows PowerShell preview (AWS CLI installed, R2 profile configured)

```powershell
$env:BERHOT_R2_ENDPOINT = "https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com"
aws s3 sync storage/data/ s3://berhot-data/ --profile r2 --region auto --endpoint-url $env:BERHOT_R2_ENDPOINT --exclude "*.gitkeep" --dryrun
aws s3 sync storage/memory/ s3://berhot-memory/ --profile r2 --region auto --endpoint-url $env:BERHOT_R2_ENDPOINT --exclude "*.gitkeep" --dryrun
aws s3 sync storage/artifacts/ s3://berhot-artifacts/ --profile r2 --region auto --endpoint-url $env:BERHOT_R2_ENDPOINT --exclude "*.gitkeep" --dryrun
```

All three buckets must exist with appropriate private permissions before syncing. Remove `--dryrun` only after reviewing paths and permissions. Do not use `--delete` as an ordinary mirror operation. Avoid overwriting published objects: use versioned snapshots. Do not sync `storage/incoming/`, `storage/cache/` or `storage/tmp/`; this last directory contains the local live SQLite prototype DB.

Empty Git directories exist thanks to `.gitkeep`. As R2 is object storage, those empty prefixes only appear after real objects have been uploaded. GitHub does not store actual empty directories.
