# HumanJS

HumanJS is an open-source scientific-software project pursuing a comprehensive, scientifically defensible computational model of the human brain.

**Current stage:** the Rust CPU core now contains an integrated passive membrane and a bounded human L2/L3 glutamatergic synapse mechanism. The synapse uses receptor-specific effective conductance waveforms, voltage-dependent NMDA magnesium block, and deterministic short-term depression/recovery. This is a limited computational mechanism, not a complete neuron, complete synapse, or working/validated brain.

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

## Current CPU mechanisms

The passive membrane module represents one lumped compartment with capacitance, leak conductance, an effective zero-current equilibrium, initial voltage, injected current, and integer-nanosecond simulation time. Constant-current steps use the analytic passive RC solution.

The glutamatergic synapse module adds AMPA- and NMDA-like biexponential conductance waveforms, a voltage-dependent NMDA magnesium-unblock factor, and a deterministic presynaptic resource model for short-term depression and recovery. The synaptic live state couples to the passive membrane using interval-mean conductances and a midpoint approximation for NMDA magnesium unblock.

The synapse parameter fixture is based on human L2/L3 pyramidal-neuron literature and is explicitly supplied in tests. It is not installed as a default model. The implementation does not yet model explicit glutamate release/cleft dynamics, stochastic vesicle fusion, receptor Markov states, dendritic spines/cable structure, action-potential generation, or connected neuron populations.

A separate external NEURON experiment audits the canonical Eyal et al. six-cell human L2/L3 soma/axon model and compares selected Figure 7A spike responses with released human recordings. Its source mapping, reproduction code and limitations are documented under `experiments/`; this is not an AP mechanism implemented in HumanJS.

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
