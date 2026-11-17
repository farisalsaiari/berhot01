# BERHOT company-wide repository layout

The architecture separates product interfaces from commercial APIs,
cross-model AI services, model-family training, infrastructure and data.

| Directory | Ownership |
| --- | --- |
| apps/ | Customer web console, developer portal, internal operations interfaces |
| platform/ | Public APIs, identity, organizations/tenant isolation, billing, usage and audit |
| core/ | Global filesystem roots, runtime settings and local storage primitives |
| services/ | Shared Data Factory, memory, knowledge graph, model dispatch, inference, evaluation, registry and async jobs |
| models/ | Independent JSM, FANN, Nabra, Bahr, Edrak and possible future image model |
| infrastructure/ | Containers, compute, scheduler, R2, database, deployment, monitoring, security |
| configs/ | Environment/model configuration pointer (existing YAML policies remain at core/configs/) |
| policies/ | Governance policy pointer; current draft YAMLs are NOT enforced |
| storage/ | Non-code local output; datasets, model artifacts, releases, state, caches and temporary files |
| docs/ | Design decisions, runbooks, safety and API docs |
| tests/ | Integration and security tests that cross package boundaries |
| tools/ | Developer operational utilities (future) |

**Important design rules**

1. Global filesystem roots belong in core/paths.py.
2. Each service/family may have a small local paths.py deriving paths from core.
3. Data Factory prepares data; only separately verified release logic can
   authorize a train-ready dataset. A model-family tokenizer defines token IDs.
4. Model-family training owns weights and checkpoint logic.
5. Each run records dataset ID/hash, tokenizer ID/hash, code revision and
   immutable config, with checkpoints nested inside the run.
6. Promote releases only after independent evaluation and authorization.
7. R2/S3 object URIs are not Python filesystem Path objects.
8. No deployed service is implied by a README or empty placeholder module.
9. Do not split into microservices until independent scaling/security demands it.
10. Company HR, payroll and accounting may remain trusted third-party systems.

**Package migration**

The root shared Python package is core for the current monorepo.
Eventually a distribution named berhot_core reduces namespace collisions.
For JSM prefer an installed berhot_jsm package under models/jsm/src/.
Do not rewrite historical experimental checkpoint code to match scaffolding.
