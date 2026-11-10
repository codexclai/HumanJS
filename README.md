# HumanJS

HumanJS is an open-source project pursuing a scientifically defensible computational model of the human brain. Its implementation is being redesigned around Rust, WGSL, Python, C, and C++.

**Current stage:** repository and governance foundation. The new simulation implementation has not yet been migrated or created here. This repository must not be represented as a working or biologically validated brain.

## Scope

HumanJS models the brain, not the whole human body. It is not a chatbot, external-LLM wrapper, generic AI-agent framework, or a claim of consciousness, sentience, human-equivalent intelligence, or biological completeness. An external host may provide body, peripheral-sensory, actuator, and environment systems through explicit interfaces.

## Approved technologies

| Technology | Intended role |
|---|---|
| Rust | Native computational core, simulation runtime, biological mechanisms, native APIs, concurrency, persistence |
| WGSL | GPU compute kernels |
| Python | Primary developer-facing API, scientific workflows, experiments, analysis, tooling |
| C | Native interoperability through a C ABI |
| C++ | Native interoperability and ergonomic wrappers |

Node.js, JavaScript, TypeScript, npm, and JavaScript runtimes are discontinued project technologies. Do not reintroduce them without a later explicit owner decision. Historical work belongs only in a clearly marked legacy archive after review.

## Start here

1. Read docs/BOOT.md.
2. Follow docs/PROJECT-INSTRUCTIONS.md.
3. Review docs/OWNER-REQUIREMENTS.md and docs/architecture/SYSTEM-ARCHITECTURE.md.
4. Use GitHub history, issues, pull requests, workflows, and repository content as the project record.

The owner is Thamindu. The current GitHub account handle is transitional and may change. Do not use it as the owner preferred name.

## Scientific and engineering standards

Biological mechanisms must be represented by causal models, not software labels or generic substitutes. Record research provenance, species, evidence type, uncertainty, parameter origin, validation status, and limitations. Distinguish measured biology from estimates, model conventions, hypotheses, and engineering constraints.

The owner-requested default of 10,000 spiking neuron units is a configurable engineering starting point, not a biological neuron-count claim or a hard maximum. Save/restore and native multi-threaded execution remain requirements. CPU execution and graceful fallback are mandatory; GPU acceleration is not claimed until implemented and measured on supported hardware.

## License and ownership

HumanJS is licensed under Apache License, Version 2.0. The owner original contributions are attributed to Thamindu. Contributors retain copyright in their own contributions; the license governs redistribution and use. See LICENSE and NOTICE.