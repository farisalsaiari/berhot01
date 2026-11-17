# Autonomous scheduler infrastructure (planned)

A future queue/worker system will handle idempotent learning-task leases, durable state transitions, retries, fairness, cancellation, daily research scans and budgets. Workers must not bypass signed policies. No recurring training job is created by this scaffold.

Proposed code: `services/learning/scheduler.py`, `state_machine.py`. Runtime state eventually belongs under local `storage/state/scheduler/`, not disposable cache.
