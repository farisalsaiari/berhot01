# Experiment sandbox (planned)

**No executable sandbox is implemented here.** Future code-generated Python, tool-use and simulation experiments require disposable isolated containers/VMs with: no production secrets, strict allowed mounts, network disabled by default, CPU/GPU/memory/time quotas, kill switch, immutable test fixtures and externalized experiment logs.

Never claim `services/learning/experiments/sandbox.py` provides isolation until an actual sandbox runner and negative security tests exist. Proposed policy: `configs/experiment-policy.yaml`.
