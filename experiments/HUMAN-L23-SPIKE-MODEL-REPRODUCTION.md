# Reproduction audit: Eyal et al. human L2/L3 spike models (Figure 7A)

**Date:** 2026-11-11  
**Purpose:** verify the canonical model source, its Table S4-to-code mapping, and the executable behavior of the six published soma/axon spike models against their released human current-clamp traces.  
**Status:** source retrieval, mechanism compilation, and a six-cell single-stimulus reproduction completed. This is a software/model reproduction audit, not biological validation or an independent model refit.

## 1. Canonical source and integrity

The full ModelDB archive for model 238347 was retrieved from the official endpoint:

- ModelDB record: https://modeldb.science/238347
- Archive: https://modeldb.science/download/238347
- Archive name: `238347-full.zip`
- Download size: 139,316,573 bytes
- SHA-256: `12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b`
- The archive passed `unzip -t`; it is not copied into HumanJS.

The official archive contains the six fitted HOC templates in `EyalEtAl2018/ActiveModels/`, six reconstructed morphologies in `Morphs/`, active channel mechanisms in `ActiveMechanisms/`, and the Figure 7A repeated current-clamp traces in `Figure7/data/`.

## 2. Exact HOC-to-Table-S4 mapping

The six model templates are:

| Cell label | HOC template |
|---|---|
| cell0603_03 | `cell0603_03_model_476` |
| cell0603_08 | `cell0603_08_model_602` |
| cell0603_11 | `cell0603_11_model_937` |
| cell1303_03 | `cell1303_03_model_448` |
| cell1303_05 | `cell1303_05_model_643` |
| cell1303_06 | `cell1303_06_model_263` |

Direct inspection of the canonical HOC `insertChannel()` routines resolves the mechanism list used by these six AP models. They insert the following nine conductance mechanisms in the soma and axon: `NaTg`, `Nap_Et2`, `K_Tst`, `K_Pst`, `SKv3_1`, `Ca`, `Ca_LVAst`, `SK_E2`, and `Im`. They also insert `CaDynamics_E2` for intracellular calcium state/handling.

`Ca_HVA.mod` exists in the archive, but is not inserted or assigned by these six Figure 7A spike-model templates. `NMDA.mod` is a separate synaptic mechanism used in other model workflows, not an active conductance fitted in the six Table S4 spike models. These distinctions are based on the original HOC insertion and parameter-assignment code, not a secondary mechanism-registration list.

The canonical HOC `biophys()` procedures contain the same per-cell conductance, NaTg shift/slope, calcium-dynamics, and leak-reversal values transcribed from supplementary Table S4 in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The Table S4 count is nine maximum conductances, three NaTg kinetic parameters, and two calcium-dynamics parameters per compartment (14 per compartment), plus a single shared `e_pas`: `2 × (9 + 3 + 2) + 1 = 29`.

The templates set a shared temperature of 37°C, `CM=0.488 μF/cm²`, `RM=21,406 Ω·cm²`, and `RA=281.78 Ω·cm`. Apical and basal membrane capacitance and passive leak are scaled by 1.9 beyond 60 μm. The Figure 7A driver replaces the reconstructed axon with two 30 μm stub sections, giving 60 μm total. The dendritic compartments are passive; the active conductance fit is applied to soma and the replacement axon. This is a reduced modeling choice and must not be described as a measured human AIS channel map.

The active mechanism readme attributes channel models to the Blue Brain Project mechanism library. Eyal et al. explicitly describe their gating kinetics as similar to rodent channel kinetics. Human AP recordings constrain fitted conductance and selected NaTg shift parameters; this does not convert transferred kinetic functions into direct human measurements.

## 3. Compiled and executed reproduction

