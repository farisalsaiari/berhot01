# Bounded GPU training orchestration (planned)

Future training jobs use immutable approved dataset manifests, replay sets, baseline checkpoint hashes, budget authorization and isolated GPU runtime. Every result is an **unreleased candidate** evaluated independently. Avoid downloading redundant datasets or uploading a running local SQLite DB.

Planned code: `services/learning/training/` and existing family-specific train scripts under `models/`. No automatic GPU execution is enabled.
