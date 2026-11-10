# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** first Rust CPU mechanism implemented and its focused CI checks passed; scientific and integration work continues.

## Canonical repository

- Repository: `codexclai/HumanJS`.
- Visibility: public. Default branch: `main`.
- GitHub `main` is the sole authoritative source. ChatGPT Project Sources may remain empty.
- The live branch listing returned exactly one branch, `main`; no non-main refs remained.
- No open issues or open pull requests were returned by the latest live checks.
- Current verified implementation head: `66f56730dbef0075132e21263ea9b679f3f2e154`.
- Workflow run `42824933385` passed for that commit: https://github.com/codexclai/HumanJS/actions/runs/42824933385.

## Implemented CPU slice

The Rust workspace contains `humanjs-core` with:

- Validated physical-unit wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation timestamps and positive step durations.
- Separate passive membrane model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC membrane equation driven by piecewise-constant injected current, integrated using its analytic exponential solution.
- A conversion from input resistance and membrane time constant to lumped leak conductance and capacitance (`G = 1/R`, `C = tau/R`).
- Validation and failure behavior that avoids partially updating runtime state when a step fails.
- Numerical and behavioral tests for the analytic response, relaxation, step partitioning, hyperpolarization, reset, unit conversion, invalid physical parameters, non-finite values, and time overflow.

The model is a deliberately limited subthreshold mechanism. It is not a complete neuron and contains no active ion channels, synaptic receptors, dendrites, action potentials, population/network connectivity, or biological parameter defaults. The tests establish software behavior for the declared equation only.

## Evidence and scientific boundary

`research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md` records human whole-cell patch-clamp evidence for layer-dependent passive membrane properties and notable within-layer heterogeneity. The initial model does not claim to reproduce the full distribution or the active sag behavior reported in those recordings. Its parameters must be supplied explicitly; no group mean is treated as a universal human neuron.

## Verification

For commit `66f56730dbef0075132e21263ea9b679f3f2e154`, GitHub Actions run `42824933385` completed successfully and verified:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --locked` — 6 unit tests and 6 integration tests passed; 0 failed.
- `python3 .github/scripts/repository_policy.py` — repository policy passed (16 required files; no JSON files; no prohibited archives/generated output).

The first implementation commit `a2161ef41f08238bef0b5014d5f4fc5f2a1a2761` initially failed the formatting gate only; the Rust sources were formatted in `66f56730dbef0075132e21263ea9b679f3f2e154`, then the full workflow passed. No lint, test, or policy failure occurred in the successful run.

A fresh local clone was attempted but this execution environment could not resolve `github.com`; no local checkout or local Rust test run was produced. Verification above was performed by the GitHub Actions runner against the committed repository state.

## Not yet implemented

- A configurable default of 10,000 spiking neuron units or any spiking neuron mechanism.
- Synaptic transmission, receptor kinetics, vesicle release, plasticity, or active conductances.
- Multicompartment morphology, population scheduling, or connected network dynamics.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Next implementation milestone

Add conductance-based synaptic input with explicit receptor/transmitter kinetics and evidence records, then test causal current/voltage effects and interaction with the passive membrane. Keep parameters provenance-tagged and do not substitute a generic exponential conductance for receptor kinetics without documenting its abstraction boundary. Follow with an evidence-bounded spike-initiation mechanism, population integration, checkpointing, and Rust-native concurrency.
