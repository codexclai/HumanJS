# HumanJS — current session handoff

**Updated:** 2026-11-10  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Verified main HEAD at handoff creation:** `1eeb9a25d2f8218c86431f974606e8e8b3f06bc0`.

## Verified repository state

- Public repository; default branch is `main`.
- The live branch listing contains exactly `main`.
- No open issues or pull requests were returned by the live checks.
- Latest full workflow: run `42829736271`, successful on `1eeb9a25d2f8218c86431f974606e8e8b3f06bc0`.
- The preceding code commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304` also passed the full workflow in run `42829179222`.

## Current implementation

The Rust workspace `crates/humanjs-core` contains:
1. A validated, single-compartment passive RC membrane mechanism, analytically integrated for constant injected current.
2. A single effective glutamatergic synapse model with separate AMPA/NMDA biexponential conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic short-term availability/depression/recovery.
3. A coupled membrane/synapse integration method using interval-mean conductances and a midpoint magnesium-block approximation. Both live states are committed atomically only on a successful step.

Current full CI passed:
- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --locked`: 10 unit tests and 9 integration tests passed.
- `python3 .github/scripts/repository_policy.py`: passed.

The two earlier synapse CI attempts found Rust formatting differences and then a Clippy too-many-arguments warning. Formatting was applied and the solver inputs were regrouped into typed model/conductance parameters. The final workflow passed; no test was weakened.

## Scientific boundaries

- Passive membrane human evidence and limitations: `research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md`.
- Human L2/L3 glutamatergic synapse evidence and parameter provenance: `research/HUMAN-CORTICAL-GLUTAMATERGIC-SYNAPSE.md`.
- AMPA/NMDA waveform and conductance parameters are fitted/effective parameters, not single-receptor molecular transition-rate measurements.
- The depression parameters are fitted at the human pyramidal-pyramidal connection level and applied to one effective contact as a computational reduction.
- Explicit presynaptic calcium/release-site/fusion, cleft glutamate dynamics/uptake, molecular receptor Markov/desensitization states, dendritic spines/cable, and inhibitory synapses remain unimplemented.
- Tests and CI establish software behavior only. No biological validation is claimed.

## Next concrete work

Investigate an evidence-bounded human neocortical spike-initiation mechanism. Prefer direct human patch-clamp data and primary models that disclose their fitted parameters, preparation, anatomy, and uncertainty. Keep direct measurements separate from model-fitted channel parameters and cross-species transfers. Do not introduce a threshold-only spike generator or a generic Hodgkin-Huxley parameter set and present it as a human neuron.

A likely route is to inspect the human L2/L3 pyramidal-cell somatic/axonal models and their supplementary parameter tables, determine which active conductances are genuinely constrained by human recordings, then select the smallest integrated mechanism supported by that evidence. The passive and synaptic modules remain the current CPU correctness baseline.

Still not implemented: action-potential generation, 10,000-unit configurable spiking population, dendritic morphology/multicompartment integration, connected populations/networks, long-term plasticity/learning, checkpoint/save-restore, Rust-native concurrency, JSON model loading, Python, C ABI, C++ wrapper, and integrated WGSL GPU execution.

A fresh local clone was attempted but this environment could not resolve `github.com`; verification has therefore been via GitHub Actions, not a local checkout. Recheck the live main HEAD, branch list, open issues/PRs, current workflow results, and full tree before future changes.
