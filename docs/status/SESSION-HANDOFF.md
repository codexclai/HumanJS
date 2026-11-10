# HumanJS — current session handoff

**Updated:** 2026-11-10  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Verified main HEAD before this evidence/documentation increment:** `bf8b44080c1e5908da15cecef177d4896ad03bf3`.

## Verified repository state

- Public repository; default branch `main`.
- Live branch listing contains exactly `main`.
- No open issues or pull requests.
- Latest completed full workflow on the documented head: run `42830050128`, success: https://github.com/codexclai/HumanJS/actions/runs/42830050128.
- Previous integrated CPU code commit `d561df97ae0bbd1012d8cd3bb3b0e466e4f78304` passed full CI in run `42829179222`.

## Implemented CPU mechanisms

The Rust workspace `crates/humanjs-core` contains:
1. A validated single-compartment passive RC membrane, analytically integrated for constant injected current.
2. An effective glutamatergic synapse with separate AMPA/NMDA biexponential conductance kernels, voltage-dependent NMDA magnesium unblock, and deterministic short-term availability/depression/recovery.
3. Coupled membrane/synapse stepping using interval-mean receptor conductances and midpoint NMDA magnesium unblock. Both live states update atomically only after a successful step.

The latest code verification passed formatting, Clippy, tests (10 unit + 9 integration), and repository policy. No local clone or local Rust run exists; the container could not resolve GitHub.

## Current spike-initiation evidence review — no code added

`research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md` is the canonical evidence record.

- Eyal et al. (2018) provide six human L2/L3 pyramidal soma/axon models fitted to human spike recordings, but the conductance distributions are fitted estimates and their channel kinetics were assumed to resemble rodents. Human dendritic active conductances were not constrained.
- Wilbers et al. (2023) directly measured somatic Na+/K+ currents in human nucleated patches. These measurements exclude the AIS. The single-compartment HH model and fitted AP conductances must not be confused with direct patch conductance densities.
- Tian et al. (2014) provide human immunostaining evidence for proximal NaV1.2 and more distal NaV1.6 distribution at pyramidal-cell AISs. This is spatial molecular evidence, not functional conductance/gating measurement.

### Additional original Wilbers source inspection

The original Wilbers supplement and author-deposited CC0-1.0 DataverseNL dataset were inspected. The dataset is DOI `10.34894/L5J0SD`, version 3.0, released 2022-12-13.

The deposited scripts include `fit_na_hh_cma_human.py` (file 326238), `fit_k_hh_cma_human.py` (326237), `channel_tools.py` (326242), and `cc_tools.py` (318557). The scripts resolve the repeated Table S2 inactivation steady-state label: the intended source variable is `th_inact_inf`. They show Na+ channel voltage-clamp fitting at 25°C and K+ fitting at 34°C, with distinct protocol timing and test-voltage ranges.

Open mapping issues:
- The actual deposited `na_human.mod` (file 318629) and `k_human.mod` (318647) are listed and their file metadata/checksums verified, but the available extractor rejects their `audio/mod` MIME type; their gate-rate source text has not yet been inspected.
- The deposited K+ script's first inactivation optimizer values match Table S2, but its final printed fit dictionary contains different values. The value set used in the published simulation has not yet been reconciled.
- The article states 14 free parameters for each channel model, but the deposited scripts visibly list 13 Na+ fit/assigned parameter names and 11 explicit K+ fit names before additional fixed quantities. The exact parameter bookkeeping remains open.
- Table S2 lacks a separately tabulated `Rb`; the fit script fits `Ra` but not `Rb`. The actual fixed `Rb` value/use must be determined from the original `.mod` mechanism.
- No HumanJS AP/spike code has been added. A somatic nucleated-patch equivalent is a possible first AP-capable model, but must not claim an anatomical soma/AIS, dendritic propagation, or full-neuron behavior. An AIS-resolved model remains a separate evidence-gated task.

## Next concrete work

Retrieve/inspect the original Dataverse `.mod` files by a route capable of reading their `audio/mod` payload, or obtain an author-provided text export. Reconcile the mechanism equations, (Rb), Q10/reference temperature, K+ parameter discrepancy, and parameter counts against the paper and Table S2. Only after that should the project decide whether a somatic-patch-equivalent model can be implemented and numerically fitted to the published human voltage-clamp and AP targets.

Keep the Eyal model as a separate soma/axon evidence source; do not silently conflate its rodent-derived gating kinetics with the human somatic patch model. No spike implementation, threshold-only generator, generic rodent HH set, or AIS conductance derived from immunostaining is acceptable.

Still not implemented: an intrinsic AP generator, configurable 10,000-unit spiking population, dendritic morphology/multicompartment integration, connected populations/networks, long-term plasticity/learning, checkpoints/save-restore, Rust-native concurrency, JSON model loading, Python, C ABI, C++ wrapper, and integrated WGSL GPU execution.
