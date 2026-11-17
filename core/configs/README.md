# BERHOT policies and configuration

**Status: Design-only for all newly added policy YAMLs.** Only existing services that explicitly load a config enforce it; the new files here DO NOT change existing behavior. Until authenticated validators and enforcement are implemented, values like `training_allowed`, `source_verified` and `human_approval` in untrusted inputs are **claims**, not authorization.

- `memory.yaml`, `rights.yaml`, `model_registry.yaml` are existing references.
- `learning-policy.yaml`: when to learn, required evidence, default autonomy disabled.
- `curiosity-policy.yaml`: bounded question generation and research.
- `experiment-policy.yaml`: isolation, quotas and repeatability.
- `capability-taxonomy.yaml`: capability skills across model families.
- `dataset-policy.yaml`: rights, dedup and immutable dataset releases.
- `training-policy.yaml`: training eligibility and catastrophic-forgetting guard.
- `evaluation-policy.yaml`: independent and leakage-resistant evaluations.
- `evolution-policy.yaml`: allowed changes, genealogy and independent tournament.
- `compute-budget.yaml`: **illustrative** SAR limits; not approved or enforced.
- `release-policy.yaml`: signed releases, manual promotion and rollback.
- `security-policy.yaml`: privilege boundaries and untrusted-data isolation.
- `memory-lifecycle.yaml`: retention, corrections and eventual rights revocation.

Policies must eventually be versioned, authenticated, validated, logged, and tested at their execution boundary. Never interpret comments or YAML alone as a runtime security guarantee.

See [end-to-end pipeline](../docs/pipeline-end-to-end.md).