**Runtime:** Ubuntu 22.04, Python 3.10.12, NEURON 9.0.2 (NEURON build date 2026-08-10), NumPy.  
**Build:** the ten mechanisms actually inserted by the six HOC templates were copied unchanged from the extracted canonical archive into a temporary build directory and compiled serially with `MAKEFLAGS=-j1 nrnivmodl mod`. The build succeeded and produced `libnrnmech.so`. The extra `Ca_HVA` and separate `NMDA` mechanisms were not part of this spike-model build because the six HOC templates do not insert them.

The six models were then constructed by following the Figure 7A driver sequence: load the cell HOC template, instantiate the corresponding Neurolucida morphology, index sections, set segmentation, replace the original axon with the two-section stub, insert channels, initialize passive properties, and apply the fitted per-cell parameters.

The stimulus and simulation settings were the published Figure 7A settings:

- `h.celsius = 37°C`
- `dt = 0.01 ms` (100 steps/ms)
- `tstop = 1500 ms`
- `v_init = −86 mV`
- Somatic current step starts at 120.33 ms and lasts 1,000 ms.
- Current amplitudes: 0.7 nA for cell0603_03, cell0603_08 and cell0603_11; 0.55 nA for cell1303_03 and cell1303_05; 0.60 nA for cell1303_06.
- Released recording traces are adjusted by subtracting the 16 mV junction potential, matching Figure7A.py.

The reproduction is performed by a Python 3 runner, `experiments/reproduce_eyal_figure7a.py`, which compiles the original mechanisms in a temporary directory and emits a JSON result. It is an independent Python 3 implementation of the original Figure 7A construction/stimulus sequence; it does not execute the original Python 2 plotting driver unchanged.

## 4. First-spike comparison

The first 0 mV crossing after 120 ms is used only as a reproducible alignment marker, not as an assertion that biological AP threshold is 0 mV. Peak is the local maximum within 2 ms of that crossing. Half-width is measured at half the excursion between the pre-stimulus median baseline and that local peak. Recorded values are medians across all released repetitions for the specified cell/current; the model values are one deterministic model run.

