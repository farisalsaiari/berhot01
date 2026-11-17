# PostgreSQL backend — planned

SQLite in `services/memory/store.py` is the current working local prototype. PostgreSQL migrations, access controls, indexes, transactional outbox/event processing, backups, rights revocation and production deployment have not been implemented. This directory reserves the integration boundary; do not assume an operational database exists.
