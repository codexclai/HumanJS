# HumanJS — current status

**As of:** 2026-11-11
**Stage:** two integrated Rust CPU mechanisms; canonical human pyramidal-model source audit and a six-cell NEURON reproduction are recorded. No intrinsic spike generator is implemented.

## Canonical repository and verification

- Repository: \`codexclai/HumanJS\`, public, default branch \`main\`.
- \`main\` is the sole project branch; the live branch list returned exactly \`main\`.
- No open issues or pull requests were returned by the live checks.
- The latest verified implementation/experiment commit before this documentation refresh was \`38caae89b44782c4631e81c5765ab47c4cde4129\`.
- GitHub Actions run \`42891382380\` passed on that exact commit: https://github.com/codexclai/HumanJS/actions/runs/42891382380.

The workflow verified:
- \`cargo fmt --all -- --check\`
- \`cargo clippy --workspace --all-targets -- -D warnings\`
- \`cargo test --workspace --locked\` — 10 unit tests and 9 integration tests passed; 0 failed.
- Python syntax parsing of \`experiments/reproduce_eyal_figure7a.py\`.
- \`python3 .github/scripts/repository_policy.py\` — passed (16 required files; no JSON files; no prohibited archives or generated output).

The new commit added experiment/research tooling and no Rust simulation code. The existing Rust tests were not modified or weakened.

## Implemented HumanJS CPU mechanisms

### Passive membrane

The Rust workspace \`crates/humanjs-core\` contains:
- Validated SI wrappers for voltage, current, capacitance, conductance, input resistance, and membrane time constant.
- Integer-nanosecond simulation time and positive step durations.
- Separate passive model parameters, initial conditions, and live runtime state.
- A single-compartment passive RC equation integrated analytically for piecewise-constant injected current.
- Derivation of lumped capacitance and leak conductance from supplied input resistance and time constant.
- Failed-step handling that does not partially update membrane state.

### Glutamatergic synapse

The CPU synapse contains independent AMPA-like and NMDA-like normalized biexponential conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic presynaptic availability/depression/recovery. The membrane step uses interval-mean conductances and midpoint NMDA unblock. The membrane and synapse states update transactionally.

The mechanism is an effective conductance abstraction for an adult human L2/L3 pyramidal-to-pyramidal evidence context, not a complete molecular or ultrastructural synapse. It excludes stochastic vesicle fusion, presynaptic calcium/release-site machinery, cleft glutamate dynamics/uptake, receptor Markov/desensitization states, dendritic spines/cable, and inhibitory inputs.

## Human spike-initiation evidence and external model reproduction

The canonical evidence record is \`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md\`. The reproducible external model audit is \`experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md\`, with runner \`experiments/reproduce_eyal_figure7a.py\`.

### Eyal et al. (2018) canonical source audit

The official 139,316,573-byte ModelDB archive for model 238347 was retrieved, integrity-tested, and audited. SHA-256: \`12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b\`. The archive is not stored in this repository.

The six HOC models map directly to the six Table S4 cell parameter sets. The active spike-model templates insert nine conductance mechanisms in soma and axon plus \`CaDynamics_E2\`; \`Ca_HVA\` is present in the archive but is not inserted by those six templates, and \`NMDA.mod\` is a separate synaptic mechanism. The HOC parameter assignments confirm the 29-parameter organization: nine maximum conductances, three NaTg parameters and two Ca-dynamics parameters per compartment, plus shared \`e_pas\`. The six models use a two-section, 60 μm axon stub; dendritic branches remain passive. The models assume rodent-like channel kinetic forms, so fitted conductances and transferred kinetics remain distinct evidence classes.

The ten mechanisms actually inserted by those six templates were compiled from the original archive with NEURON 9.0.2. A Python 3 reproduction of the Figure 7A model-construction and stimulus sequence ran all six cells and compared first-spike metrics with the released repeated human current-clamp traces. The checked-in runner was executed successfully against the canonical archive in the cloud VM (Python 3.10.12, NEURON 9.0.2). The result table and methodological details are recorded in the experiment report.

The comparison showed some close matches and visible timing/width/peak differences for several cells. It verifies source availability, HOC-to-Table-S4 mapping, channel compilation, and model execution; it is not an independent model refit, exact trace match, or biological validation.

### Wilbers et al. (2023) human Na+/K+ mechanism audit

The pure human \`na_human.mod\` and \`k_human.mod\` files were retrieved from the CC0 DataverseNL deposit, checksum-verified, compiled unchanged, and probed in NEURON 9.0.2. Both explicitly set \`Rb = Ra\`. The K+ file matches Table S2 and its first optimizer result, while the fit script's later final dictionary differs; the script also assigns \`h12factor_k_human\`, which is not declared in the pure K+ mechanism. The paper's 14-parameter methods count remains unreconciled with the visible staged fit/assignment variables.

A direct compiled \`trap0\` call at each stored gate singularity returns a non-finite value. In the Na+ mechanism, all 200 nodes of its active −120 to +100 mV lookup table were finite; the exact singularities are off-grid. With the Na+ table disabled, exact-singularity rates are non-finite. The K+ mechanism's table is commented out; exact gate singularities are non-finite, and two opposite-sign branch triggers produced negative inactivation time constants. This numerical issue is documented; the original source has not been modified, and HumanJS does not silently claim a patched source is an exact reproduction.

The full Wilbers voltage-clamp fitting workflow was not rerun from raw traces. The public per-cell workbook summaries are not raw current recordings, and the NWB traces were absent from the 65-file Dataverse version examined.

## Implementation boundary — no AP code

HumanJS still does not generate action potentials. The Wilbers mechanisms represent human somatic nucleated-patch voltage-clamp behavior and exclude the AIS. Eyal's six-cell models include soma and a 60 μm axon stub but use rodent-like channel kinetics and passive dendrites. Human NaV1.2/NaV1.6 AIS immunolocalization supplies subtype-location evidence, not functional conductance or gating values.

A future somatic nucleated-patch-equivalent model must be explicitly distinguished from an anatomical soma/AIS neuron. Its gate equations must handle the source's numerical edge cases intentionally and be checked against human voltage-clamp targets. The K+ parameter discrepancy and the methods parameter-count discrepancy remain unresolved. No threshold-only event, generic rodent Hodgkin–Huxley set, or AIS conductance inferred from immunostaining has been added.

## Not yet implemented

- A configurable default of 10,000 spiking neuron units or any AP-generating mechanism.
- An evidence-bounded somatic-patch-equivalent model or anatomical AIS model.
- Explicit presynaptic calcium/release machinery, stochastic vesicle fusion, glutamate-cleft dynamics/uptake, and molecular receptor-state kinetics.
- Dendritic morphology/spines/cable filtering, multicompartment integration, populations, and connected networks.
- Long-term synaptic plasticity or learning.
- Runtime save/restore/checkpointing or safe interruption/resumption.
- Rust-native multi-threaded simulation execution.
- JSON model-definition loading and schema validation.
- Python developer package, stable C ABI, C++ wrapper, or integrated WGSL backend.

These remain requirements or future objectives, not current capabilities.

## Next implementation milestone

Resolve the remaining Wilbers K+ fit/parameter-count discrepancies and define an independently specified, numerically stable human somatic-patch-equivalent Na+/K+ model. Validate its gate responses against published human voltage-clamp summaries and its action-potential waveform against the available human current-clamp targets. Keep this preparation-equivalent model separate from an anatomical soma/AIS model. Do not claim biological validation from software or external model reproduction tests.
