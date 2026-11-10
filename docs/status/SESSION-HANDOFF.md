# HumanJS — current session handoff

**Updated:** 2026-11-10  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Verified main HEAD before this evidence/documentation increment:** `574ffbd7c2ba403405bc63a6a2c0853f0e8920a1`.

## Verified repository state

- Public repository; default branch `main`.
- Live branch listing contains exactly `main`.
- No open issues or pull requests.
- Latest completed full workflow on the documented head: run `42841773499`, success: https://github.com/codexclai/HumanJS/actions/runs/42841773499.
- Previous integrated CPU code commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304` passed full CI in run `42829179222`.

## Implemented CPU mechanisms

The Rust workspace `crates/humanjs-core` contains:
1. A validated single-compartment passive RC membrane, analytically integrated for constant injected current.
2. An effective glutamatergic synapse with separate AMPA/NMDA biexponential conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic short-term availability/depression/recovery.
3. Coupled membrane/synapse stepping using interval-mean receptor conductances and midpoint NMDA magnesium unblock. Both live states update atomically only after a successful step.

The latest full workflow passed formatting, Clippy, tests (10 unit + 9 integration), and repository policy. The evidence/documentation commit did not change Rust code; the existing tests remain unchanged. No local clone or local Rust run exists; the container could not resolve GitHub.

## Current spike-initiation evidence review — no code added

`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` is the canonical evidence record.

- Eyal et al. (2018) provide six human L2/L3 pyramidal soma/axon models fitted to human spike recordings, but the conductance distributions are fitted estimates and their channel kinetics were assumed to resemble rodents. Human dendritic active conductances were not constrained.
- Wilbers et al. (2023) directly measured somatic Na+/K+ currents in human nucleated patches. These measurements exclude the AIS. The single-compartment HH model and fitted AP conductances must not be confused with direct patch conductance densities.
- Tian et al. (2014) provide human immunostaining evidence for proximal NaV1.2 and more distal NaV1.6 distribution at pyramidal-cell AISs. This is spatial molecular evidence, not functional conductance/gating measurement.

### Additional original Wilbers source inspection — direct mechanism audit completed, reproduction pending

The original Wilbers supplement and author-deposited CC0-1.0 DataverseNL dataset were inspected. Dataset DOI: 10.34894/L5J0SD, version 3.0, released 2022-12-13.

The pure voltage-clamp mechanisms were retrieved and decoded:
- na_human.mod, file 318629, 3,602 bytes, SHA1 b199d70c3d0e7a2e991fd8d26c54b1318e3c0970.
- k_human.mod, file 318647, 4,220 bytes, SHA1 d299b3430ecda7a94f6d1c37ac76b2878052c7d5.

Both original files explicitly set Rb equal to Ra. The Na+ file uses a 25°C reference and Q10=2.3; the K+ file uses a 34°C reference and Q10=2.3. The Na+ conductance expression itself is multiplied by the Q10 adjustment, whereas the K+ conductance expression is not. The current-clamp hybrid copies (files 318563 and 318566) are distinct variants with human/mouse channel-fraction scaling.

The K+ parameter ambiguity is partly resolved: the deposited pure K+ mechanism file matches Table S2 and the first optimizer result. The fit script's later final dictionary still differs, and it assigns h12factor_k_human although that symbol is not declared in the inspected pure K+ mechanism. The paper's 14-parameter count remains unreconciled with 13 Na+ and 11 K+ visible fit/assignment values after Rb=Ra is treated as one parameter.

Both original files implement a trap0 function whose branch condition uses v+th even though the main rate expression is singular at v=th. The active fallback omits the rate prefactor a; the mathematical limit of the main expression is a*q. This needs testing under the exact NEURON lookup-table behavior before porting or correcting it.

The author per-cell summary workbooks were parsed directly:
- data_fig3.xlsx (318666): 19 human Na+ activation rows; 18 inactivation values reproduce the paper's summary after excluding one row with fit quality 0.8600. The workbook does not state that exclusion rule explicitly.
- data_fig4.xlsx (318667): 13 human K+ activation rows and 11 K+ inactivation rows, consistent with the paper's reported counts.
These tables are per-cell fit summaries, not raw current traces. The original NWB trace files were not present in the 65-file Dataverse version-3.0 listing inspected.

The source files have been inspected but not compiled/reproduced: NEURON/nrnivmodl was unavailable in the execution environment. No HumanJS spike/AP code has been added. A somatic nucleated-patch equivalent must remain distinct from anatomical soma/AIS modeling, and no AIS conductance can be inferred from immunostaining.

## Next concrete work

Reproduce the original pure human Na+/K+ channel mechanisms in compiled NEURON or an equivalent verified runtime, including a controlled test of trap0 behavior on the published lookup grid. Reconcile the 14-parameter methods count, the K+ script's final dictionary, and its h12factor assignment. Compare mechanism output against published/per-cell human voltage-clamp summaries and current-clamp AP targets; the summary workbooks alone are not raw traces. Then separately reconcile Eyal Table S4 against the canonical ModelDB source before deciding whether any somatic-patch-equivalent implementation is sufficiently constrained.

Keep the Eyal soma/axon model separate from Wilbers' nucleated-somatic-patch model; its gating kinetics were assumed rodent-like. No spike implementation, threshold-only generator, generic rodent HH set, or AIS conductance derived from immunostaining is acceptable.

Still not implemented: an intrinsic AP generator, configurable 10,000-unit spiking population, dendritic morphology/multicompartment integration, connected populations/networks, long-term plasticity/learning, checkpoints/save-restore, Rust-native concurrency, JSON model loading, Python, C ABI, C++ wrapper, and integrated WGSL GPU execution.
