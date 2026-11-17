# Independent evaluator infrastructure (planned)

Production evaluator must live in a separate trust boundary from candidate-generation and training agents. Protect hidden holdouts, evaluator credentials, signed result receipts and release permissions. Candidate agents must not edit the tests or simply assert their own score.

Proposed code: `services/learning/evaluation/`; policies `configs/evaluation-policy.yaml`, `release-policy.yaml`. No trusted evaluator or canary is active.
