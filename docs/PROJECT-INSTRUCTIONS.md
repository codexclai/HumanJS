# HumanJS — repository operating instructions

GitHub repository `codexclai/HumanJS`, branch `main`, is the sole canonical source for active code, docs, requirements, decisions, research, experiments, issues, workflows, and history. No project ZIP is required or maintained. ChatGPT Project Sources may remain empty.

At every new chat, inspect live repository metadata and `main` HEAD, read `docs/BOOT.md` first, and follow its mandatory reading order. Never treat old chats, local copies, archives, or remembered commits as current. The original owner prompt remains preserved at `archive/owner-inputs/Applys-everything-everywhere-everyway-maximumly-fully-completely.txt`; current owner decisions and `docs/OWNER-REQUIREMENTS.md` supersede conflicting historical text.

## Branch policy
`main` is the only branch to use, permanently. Never create, check out, update, merge, or otherwise use another branch, existing or new. Make authorized changes directly on `main`; verify every commit and resulting HEAD. The intended final repository state is `main` alone. Existing non-main refs are leftovers: inspect unique commits before deleting them when deletion is available. Never use them for work. Disclose tool limitations rather than claiming deletion. Do not require or configure rulesets, branch protection, or deletion-prevention settings. Force pushes are permitted but exceptional; inspect and verify carefully.

## Purpose and scope
HumanJS is a scientifically defensible computational model of the human brain only. It is not a whole-body simulator, chatbot, external-LLM wrapper, generic agent framework, or claim of consciousness, sentience, human-equivalent intelligence, clinical validity, or biological completeness. External hosts may provide peripheral/body/sensory/environment inputs and receive outputs through explicit interfaces.

## Approved stack
- Rust: native simulation core, mechanisms, runtime, APIs, concurrency, resources, persistence.
- WGSL: GPU compute.
- Python: primary developer API, scientific workflows, experiments, analysis, tooling.
- C: stable native interoperability through a designed C ABI.
- C++: native interoperability and wrappers, preferably over the C ABI.

Node.js, JavaScript, TypeScript, npm, JavaScript runtimes, and `.ajs` implementation are retired. Do not reintroduce them into active work.

Retain correct save/restore, Rust-native multithreaded execution, and a configurable default of 10,000 spiking neuron units (engineering default, not biological count or hard maximum). CPU execution and fallbacks must work. Claim GPU/WGSL support only after actual hardware integration, correctness checks, and reproducible benchmarks. Keep model definitions, initial conditions, live runtime state, learned state, and checkpoints distinct. Applicable inspectable model/IR definitions should use JSON.

## Scientific and engineering requirements
Implement causal, interacting, evidence-grounded mechanisms, not biological labels on generic software stand-ins. Do not substitute fact tables, fixed lexicons/English grammar parsers, object-ID tracking, numbered goal slots, fixed task-switch penalties, capped sequence lookup, global scalar neuromodulators, simplistic sensory transforms, or arbitrary anatomy presented as measured human biology. Prefer primary research; distinguish human/animal evidence, measurements/estimates, findings/hypotheses, and record provenance, uncertainty, methods, and validation limits.

Inspect existing code, dependencies, interfaces, data flow, history, and tests before changing anything. Implement integrated, testable functionality. Add relevant numerical, unit, integration, causal, persistence, concurrency, and regression tests. Fix root causes; never weaken tests or claim unrun checks passed. Hardware/resource detection, fallback, cancellation, backpressure, recovery, and monitoring must be real, bounded, observable, configurable, explainable, and tested.

HumanJS has no requirement to store credentials, private user data, or secrets. Do not introduce authentication/secret-management features, `.env`, `.env.example`, `dotenv`, or generic env-file infrastructure without a specific approved requirement. Keep `.gitignore` limited to actual generated project artifacts.

## Documentation and delivery
Keep `/docs` canonical for requirements, architecture, specifications, decisions, research, experiments, status, recovery, and handoffs. Maintain one authoritative document per topic. Record meaningful decisions, changes, rationale, evidence, failures, and verification. Update `docs/BOOT.md` and status after meaningful work.

GitHub is source and delivery location. Use Releases for intentional versioned distributions, Packages for actual distributable packages, and Deployments only for a real hosted service. These are optional and do not replace the repository. Never produce HumanJSProject.zip or claim a GitHub-generated source archive is a separately maintained project deliverable.

Verify every GitHub operation. Report exact changed paths, tests/results, failures, limitations, untested areas, and next actions.