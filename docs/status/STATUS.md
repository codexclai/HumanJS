# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** two integrated Rust CPU mechanisms implemented; latest full verification passed.

## Canonical repository

- Repository: `codexclai/HumanJS`.
- Current session handoff: `docs/status/SESSION-HANDOFF.md`.
- Visibility: public. Default branch: `main`.
- GitHub `main` is the sole authoritative source. ChatGPT Project Sources may remain empty.
- The live branch listing returned exactly one branch, `main`; no non-main refs remained.
- No open issues or open pull requests were returned by the latest live checks.
- Verified implementation commit: `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304`.
- Successful full workflow: run `42829179222`, commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304`: https://github.com/codexclai/HumanJS/actions/runs/42829179222.

## Implemented CPU mechanisms

### Passive membrane

The Rust workspace `crates/humanjs-core` contains:
- Validated SI wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation time and positive step durations.
- Separate passive model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC equation integrated analytically for piecewise-constant injected current.
- Derivation of lumped capacitance and leak conductance from supplied input resistance and time constant.
- Failed-step handling that does not partially update membrane state.

### Glutamatergic synapse

A first integrated, CPU-only excitatory synaptic mechanism contains:
- Independent AMPA-like and NMDA-like normalized biexponential conductance kernels.
- Explicit conductance peak, rise time, and decay time parameters, validated so decay is longer than rise.
- NMDA voltage-dependent magnesium unblock using gamma, extracellular magnesium concentration, and the Jahr-Stevens coefficient.
- A deterministic presynaptic availability model with utilization and exponential recovery, fitted to the effective short-term depression/recovery scale reported for adult human L2/L3 pyramidal-to-pyramidal connections.
- An integrated membrane step that uses interval-mean receptor conductances and a midpoint estimate for NMDA magnesium unblock.
- Transactional coupled updates: a failed step leaves both membrane runtime state and synapse runtime state unchanged.

The current synapse parameter fixture uses explicit human L2/L3 literature-based values in tests. It is not a universal default or a direct microscopic measurement of all receptor parameters.

## Scientific evidence and limitations

- `research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md` records human layer-specific passive membrane measurements and their limitations.
- `research/HUMAN-CORTICAL-GLUTAMATERGIC-SYNAPSE.md` records human adult L2/L3 pyramidal-to-pyramidal evidence, the fitted AMPA/NMDA conductance-waveform parameters, short-term depression/recovery fits, and a separate pyramidal-to-interneuron study that is deliberately not used as the parameter source for the selected connection class.

The synapse remains a bounded abstraction. It does not simulate presynaptic action potentials, calcium entry, docked/releasable vesicles, stochastic fusion, multivesicular release, explicit synaptic-cleft glutamate concentration/diffusion/uptake, molecular AMPA/NMDA Markov states or desensitization, dendritic spines/cable structure, or local NMDA dendritic spikes. It applies a connection-level depression fit to one effective contact as an explicit reduction. Tests establish computational behavior for these equations; they do not biologically validate the mechanism.

## Verification

For commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304`, GitHub Actions run `42829179222` completed successfully and verified:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --locked` — 10 unit tests and 9 integration tests passed; 0 failed.
- `python3 .github/scripts/repository_policy.py` — repository policy passed (16 required files; no JSON files; no prohibited archives or generated output).

The first synapse commit needed formatting changes; the formatting gate then passed. Clippy identified an overly wide helper signature, which was refactored to pass typed synapse model/conductance values instead. The successful run above passed all checks. No tests were weakened or skipped in the successful workflow.

A fresh local clone was attempted but this execution environment could not resolve `github.com`; no local checkout or local Rust test run was produced. The reported verification was performed by the GitHub Actions runner against the committed repository state.

## Not yet implemented

- A configurable default of 10,000 spiking neuron units or an intrinsic spike-generation mechanism.
- Active voltage-gated membrane currents or calibrated human axon-initial-segment/somatic excitability.
- Explicit presynaptic release machinery, stochastic vesicle fusion, glutamate-cleft dynamics/uptake, and molecular receptor-state kinetics.
- Dendritic morphology/spines/cable filtering, multiple neuron compartments, population scheduling, and connected network dynamics.
- Long-term synaptic plasticity or learning.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Next implementation milestone

Add an evidence-bounded intrinsic spike-initiation mechanism to the existing passive membrane and synaptic-current path. Gather direct human neuronal evidence where available and keep any axon-initial-segment, channel-density, and kinetic parameters provenance-tagged; do not simply transfer a rodent model and label it human. Follow with multi-compartment/dendritic integration, population interactions, persistence, and native concurrency.
