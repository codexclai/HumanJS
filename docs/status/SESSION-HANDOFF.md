# HumanJS — current session handoff

**Updated:** 2026-11-11
**Canonical repository:** \`codexclai/HumanJS\`, branch \`main\` only.
**Last fully verified implementation/experiment commit:** \`38caae89b44782c4631e81c5765ab47c4cde4129\`.

## Verified repository state

- Public repository; default branch \`main\`.
- Live branch listing contains exactly \`main\`.
- No open issues or pull requests were returned by live checks.
- Full GitHub Actions workflow run \`42891382380\` passed on the commit above: https://github.com/codexclai/HumanJS/actions/runs/42891382380.
- The workflow passed Rust formatting, Clippy, 19 Rust tests, experiment-runner AST syntax validation, and repository policy.
- The code commit for the two current native CPU mechanisms, \`d561df97ae0bbd1012d8cd3bb3b0e466e4f78304\`, passed its own full workflow in run \`42829179222\`.

## Current HumanJS implementation

The Rust core \`crates/humanjs-core\` contains two integrated CPU mechanisms:
1. A validated single-compartment passive RC membrane, analytically integrated for piecewise-constant injected current.
2. An effective human L2/L3 glutamatergic synapse with separate AMPA/NMDA conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic short-term availability/depression/recovery.
3. A coupled membrane/synapse step with interval-mean conductances, a midpoint magnesium-block approximation, and atomic update of both live states.

No intrinsic action-potential generation is implemented. No 10,000-unit population, dendritic compartments, connected populations/networks, checkpointing, Rust-native concurrency, JSON loader, Python package, C ABI, C++ wrapper, or WGSL backend exists yet.

## Human spike-initiation source audit and external reproduction

Canonical research record: \`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md\`.
Reproduction protocol/results: \`experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md\`.
Reproduction runner: \`experiments/reproduce_eyal_figure7a.py\`.

### Eyal et al. 2018

- Official ModelDB archive for model 238347 retrieved; 139,316,573 bytes; SHA-256 \`12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b\`. Not stored in HumanJS.
- Canonical HOC model templates and Table S4 parameter assignments mapped for all six cells.
- Nine inserted active conductance mechanisms in soma/axon plus \`CaDynamics_E2\`; \`Ca_HVA\` is not inserted by these six spike-model templates; \`NMDA.mod\` belongs to separate synaptic workflows.
- Two-section 60 μm axon stub; dendritic branches passive; channel kinetics assumed rodent-like.
- The ten mechanisms actually inserted by the six templates compiled successfully in NEURON 9.0.2.
- Six-cell Figure 7A construction/stimulus sequence reproduced with the checked-in Python 3 script against released human current-clamp repetitions. Single model responses differ from recorded medians for several cells; report the result as an executable source/model audit, not an exact reproduction or biological validation.

### Wilbers et al. 2023

- Pure human \`na_human.mod\` and \`k_human.mod\` retrieved from the CC0 DataverseNL deposit, checksum-verified, compiled unchanged and probed in NEURON 9.0.2.
- Direct exact-singularity probes exposed non-finite \`trap0\` values in both files. The active Na+ table's 200 nodes were all finite; direct Na+ rates with table disabled were non-finite at exact singularities. K+ has no active table; exact singularities return non-finite values and two opposite-sign branch triggers produce negative inactivation time constants.
- The K+ file matches Table S2 and the first optimizer result, but the script's final printed dictionary differs and assigns an undeclared \`h12factor_k_human\`. The methods-level 14-parameter sodium count also remains unreconciled with the visible fit stages.
- No source correction was applied and the full Wilbers voltage-clamp fitting workflow was not reproduced from raw NWB traces.

## Exact runner verification

In the clean main-only cloud checkout at commit \`38caae89b44782c4631e81c5765ab47c4cde4129\`, this command completed successfully:

\`\`\`sh
python3 experiments/reproduce_eyal_figure7a.py \\
  --modeldb-root /tmp/eyal-modeldb/extracted/EyalEtAl2018 \\
  --output /tmp/eyal-modeldb/checked-in-runner-results.json
\`\`\`

Runtime: Python 3.10.12, NEURON 9.0.2, Ubuntu 22.04. It compiled the ten original active mechanisms in a temporary build directory, simulated six cells and compared 20, 10, 20, 15, 10 and 17 released repetitions respectively. The JSON result remained in external scratch space and was not committed.

## Next concrete work

Resolve the remaining Wilbers K+ fit/dictionary and parameter-count discrepancies. Then implement a clearly named, numerically stable human somatic nucleated-patch-equivalent channel model with explicit equations, units, temperature, and provenance; validate voltage-clamp responses and current-clamp waveform features. Do not present it as an anatomical AIS-resolved neuron. Human AIS immunostaining does not provide functional channel conductances/gating.

No biological validation, clinical validity, whole-brain functionality, or consciousness claim is made. A fresh local clone in the container remained unavailable, but the source of truth was cloned and verified from GitHub \`main\` in the isolated cloud VM used for the external reproduction; it was not used as an alternate project source.
