# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** initial Rust CPU mechanism implemented; scientific and integration work continues.

## Canonical repository

- Repository: `codexclai/HumanJS`.
- Visibility: public. Default branch: `main`.
- GitHub `main` is the sole authoritative source. ChatGPT Project Sources may remain empty.
- The live branch listing returned exactly one branch, `main`; no non-main refs remained.
- No open issues or open pull requests were returned by the latest live checks.
- Before this implementation commit, the latest repository-policy workflow passed on commit `fccb71e43a66ebab09a54f54c06d7e8d4438d824` (run `42819045682`, success). That check validated repository policy only; it was not a code build, simulation test, or biological validation.

## Implemented CPU slice

The new Rust workspace contains `humanjs-core` with:

- Validated physical-unit wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation timestamps and positive step durations.
- Separate passive membrane model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC membrane equation driven by piecewise-constant injected current, integrated using its analytic exponential solution.
- A conversion from input resistance and membrane time constant to lumped leak conductance and capacitance (`G = 1/R`, `C = tau/R`).
- Validation and failure behavior that avoids partially updating runtime state when a step fails.
- Numerical and behavioral tests for the analytic response, relaxation, step partitioning, hyperpolarization, reset, unit conversion, and time overflow.

The model is a deliberately limited subthreshold mechanism. It is not a complete neuron and contains no active ion channels, synaptic receptors, dendrites, action potentials, population/network connectivity, or biological parameter defaults. The tests establish software behavior for the declared equation only.

## Evidence and scientific boundary

`research/HUMAN-NEOCORTEX-PASSIVE-MEMBRANE.md` records human whole-cell patch-clamp evidence for layer-dependent passive membrane properties and notable within-layer heterogeneity. The initial model does not claim to reproduce the full distribution or the active sag behavior reported in those recordings. Its parameters must be supplied explicitly; no group mean is treated as a universal human neuron.

## Not yet implemented

- A configurable default of 10,000 spiking neuron units or any spiking neuron mechanism.
- Synaptic transmission, receptor kinetics, vesicle release, plasticity, or active conductances.
- Multicompartment morphology, population scheduling, or connected network dynamics.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Verification and environment

The GitHub Actions workflow now runs Rust formatting, Clippy, workspace tests, and the repository policy validator on pushes to `main`. The result for this implementation commit must be checked before reporting these commands as passed.

A fresh local clone was attempted but this execution environment could not resolve `github.com`; no local checkout or local Rust test run was produced. Repository updates were made through GitHub's Git data API and must be verified through the remote commit and workflow results.

## Next implementation milestone

Add conductance-based synaptic input with explicit receptor/transmitter kinetics and evidence records, then test causal current/voltage effects and interaction with the passive membrane. Keep parameters provenance-tagged and do not substitute a generic exponential conductance for receptor kinetics without documenting its abstraction boundary. Follow with an evidence-bounded spike-initiation mechanism, population integration, checkpointing, and Rust-native concurrency.