| Cell | Current | Repetitions | Model peak (mV) | Recorded median peak (mV) | Model crossing (ms) | Recorded median crossing (ms) | Model half-width (ms) | Recorded median half-width (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cell0603_03 | 0.70 nA | 20 | 42.34 | 43.08 | 141.44 | 141.86 | 0.73 | 1.14 |
| cell0603_08 | 0.70 nA | 10 | 44.95 | 40.19 | 136.37 | 138.11 | 0.87 | 1.03 |
| cell0603_11 | 0.70 nA | 20 | 35.18 | 39.04 | 138.48 | 140.08 | 0.78 | 1.24 |
| cell1303_03 | 0.55 nA | 15 | 41.68 | 40.43 | 150.75 | 150.49 | 0.90 | 0.85 |
| cell1303_05 | 0.55 nA | 10 | 36.20 | 36.83 | 151.30 | 159.90 | 0.80 | 1.16 |
| cell1303_06 | 0.60 nA | 17 | 47.18 | 44.42 | 148.70 | 151.62 | 0.83 | 1.06 |

The released recordings show trial-to-trial variation; some cells have wider timing ranges than others. The comparison also shows nontrivial model/data differences in several cells, especially first-spike timing and width. This audit therefore verifies that the archived model is loadable, its fitted parameter assignments map to the official Table S4, the original channel mechanisms compile, and the published stimulus sequence produces spikes. It does **not** establish an exact trace match, independent reproduction of the multi-objective optimization, a successful refit, or biological validation. The model should not be treated as a gold-standard biological ground truth simply because its source can be executed.

## 5. Wilbers human Na+/K+ mechanism runtime audit

The pure human voltage-clamp files from the CC0 DataverseNL deposit were also compiled unchanged with NEURON 9.0.2:

- `na_human.mod`, Dataverse file 318629, SHA-1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970`.
- `k_human.mod`, Dataverse file 318647, SHA-1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`.

A direct compiled-function probe at each stored `trap0` singular voltage returns a non-finite result. The mathematical limit of the main expression is `a × q`, while the active fallback omits the `a` prefactor and its branch test uses `v + th` even though the main expression's singularity is at `v = th`.

The Na+ mechanism enables a voltage lookup table from −120 to +100 mV with 199 subdivisions (200 grid nodes). A scan of all 200 compiled table nodes produced finite activation and inactivation time constants. The three Na+ gate singularities are off-grid; the nearest node to the `thi1` inactivation singularity is approximately 0.0022 mV away. With the lookup table explicitly disabled, direct Na+ evaluation at the exact singular voltages produces non-finite time constants.

The K+ mechanism's table block is commented out, so its rates are evaluated directly. Exact evaluations at its activation, inactivation and recovery singularities produce non-finite time constants. The compiled K+ runtime also returns negative inactivation time constants at two opposite-sign branch triggers (approximately −0.73 ms and −0.13 ms). This is a source/runtime numerical issue that must be preserved in provenance and isolated in any HumanJS reproduction; do not silently patch it and claim exact source reproduction.

The pure K+ mechanism source matches Table S2 and the first optimizer result. The deposited K+ fitting script's later final printed six-parameter dictionary differs, and the script assigns `h12factor_k_human` although the pure mechanism does not declare it and the corresponding `h2tau` multiplication is commented out. The paper's methods-level 14-parameter sodium count also remains unreconciled with the visible fit/assignment sequence. These are source discrepancies, not reasons to select one parameter set without evidence.

This runtime audit tests the original rate functions and lookup-grid behavior; it does not reproduce the full Wilbers voltage-clamp fitting workflow, rerun its optimizer from raw current traces, or reproduce its current-clamp hybrid AP fit.

## 6. Interpretation and gate for HumanJS

This work closes the source-download and Eyal Table S4 mapping questions and establishes an executable baseline for the six canonical human L2/L3 soma/axon AP models. It also exposes a concrete numerical concern in the pure Wilbers human Na+/K+ rate implementations.

It does **not** provide a ready-to-port, unambiguous human AIS model:

- Eyal uses a reduced soma + 60 μm axon stub, with passive dendrites and rodent-like kinetic transfers.
- Wilbers pure files represent human nucleated somatic-patch voltage-clamp data, not the AIS. The table/fit-script discrepancies and trap0 edge cases are still present.
- Human AIS NaV1.2/NaV1.6 staining supplies subtype localization, not conductance density or gating kinetics.
- The public per-cell Wilbers workbooks are summary fit tables, not raw current traces; the original NWB traces were not present in the 65-file version-3.0 listing inspected.

Accordingly, no intrinsic spike-generation code is added by this experiment. The next viable implementation target is a clearly named human somatic nucleated-patch equivalent, but only after defining a corrected, independently specified numerical interpretation of the human gate equations and validating it against published voltage-clamp targets. That implementation must be labeled as a HumanJS model derived from human somatic recordings, not an exact reproduction of the problematic NEURON source and not an anatomical soma/AIS neuron. An AIS-resolved model remains a separate, evidence-gated milestone.

## 7. Reproduction instructions

1. Download the official ModelDB model archive (model 238347) from https://modeldb.science/download/238347 and verify its integrity against the recorded SHA-256 if the same archive version is obtained.
2. Extract it so the path supplied to the runner is the `EyalEtAl2018` directory containing `ActiveMechanisms/`, `ActiveModels/`, `Morphs/` and `Figure7/data/`.
3. Install Python 3.10+, NEURON 9.0.2, NumPy, `nrnivmodl`, and a C++ compiler.
4. Run:

```sh
python3 experiments/reproduce_eyal_figure7a.py \
  --modeldb-root /path/to/EyalEtAl2018
```

The default output is JSON on stdout. Supply `--output results.json` to save a result file outside the tracked tree. The runner builds the ten required original `.mod` files in a temporary directory and removes that build directory when it exits. It does not copy the ModelDB archive or mechanism source into HumanJS.
