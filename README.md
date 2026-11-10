# HumanJS

HumanJS is an open-source scientific-software project pursuing a comprehensive, scientifically defensible computational model of the human brain.

**Current stage:** the first CPU implementation slice is present: a typed, single-compartment passive membrane model with exact integration for constant injected current. This is a narrow subthreshold mechanism, not a complete neuron or working/validated brain.

## Scope

HumanJS models the brain, not the whole human body. It is not a chatbot, external-LLM wrapper, generic AI-agent framework, or a claim of consciousness, sentience, human-equivalent intelligence, clinical validity, or biological completeness. An external host may provide body, peripheral-sensory, actuator, and environment systems through explicit interfaces.

## Approved technologies

| Technology | Intended role |
|---|---|
| Rust | Native computational core, simulation runtime, biological mechanisms, APIs, concurrency, persistence |
| WGSL | GPU compute kernels |
| Python | Primary developer-facing API, scientific workflows, experiments, analysis, tooling |
| C | Native interoperability through a C ABI |
| C++ | Native interoperability and ergonomic wrappers |

## Start here

1. Read `docs/BOOT.md` at the beginning of every development session.
2. Follow `docs/PROJECT-INSTRUCTIONS.md` and its mandatory reading order.
3. Review `docs/OWNER-REQUIREMENTS.md`, the system architecture, and the brain-scope specification.
4. Check `docs/status/STATUS.md` for the verified implementation state.

GitHub `main` is the sole source of truth. The ChatGPT Project Sources area may remain empty; no uploaded source or separately synchronized archive is needed.

## First CPU mechanism

The current mechanism is a single passive membrane patch. It accepts explicit SI-valued capacitance, leak conductance, equilibrium potential, initial voltage, injected current, and integer-nanosecond time steps. It does not yet implement active channels, synaptic receptors, dendrites, action potentials, neuron populations, or network connectivity.

Run the native checks with:

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --locked
```

## Scientific and engineering standards

Biological mechanisms must be represented by causal models, not software labels or generic substitutes. Record research provenance, species, evidence type, uncertainty, parameter origin, validation status, and limitations. Distinguish measured biology from estimates, model conventions, hypotheses, and engineering constraints.

The configurable default of 10,000 spiking neuron units is an engineering starting point, not a biological neuron-count claim or a hard maximum. Save/restore and native multi-threaded execution remain requirements. CPU execution and graceful fallback are mandatory; GPU acceleration is not claimed until integrated and measured on supported hardware.

## License and ownership

HumanJS is licensed under Apache License, Version 2.0. Owner original contributions are attributed in `NOTICE`. Contributors retain copyright in their own contributions; the license governs redistribution and use. See `LICENSE` and `NOTICE`.
