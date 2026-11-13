# HumanJS — current session handoff

**Updated:** 2026-11-13
**Canonical repository:** codexclai/HumanJS, branch main only.
**Latest live implementation HEAD before this documentation handoff refresh:** 5d5e180bc5068f647edc040de39481801be52a0e (111-entry non-truncated tree, main only, no open issues or PRs). Workflow [43469283136](https://github.com/codexclai/HumanJS/actions/runs/43469283136) passed on that exact pushed experiment commit, including the new three-adjacent-voltage residual profile and expected-summary validator. All code, data and workflow changes were pushed directly to main; its live remote ref was checked against the commit.
**Next session:** refresh repository metadata, read live docs/BOOT.md, then inspect the current main tree, latest workflow, issues/PRs and branch refs before relying on this handoff.

## Verified repository state at handoff

- Public repository; default branch main; implementation HEAD at this handoff snapshot: 5d5e180bc5068f647edc040de39481801be52a0e; complete 111-entry recursive tree, exactly one branch (main), zero open issues and zero open pull requests.
- Workflow [43469283136](https://github.com/codexclai/HumanJS/actions/runs/43469283136) passed on exact implementation HEAD 5d5e180bc5068f647edc040de39481801be52a0e: rustfmt, Clippy, Rust workspace tests (41 unit, 3 synapse integration, 6 passive membrane integration), syntax for 28 experiment scripts, 43 Python tests, existing Wilbers data validators, five original Na/K NEURON source replays and their validators, K_IV multi-start/profile/residual checks, the new -75/-70/-65 mV signed residual analysis, comparison against its committed result CSV, and repository policy.

- The direct NEURON runner verifies and executes the pure human sodium NMODL mechanism plus the original Dataverse channel_tools.py source helpers under the source fitting caller's cell configuration. Main Na_IV passes current-density selection at 19/19 voltages and joint-fit R² at 17/19; Na_IV_inact produces 30 conditioning points and Boltzmann Vhalf/slope −68.251977/8.472251 mV; Na_recovery records 156 paired-pulse traces and 13/13 finite apparent recovery taus.
- The raw result records are research/HUMAN-L23-WILBERS-NA-IV-NEURON-REPLAY.csv, research/HUMAN-L23-WILBERS-NA-IV-INACT-NEURON-REPLAY.csv, and research/HUMAN-L23-WILBERS-NA-RECOVERY-NEURON-REPLAY.csv. Validators compare CI reruns with these per-protocol records. Actual NEURON timer masks can include a boundary sample because the helper compares recorded floating-point timestamps strictly; first/last times and counts are preserved rather than imposing ideal counts.
- The separate ideal-command Na_IV equation replay remains an approximation; its apparent tau outputs are not substituted for finite-feedback NEURON results. Neither source execution uses raw experimental NWB voltage-clamp records. No raw-trace refit or biological validation is claimed.
- The exploratory Na/K single-compartment spike model remains scientifically unaccepted and not biologically validated.

## Current HumanJS implementation

The Rust core `crates/humanjs-core` contains three mechanisms:

1. A validated single-compartment passive RC membrane, analytically integrated for piecewise-constant injected current.
2. An effective human L2/L3 glutamatergic synapse with separate AMPA/NMDA conductance kernels, voltage-dependent NMDA magnesium unblock, deterministic short-term availability/depression/recovery, and transactional coupling to the passive membrane.
3. An **exploratory, not scientifically accepted** human L2/L3 single-compartment Na+/K+ conductance model in `crates/humanjs-core/src/ion_channels.rs`. It integrates voltage and five gates with fixed-step RK4 and can generate one spike for its software test pulse.

The third mechanism was committed before the scientific evidence gate in ADR-014 was closed. It must be described accurately as existing code, but it does not satisfy that gate and must not be called biologically validated. It is one lumped electrical compartment, not an anatomical soma/AIS neuron, intact pyramidal neuron, axon, dendritic tree, or propagating neuron.

### Exploratory model parameter choices and unresolved issues

- Na+ gates use the pure Wilbers human `na_human.mod` values.
- K+ gates use the pure `k_human.mod` values that match Table S2 and the first optimizer result. The fitting script explicitly applies this first result; its trailing alternate dictionary is a bare literal and is never applied.
- The K+ script assigns `h12factor_k_human=10.5`, but all three inspected pure/hybrid K+ NMODL variants contain only a commented-out `h2tau = h1tau * h12factor` line; the helper does not read the Python attribute.
- The article's 14-parameter model description includes two inactivation steady-state values and independent `Rb`; the deposited scripts fix the former from experiment and constrain `Rb = Ra`, leaving 11 optimizer variables.
- Current-clamp fitted conductance densities (114.48 pS/μm² Na+, 29.05 pS/μm² K+) were fitted against cross-species mean AP features; they are not direct human channel-density measurements.
- The 10 μm cylindrical geometry, 34°C, −10 mV channel shift, +15 mV reversal offsets, 1 μF/cm² capacitance, Rm=10,000 Ω·cm² leak, and 20 μs maximum step follow the deposited current-clamp helper.
- The Rust `trap0` uses a stable analytic limit at the mathematical singularity. This is not an exact reproduction of the source's branch behavior. The pure NMODL files declare its prefactor as `/ms`, but the voltage-valued numerator requires `mV⁻¹·ms⁻¹`; HumanJS keeps numeric values and uses the equation-consistent internal unit pending verification against the original NEURON unit contract.

Current code tests cover the analytic `trap0` limit/continuity, half-voltage steady states, potassium fast/slow inactivation branch constants and conductance fractions, positive finite time constants over a bounded voltage scan, Q10 scaling, K+ gate-clamp replay, all 50 gate recovery voltage/delay conditions, source `K_IV` current-activation fitting at seven voltages, source post-peak biexponential inactivation fitting at six voltages, and the full 50-condition `K_recovery` current protocol with biexponential current-fit, plus one-spike waveform scale, approximate step-size convergence, reset, and transactional failure. These are software tests, not biological validation.

## Human spike-initiation source audit and external reproduction

Canonical evidence: `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.  
Eyal reproduction: `experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md`.  
Runner: `experiments/reproduce_eyal_figure7a.py`.

### Eyal et al. (2018)

- Official ModelDB archive for model 238347 retrieved; 139,316,573 bytes; SHA-256 `12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b`. Not stored in HumanJS.
- Canonical HOC templates and Table S4 parameter assignments mapped for all six cells.
- Nine inserted active conductance mechanisms in soma/axon plus `CaDynamics_E2`; `Ca_HVA` is not inserted by these six templates; `NMDA.mod` belongs to separate synaptic workflows.
- Two-section 60 μm axon stub; dendritic branches passive; channel kinetics assumed rodent-like.
- Ten mechanisms actually inserted by the six templates compiled with NEURON 9.0.2.
- Six-cell Figure 7A construction/stimulus sequence reproduced with the checked-in Python 3 script against released human current-clamp repetitions. Model/data timing, width, and peak differences remain. This is not an independent refit, exact trace match, HumanJS implementation, or biological validation.

### Wilbers et al. (2023)

- Pure human `na_human.mod` and `k_human.mod` retrieved from the CC0 DataverseNL deposit, checksum-verified, compiled unchanged, and probed in NEURON 9.0.2.
- Exact-singularity probes exposed non-finite `trap0` values. The active Na+ table's 200 nodes were finite; direct Na+ rates with table disabled were non-finite at exact singularities. K+ has no active table; exact singularities return non-finite values and two opposite-sign branch triggers produce negative inactivation time constants.
- The K+ source matches the parameter values actually applied by the script; its alternate dictionary is a bare literal and is not applied. The 14-versus-11 parameter count is explained by fixed inactivation steady states and `Rb = Ra`. The fit script's `h12factor_k_human` assignment is not declared in the pure mechanism or read by `channel_tools.py`. The source's printed Table S2 rate-prefactor unit (`ms^-1`) is dimensionally incomplete for the voltage-valued `trap0` numerator; the code interprets the coefficient as `mV^-1 ms^-1`.
- Full Wilbers voltage-clamp fitting was not reproduced from raw NWB traces; public workbooks are summary fits and original NWB traces were not present in the 65-file Dataverse listing examined.


### Wilbers K+ voltage-clamp protocol and fitting objective audit

- Directly inspected Dataverse files `fit_k_hh_cma_human.py` (326237), `channel_tools.py` (326242), `channel_kinetics.py` (326241), and pure `k_human.mod` (318647), from dataset DOI 10.34894/L5J0SD version 3.0.
- Activation/inactivation model clamp: −140 mV for 20 ms, each test voltage for 500 ms, +60 mV for 50 ms, then −140 mV for 100 ms. `K_IV` scans −110 to +55 mV in 5-mV increments; `K_IV_ss` scans −110 to +50 mV in 10-mV increments.
- Recovery model clamp: −120 mV for 2 ms, +40 mV for 5,000 ms, recovery at −90/−85/−80/−75/−70 mV for 4, 144, 484, 1,024, 1,764, 2,704, 3,844, 5,184, 6,724, and 8,464 ms, then +40 mV for 5 ms. Temperature is 34°C. Deactivation protocol exists in the helper but is not used by the optimizer.
- The human optimizer fits six inactivation/recovery parameters, then activation kinetics, then activation steady state. Its fast-recovery target is hard-coded to 236.824345 ms, commented as the mean of human and mouse values. Slow inactivation (450 ms) and slow recovery (2,789.7929 ms) are fixed mechanism settings, not fitted variables. Reported inactivation/recovery component scores are fast 0.0721, slow 2.4386, and fast recovery 0.00235; the slow component has 0.05 relative weight.
- The public 65-file Dataverse inventory lacks the `Experimental means/k_tau_*.csv` files read by the fitting helper, the `data_fig5.xlsx` referenced by the K plotting script, and raw K voltage-clamp NWB current traces. `K_data_fig2.xlsx` is AP-clamp repeated-waveform amplitude data, not the missing voltage-step kinetic dataset.
- Rust unit tests in `crates/humanjs-core/src/ion_channels.rs` replay activation, inactivation, and recovery command sequences with exact first-order gate updates. The recovery regression now covers all five deposited recovery voltages × all ten delays (50 combinations) and checks independent model-side reference conductance values plus monotonic recovery at each voltage. A full `K_IV_ss` series uses the deposited −110 to +50 mV, 10-mV grid. Transparent half-range interpolation gives −3.25 mV activation midpoint, −51.48 mV inactivation midpoint, and 0.936 availability at −80 mV; all fall within the published human group mean ± SD. This is a coarse summary comparison and software regression, not the source nonlinear fit or raw-trace validation.
- Workflow `43016424733` passed formatting, Clippy, Rust workspace tests, Python syntax validation, and repository policy on code commit `660dee7287376720d37d96dac939941fe26df7d6`. The local clone attempt still fails because GitHub DNS cannot be resolved in this environment; no local Rust test run is claimed.


### NEURON 9.0.2 unit-check result

- Original `k_human.mod` and `na_human.mod` compile unchanged with `nrnivmodl`, but the compiler warns that GLOBAL `tadj` assignment is not thread-safe.
- Original `modlunit` runs stop at the untyped `trates(v+vshift)` call (K line 82; Na line 80). Temporary diagnostic copies with typed signatures expose the declared `/ms` versus equation-required `mV^-1 ms^-1` mismatch, the fallback's missing prefactor/wrong dimensions, the wrong-sign branch predicate, the dimensionful Q10 exponent, and missing mV units on activation midpoint/slope parameters.
- Temporary typed K/Na copies pass `modlunit` 9.0.2 only after those unit corrections and replacing the active fallback with the source's commented-out `a*q` limit. No Dataverse source was modified.
- The original NMODL is therefore not a unit-checked reference implementation. HumanJS's Rust rate units and analytic singularity handling are equation-consistent corrections, not exact reproduction of the source branch.


### Supplementary Figure S5: visually verified legend, marker digitization, and source-path audit

- Retrieved the official 13-page supplement from the PMC AWS Article Dataset object: https://pmc-oa-opendata.s3.amazonaws.com/PMC10569700.1/sciadv.ade3300_sm.pdf. Size 1,468,232 bytes; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d`.
- Rendered Figure S5 page 7 and visually verified the legend: red model line/human open-circle experimental means; blue model line/mouse cross experimental means. The caption duplicates “(I)” for fast inactivation; the actual plotted panel is labelled J.
- Recorded 50 experimental marker values across panels I, J, K, M, and N: 46 manually digitized markers in I/J/K and four exact group means transcribed from `channel_tools.K_IV` in M/N. Seven research CSVs preserve source hash, raster coordinates, axis calibration, marker identity, and uncertainty. These are group means; plot-reading uncertainty is not biological SD.
- Panel I activation has seven voltages per species from −10 to +50 mV. The Rust regression replays the deposited 34°C, 0.1-ms current protocol and matches independent SciPy current-fit references within 0.01 ms. This apparent current-rise time constant is not direct K-gate `mtau`; the voltage-clamp helper uses zero shift, not the separate −10-mV current-clamp shift.
- Panel J fast inactivation has six voltages per species from 0 to +50 mV. Panel K slow inactivation has ten voltages per species from −30 to +60 mV. The Rust implementation reconstructs the intended post-peak fit with a fixed 450-ms slow component for human and mouse model parameters. Human reconstructed fast-component values are ≈52.28, 41.56, 33.46, 27.26, 22.47, and 18.75 ms; mouse values are ≈53.43, 42.00, 33.68, 27.40, 22.57, and 18.82 ms. These are model-side current-fit reconstructions checked against independent SciPy references, not microscopic gate taus.
- **Corrected K_IV source-helper audit:** the exact Dataverse `channel_tools.py` (file 326242; SHA-1 `615595a270c6170987757cd35743f5d5b5b2af0e`) defines `get_tau_inact_double_fixedtau2` with four free parameters and four `p0` values; `tau2` is fixed at 450 ms. The earlier five-versus-four arity-error statement was incorrect and is retracted. The helper has since executed in the NEURON K_IV source replay. The separate final Figure S5 plot-generation script is still absent, so exact red/blue model-line provenance is not fully recovered.
- For reference only, reconstructed human panel-J current-fit values have ≈5.91-ms RMSE against digitized human group means. The fixed 450-ms panel-K component has ≈149-ms human and ≈166-ms mouse RMSE against digitized group means. These are model-vs-marker residual summaries, not pixel-level model-line comparisons, biological SD, or statistical tests.
- Panel M fast recovery and panel N slow recovery at −80 mV have exact `channel_tools.K_IV` group means. Human/mouse fast means are 228.5275/245.1212 ms; slow means are 1999.7295/3579.8564 ms. Their arithmetic means, 236.8243 and 2789.7929 ms, are pooled model targets/constants. The slow value is ≈39.5% above the human-only mean; do not treat pooled constants as human-specific parameters.
- Rust replays the `K_recovery` current protocol for both human and mouse model parameters: five recovery voltages × ten delays (50 test-pulse peaks per species), followed by a constrained two-component current fit. The mouse model uses pure `k_mouse.mod` defaults (file 318560), including pre-fit activation `Ra=0.0167/ms`. Mouse fast/slow references (ms) are −90 mV: 115.59/2790.86; −85 mV: 155.36/2793.14; −80 mV: 234.45/2799.27; −75 mV: 374.39/2801.18; −70 mV: 329.90/2799.72. Both species' model references are preserved in `HUMAN-L23-WILBERS-FIG-S5-MN-RECOVERY-MODEL-REPLAY.csv` and CI-checked. These are current-fit components, not direct readings of gate taus.
- Model-curve provenance: both available `fit_k_hh_cma_*` scripts call `K_IV(cell)` before activation optimization. Human MOD defaults match the final fit; mouse default activation `Ra=0.0167/ms` differs from the later fitted `0.020746083599133762/ms`. Six unmarked blue model-line samples give pixel RMSE 5.35 against the pre-fit default current-fit curve versus 36.06 against the post-fit curve. This strongly supports that the blue mouse activation line is pre-fit, but no separate final plot generator is deposited.
- Exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. No raw-trace reproduction, independent refit, or biological validation is claimed.
- `experiments/validate_wilbers_fig_s5_digitization.py` checks the seven source/replay CSVs, PDF hash, marker identities, axis calibration, model references, and J/K reconstruction residuals. CI also runs the current-clamp grid validator.
- Added Rust regressions for the human/mouse K+ rising-current activation fits, the human/mouse fixed-450-ms post-peak current-fit reconstructions, and both species' full 50-condition recovery-current protocols. The paired mouse parameters are copied from the pure `k_mouse.mod`, not guessed from the plotted curves.
- Reconciled `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`, `experiments/validate_wilbers_fig_s5_digitization.py`, `docs/BOOT.md`, and `docs/status/STATUS.md` to distinguish model-equation reconstruction from exact source plotting reproduction.
- Existing architecture/decision/roadmap records continue to classify the single-compartment spike mechanism as exploratory and unaccepted; no biological validity claim is made.
- This handoff is the final documentation file to update after this commit.

### 2026-11-12 — Dataverse manifest and ModelDB provenance rechecked

- The version-specific live Dataverse API reports one released v3.0 dataset version (2022-12-13; CC0-1.0) with `totalCount=65`. The complete 65-filename metadata export is independently mirrored in `Dans-labs/odissei-portal-exp` at commit `ac75eb2a48cc0bf876ec451ed82d68c101326540` (metadata only).
- Neither source inventory contains the named `Experimental means/k_tau_*.csv` input files, `data_fig5.xlsx`, `.nwb` raw recordings, or a separate final Figure S5 plotting/export script. The exact source helper arity defect and the transparent-versus-exact J/K curve distinction remain as documented in the research record.
- The bioRxiv v2 ModelDB/GitHub URLs are unfinished placeholders. Final-paper ModelDB 8210 resolves to the Mainen et al. (1995) neocortical spike-initiation model, not the Wilbers authors' own data/plotting source. The final paper's availability statement points to Dataverse.
- This resolves the public inventory and citation identity; it does not restore the missing per-cell K measurements, raw voltage-clamp traces, or exact plotting script. No runtime or parameter code was changed; the Rust spike mechanism remains exploratory and unaccepted.
- Research updates were committed as `2e0b0cc3b83aa43ec4a331355d5bae2bf1b5a108` and `2c47917b407052c4cbe768ddda22ea08406c5462`; status as `a54a71f440004d251325a54cb4687b909835322a`; BOOT as `8a31e626f5f7c70892dae93acee94b634e0f979e`. The research/status/BOOT commits each passed the repository workflow on their exact commit (runs `43127747149`, `43128024657`, `43128130076`, and `43128214721`, respectively).

## Next concrete work

1. Keep the author-default NEURON run as the comparison baseline. Do not retune channel densities or claim the diagnostic Crank–Nicolson runs are the authors' reported configuration; the large trace residual is now mainly explained by the source's default first-order voltage solver at 20 µs.
2. Keep the biological evidence gaps explicit: human-only per-cell K activation/inactivation/recovery data, raw voltage-clamp recordings and acquisition metadata, and the exact Figure S5 fitting/plotting state remain absent from the inspected Dataverse v3.0 inventory. Continue only with independently accessible public sources; do not contact authors or researchers.
3. Keep the pooled 236.824345-ms/2789.7929-ms recovery constants, cross-species AP fitting targets, non-measured fitted conductance densities, source unit/`trap0` defects at other voltages, and single-compartment geometry as explicit acceptance blockers. Raster estimates must not substitute for raw recordings or human-only measurements.
4. Reassess the exploratory single-compartment model only after the missing kinetics, fit objective, preparation equivalence and relevant human validation evidence are independently resolved. Preserve the present software-level source replay as a numerical regression, not a biological validation claim.
5. The next bounded numerical step is to compare the prescribed-path CN midpoint/left-gate current counterfactual with the fully evolved source/HumanJS current paths across matched timestep refinement and Na TABLE settings. Keep the author's default dynamic source run as the baseline, do not alter fitted channel parameters, and do not infer biological superiority.

No biological validation, clinical validity, whole-brain functionality, or consciousness claim is made. Save/restore, Rust-native concurrency, the configurable 10,000-unit default, JSON model loading, Python, C/C++, and WGSL remain unimplemented.

### Current-clamp conductance-grid follow-up (2026-11-11)

- Recovered the complete deposited fit_gbar_na_k.py and currentclamp.py source scripts through the Dataverse access API (dataset DOI 10.34894/L5J0SD, v3.0; files 318556 and 318553).
- fit_gbar_na_k.py evaluates a 20×20 grid of independent human Na/K kinetic ratios (20 values each from 0 to 1), calling the cross-species-midpoint fit_densities optimizer at all 400 combinations and writing gbar_na.csv / gbar_k.csv. Rows are reversed in the exported matrices for plotting.
- currentclamp.py separately fits all-human, all-mouse and 0.5/0.5 kinetic mixtures, then invokes the fitted-density interpolation path for 20×20 AP upstroke/downstroke heatmaps and repeated-AP sweeps up to 200 APs.
- Its initial values 96.01446023 and 48.84943554 pS/µm² are optimizer starting values, not fitted outputs. The deposited interpolation CSVs have since been retrieved and checksum-verified.
- The all-human kinetic grid endpoint has been mapped exactly to HumanJS's 114.48/29.05 pS/μm² values after rounding. Do not misstate this as a human-only AP fit: its targets are 50:50 human/mouse medians.
- Next: review the provisional single-compartment mechanism's scientific acceptance gate and determine which additional source evidence or mechanistic corrections are required before promotion. Do not change fitted conductances solely because provenance is now resolved.

### Current-clamp source completeness finding (2026-11-11) — superseded

The 2026-11-11 missing-helper conclusion was based on an incomplete extraction. The complete checksum-verified `cc_tools.py` defines `get_outcomes_full` and `get_outcomes`; all three calibration CSVs are now retrieved and their exact all-human grid endpoint is mapped to the HumanJS preset. See the 2026-11-12 resolved audit below.


### 2026-11-12 current-clamp inventory correction

- Fresh live DataverseNL API query for DOI 10.34894/L5J0SD v3.0 returned the complete 65-file inventory.
- The unrestricted current-clamp files are present: `AP1comparison.csv` file 318555 (846 bytes), `gbar_na.csv` file 318551 (8,224 bytes), and `gbar_k.csv` file 318552 (8,037 bytes).
- The CSV contents have since been retrieved through the signed object-store redirect and verified against Dataverse metadata; see the subsequent resolution entry.
- The current-clamp directory contains only three Python source files in the inventory: `cc_tools.py`, `currentclamp.py`, and `fit_gbar_na_k.py`. No separately named extractor module is listed because `get_outcomes_full` is defined at the end of `cc_tools.py`; the earlier extraction omitted that part of the file.
- The all-human grid endpoint is now traced to the 114.48/29.05 pS/µm² preset; the spike model remains exploratory pending its broader scientific acceptance gate.
- This inventory note is superseded by the fully retrieved and checksum-verified source audit below.


### 2026-11-12 — current-clamp calibration source fully recovered

- Corrected the earlier incomplete extraction finding: complete Dataverse `cc_tools.py` (file 318557; 10,448 bytes; SHA-1 `f64162577fa5dd86892b46570d597e58e083a02b`) defines `get_outcomes_full` and `get_outcomes`. The previous “missing helper” conclusion was wrong.
- Retrieved `AP1comparison.csv`, `gbar_na.csv`, and `gbar_k.csv` via Dataverse's signed SURF object-store redirect. Their sizes and SHA-1 hashes match Dataverse metadata. Preserved the three CC0 source tables verbatim in `research/WILBERS-CURRENT-CLAMP-*.csv`.
- Parsed the exact AP feature extractor and Powell objective. The three targets are absolute AP peak voltage, mean rising 30–70% dV/dt, and mean falling 70–30% dV/dt. Targets are 50:50 human/mouse median means; Powell starts [95,65], bounds [20,150], and applies a ×4 penalty unless exactly one AP is detected.
- The all-human kinetic (Na ratio=1, K ratio=1) top-right grid cell is Na 114.47654963753565 and K 29.045736151752504 pS/μm², which rounds exactly to the HumanJS preset 114.48/29.05. Preset provenance is now resolved to the all-human-kinetics endpoint; it is not a human-only AP fit.
- Added `experiments/validate_wilbers_current_clamp_grid.py` and a repository-policy CI step. It validates upstream SHA-1 hashes, AP1 target medians, grid axes/orientation, bounds, and all-human/all-mouse endpoints.
- Original NEURON/SciPy optimizer not rerun: NEURON, SciPy, and NumPy are unavailable in the execution environment. No biological validation is claimed.
- Next: review the existing provisional spike mechanism against this now-resolved source provenance and prioritize a defensible acceptance gate (or explicitly defer its status); do not retune the conductance values based solely on this provenance correction.


- Additional NMODL audit verified complementary species mixing: human Na/K current contributions scale with the human ratio, mouse contributions with (1-ratio), using shared fitted total conductance. Thus the (1,1) grid endpoint is truly all-human kinetics. Na Q10 scales conductance and rates; K Q10 scales rates only, matching Rust.
- The source CSV validator now checks Dataverse SHA-1 plus retrieved-byte SHA-256 and verifies that the Rust preset literals match the rounded all-human endpoint.
- Latest verified workflow: run `43124314513` passed on exact HEAD `c73a90270cc92979add481b00856ea2848eea98c`; formatting, Clippy, Rust workspace tests, Python syntax, both research validators, and repository policy all succeeded.


### 2026-11-12 — historical public contact-route lookup retired

A public publisher-page lookup established that a corresponding-author contact route existed and that the article's data statement points to Dataverse DOI 10.34894/L5J0SD. The project owner directed that no authors or researchers be contacted. No message was sent, and outreach is not a planned action. The missing per-cell K kinetic tables, raw K voltage-clamp recordings and exact Figure S5 plotting state remain unresolved in the inspected public inventory.


### 2026-11-12 — Figure S5 model-line raster digitization completed

- Retrieved the official supplementary PDF from the public PMC open-access object store; SHA-256 matches dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d.
- Rendered page 7 at 300 dpi and digitized 23 model-line center samples across panels J/K/M/N into research/HUMAN-L23-WILBERS-FIG-S5-MODEL-LINE-RASTER.csv.
- The traces are combined red/blue estimates because the species curves overlap/interleave at this raster resolution; do not assign species, treat them as measurements, or claim exact curve reproduction.
- Wired structural/range/trend checks into experiments/validate_wilbers_fig_s5_digitization.py.
- Next: compare these raster estimates with the prior equation-level reconstructions without refitting, quantify residuals only where axes/overlap support it, and preserve the missing source plotting code/raw recordings as an unresolved evidence gap. Do not promote the spike mechanism.


### 2026-11-12 — refined Figure S5 curve comparison

- Recalibrated panel J against the six existing experimental marker centers and updated its six inter-marker model-line estimates. The raster trace is within 0.36 ms RMSE of both the human and mouse equation-level current-fit reconstructions; the overlaid traces cannot be species-discriminated at this resolution.
- Panel K's raster line is approximately 444.8 ms, close to the fixed 450-ms slow component; panel N is approximately 2.78–2.79 s, close to the pooled slow-recovery constant.
- Panel M remains a raster estimate only. Next work: inspect the deposited K_IV recovery model path and compare its exact voltage-dependent model output to the raster before interpreting any residual against the Rust K_recovery protocol replay.


### CI correction and verified rerun

Run 43130214819 exposed an overly restrictive validator lower bound (18 ms) for the 17.51-ms final panel-J sample. The data point was not altered; the accepted plotted range was corrected to 17 ms. Follow-up run 43130293760 passed formatting, Clippy, all Rust tests, Python syntax, both Wilbers validators, repository policy, and cleanup on its exact commit. Preserve this failure/fix history.


### 2026-11-12 — historical archive audit completed

- Owner-provided `HumanJSProject.zip` was inspected read-only; SHA-256 `0deb7789a8df444ea6a4e957dc63520cf6e786c18887286c3a31a319f61eccdf`; 422 entries, 375 files, 26,045,082 uncompressed bytes.
- Inventory: 16 old JavaScript source files, 28 architecture notes, 143 experiment documents, 92 simulator-result JSONs, three test files, historical requirements/decisions, and a large scientific dossier.
- Archive remains outside GitHub. Do not port the legacy runtime or treat its old simulator outputs as current HumanJS or biological evidence. Selectively reuse a research citation only after checking the primary source; re-run a historical experiment in the Rust core before relying on its outcome.
- This was triage, not exhaustive scientific revalidation of every old source/note. ADR-017 records the scope and policy. Future chats do not need the ZIP to continue current work.
- Current active task: complete Figure S5 panel-M comparison using the deposited K_IV -> K_recovery source path and report the raster/polyline residual without conflating it with raw experimental evidence.


### 2026-11-12 — Figure S5 panel-M source comparison complete

- Traced the exact deposited Figure S5 recovery path: pre-optimizer human/mouse `K_IV(cell)` calls use pure `k_human.mod` / `k_mouse.mod`; `K_IV` calls `K_recovery`; tau1 is panel M and tau2 panel N. The mouse recovery plot uses the pre-fit model state. Source IDs, SHA-1 values and protocol details are preserved in the replay CSV header and research note.
- Recalibrated M against the 300/200-ms printed ticks. Four combined red/blue raster samples: 134.36, 193.41, 304.46, 350.03 ms. Pooled human/mouse source-polyline comparison: RMSE 2.01 ms, max residual 3.32 ms.
- This is a raster-to-equation-replay consistency check. NEURON was not executed; overlapping species traces are not separable; no raw K recordings or missing per-cell K tau tables were recovered.
- CI runs 43131449785 and 43131513456 failed only because the validator rejected the newly explicit 5-pixel reading uncertainty. The validator was corrected to admit 5 pixels; the digitized samples were retained. Run 43131570918 passed all workflow steps on exact commit 49978d3920eb3d6d53e6dbc2e8aa20c25ef41fae.
- Historical pre-migration archive review is recorded in ADR-017; no archive copy or legacy code is needed in future sessions.


### 2026-11-12 — Human L2/L3 single-compartment acceptance audit

- Source files directly inspected: Dataverse v3.0 na_human.mod file 318563, k_human.mod file 318566, and current-clamp helper cc_tools.py file 318557.
- Voltage-shift polarity resolved: source trates(v+vshift) with helper vshift = −10 mV, matching HumanJS's V−10 mV. Source gate initialization and Na/K Q10 placement also match.
- Geometry, passive leak/capacitance, reversal offsets, K gate fractions and current-density units have been traced. A Rust regression covers source shift and initial gate semantics.
- Do not promote: HumanJS deliberately corrects the broken NMODL trap0, uses RK4 rather than source NEURON cnexp, and has not yet replayed the exact rheobase/1.5×-rheobase current-clamp runner. K recovery includes a pooled human/mouse constant; the conductance fit has cross-species targets; this is not an AIS model.
- Next: implement the exact current-clamp stimulus/rheobase reproduction check, then independently compare source-model features and numerical integrator behavior. Keep evidence limitations explicit.


### Verification correction — source-mapping regression formatting

Workflow run 43133844647 failed at the Rust formatting check only. The failure was the exact rustfmt layout of the newly added current-clamp voltage-shift/initial-state regression; all subsequent workflow checks were skipped, so no compile/test result was obtained in that run. The code was reformatted to the CI rustfmt output without changing its assertions or model behavior. A new workflow run on the correction commit is required before calling this change verified.


### Verification resolved — source-mapping regression

Follow-up workflow run 43133951113 completed successfully on exact commit 3dfc6ea954401e05aafe6aac4c29a3b5b07870f1. Rust formatting, Clippy, Rust tests (including current_clamp_voltage_shift_and_initial_gates_match_hybrid_source), Python syntax, both Wilbers validators, and repository policy all passed. The earlier formatting-only failure in run 43133844647 is resolved; it did not require changing the scientific assertions or relaxing checks.


### Verification correction — current-clamp protocol test

Workflow run 43134237756 failed only at rustfmt after the first source-protocol test commit; no compile or test was run in that attempt. Its formatter output was inspected. The rheobase helper was also corrected to match the deposited Python loop's increment-before-first-trial order in each of its 0.1/0.01/0.001-nA phases, retaining the source's backoff after the first two phases. The 20-nA/200-step guard is a HumanJS resource bound, not a biological threshold. Await the follow-up workflow before considering the protocol test verified.


### Verification correction — exact rustfmt shape

The next workflow (43134383535) again stopped at rustfmt only. The CI diff showed two initial-condition constructors that rustfmt collapses to a wrapped single expression. Those exact formatting changes are applied; the rheobase increment-order correction remains intact. No compile/test result was available from that formatting-only run.


### Verification correction — remaining rustfmt constructor

Workflow run 43134461510 reached the formatter and identified one remaining copy of the initial-condition constructor with the same rustfmt reflow. That exact formatting-only correction is now applied. No compilation or Rust test result was obtained from the previous run; use the next workflow as the verification gate.


### Verification correction — strongly typed voltage comparisons

Workflow run 43134527862 passed rustfmt but Clippy/compilation rejected direct ordering comparisons on the intentionally non-ordered Volts newtype. The regression now compares its explicit SI values via as_volts(), retaining dimensional types everywhere else. The failure was a compile-time API misuse, not a numerical test result.


### Verification correction — voltage-crossing condition formatting

Workflow run 43134596362 identified only the formatter's preferred single-line layout for the two SI-value threshold-crossing conditions. The logic remains the same; exact rustfmt output is now applied. The type-corrected regression still awaits compilation and execution.


### Verification correction — rustfmt condition/brace layout

Workflow run 43134667073 passed no code checks beyond setup because rustfmt requested the line break before the opening brace for both threshold conditions. The condition remains two typed SI-voltage comparisons; only its precise formatter-required wrapping is changed here. No test execution has yet succeeded for the new rheobase protocol.


### Verification failure — current-clamp source threshold extractor

Workflow run 43134731123 passed formatting and Clippy and executed 30 of 31 tests successfully. The new protocol test panicked while reproducing the source threshold heuristic: within its peak-centred −1/+3 ms window, it found no pre-maximum-slope derivative below 40 mV/ms. This is not an accepted spike-feature result and must not be fixed by widening thresholds. The next run adds the derivative/window diagnostics needed to locate whether the issue is the trace window, stimulus replay, or source-equivalence assumptions.


### 2026-11-12 — author current-clamp protocol replay diagnostic

A Rust-side replay of the published rheobase search and 1.5×-rheobase pulse reaches one −20-mV crossing, but the peak is 59.594103 mV (outside the 48–53-mV regression band). The published 40-mV/ms threshold heuristic is also undefined: its peak-centred window begins at 47.44865 mV/ms with no pre-maximum derivative below 40. Both mismatches are explicitly preserved as regressions. This is HumanJS RK4 output, not a biological result or source-exact NEURON reproduction.


### Author current-clamp replay — quantitative mismatch

The 1.5×-rheobase Rust replay finds one −20-mV crossing, but the HumanJS peak is 59.594103 mV, outside the existing 48–53-mV published-scale test band. The source threshold extractor is also undefined: its first derivative sample is 47.448652 mV/ms, already above the strict 40-mV/ms criterion, and maximum derivative is 526.597377 mV/ms. This mismatch is now asserted explicitly; no tolerance or target was widened. It is HumanJS RK4 output, not an original NEURON source run or biological result.


### Verification correction — stale peak-band assertion

Run 43135076696 exposed a stale 48–53-mV assertion that remained ahead of the new explicit mismatch assertions. It correctly failed on the 59.594-mV model output, but prevented the test from reaching its assertions that pin this result and the undefined threshold extractor. The stale success-band assertion is removed; the test is renamed to state that it preserves the published-feature mismatch. The 48–53-mV band is not widened.


### Verified protocol mismatch regression — CI success (2026-11-12)

Commit b44a0650b72501f76864f68ef593a772e16c779f removes the stale peak-band success assertion and renames the new test to `author_current_clamp_rheobase_protocol_preserves_published_feature_mismatch`. The test now checks exactly one −20-mV crossing, pins the HumanJS RK4 peak at 59.59410314264656 mV, asserts it remains above the 53-mV upper regression bound, and preserves the undefined source-threshold case (first derivative 47.448651583561485 mV/ms; max 526.5973771676144 mV/ms). It does not claim the 50:50 AP1 target is met.

GitHub Actions run 43135180538 completed successfully on exact commit b44a0650b72501f76864f68ef593a772e16c779f: rustfmt, Clippy, all Rust tests (31 passed), Python syntax, Figure S5 validator, current-clamp grid validator, and repository-policy validation passed. Earlier failed workflow attempts are recorded above; they surfaced formatting/API mistakes and then the actual model mismatch. This successful test is a regression which preserves the discrepancy, not a pass of the biological/source acceptance gate. No NEURON run or biological validation is claimed.


### Follow-up documentation verification

The documentation commit `5767d020cc096002a3afd83bf014018b6e30e880` is also CI-clean: GitHub Actions run `43135290117` completed successfully on that exact SHA. Formatting, Clippy, the full Rust test suite, Python syntax, both Wilbers scientific validators and repository policy all passed. The protocol-mismatch test is a passing regression because it deliberately preserves the observed out-of-band HumanJS output; it does not imply scientific acceptance.


### 2026-11-12 — corrected Wilbers current-clamp source reproduction

The previous 101-pA/59.594-mV/undefined-threshold conclusion is retracted. The first Rust test transcription omitted the authors' initial 0.1-nA trial before the increment loops. With the initial source trial restored, both NEURON 9.0.2 and HumanJS return 20.0-pA rheobase and use the same 30.0-pA AP1 pulse. The unchanged deposited helper/mechanisms were run independently; HumanJS matches all five extracted AP1 features within the measured RK4-versus-cnexp differences. Shared voltage samples have 0.455221-mV RMSE and 4.615873-mV maximum absolute error. The detailed reference, hashes, and reproduction runner are in research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md Section 6 and experiments/WILBERS-CURRENT-CLAMP-NEURON-REFERENCE.md. The model remains exploratory and unaccepted.


### CI verification of corrected NEURON reference replay (2026-11-12)

Commit 3ea7cb43fcc0e9627cfc7b6cdde3c28055356dd0 passed GitHub Actions run 43139126138. All required steps succeeded: Rust formatting, Clippy, complete Rust workspace tests, Python experiment-runner syntax, Figure S5 digitization validator, current-clamp conductance-grid validator, and repository policy. Two immediately preceding runs stopped at rustfmt because the source file lacked its terminal newline; that formatting-only issue was corrected. The source-model comparison assertions themselves passed unchanged. This CI validates the implementation and its pinned reference checks, not biological validity.

### 2026-11-12 — Wilbers AP1 solver-residual attribution

The unchanged `cc_tools.run_1AP` sets `h.dt=0.02` ms and leaves `h.secondorder` untouched; the NEURON 9.0.2 replay measured the default `secondorder=0` (fully implicit backward Euler). Both source NMODL channel mechanisms continue to use `METHOD cnexp` for their gates. The human Na mechanism has an active voltage-rate table (`FROM -120 TO 100 WITH 199`); the human K table code is commented out. NEURON's current reference documents the default and the Crank–Nicolson alternatives: https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html.

A source-verified numerical sensitivity experiment now separates the major solver effect. The original 20-µs, secondorder=0, Na-table-on baseline remains 0.455221-mV RMSE / 4.615873-mV max residual against HumanJS. Changing only the diagnostic NEURON voltage solver to secondorder=1 at the same 20-µs step reduces this to 0.038124 / 0.594290 mV. With 5-µs CN and Na table off the residual is 0.004756 / 0.062958 mV against the 20-µs HumanJS trace; a separately matched 1-µs CN/table-off comparison gives 0.001515 / 0.005020 mV. No biological parameters were changed. Table on/off is a secondary, timestep-dependent effect; the original table-on source remains canonical. Temporary diagnostic-only counters around the unchanged source `trap0` predicate observed 800 Na calls (including table generation) and 13,188 K calls, with zero fallback entries; the instrumented and original source traces were bit-identical over all 1,451 samples. The source defect remains relevant to other voltage trajectories and protocols.

New tools: `crates/humanjs-core/examples/wilbers_current_clamp_trace.rs` exports a HumanJS trace and independently replays the deposited rheobase search; `experiments/diagnose_wilbers_neuron_solver.py` downloads/checksums the five CC0 files, compiles unchanged NMODL, verifies the unmodified source baseline, then varies timestep, NEURON voltage integration order, and Na table use. Details and exact numbers are in `experiments/WILBERS-CURRENT-CLAMP-NEURON-REFERENCE.md` and Section 6 of the research record. This attribution is specific to a model-side AP1 numerical comparison, not biological validation; the human data/model-acceptance blockers remain open.

The clean main clone at pre-change HEAD `d9b0b871e4aadacb3cc1b58e873a1c32fd11563f` passed `cargo test --workspace --locked` locally (31 unit + 3 synapse integration + 6 passive membrane integration tests). The new Rust trace example also ran, independently returned rheobase 20.0 pA / AP1 30.0 pA, and emitted 1,450 samples. The diagnostic script passed Python 3.10 syntax, CLI, and end-to-end execution against the checksum-verified NEURON 9.0.2 environment; its author-helper baseline reproduced the prior reference to floating-point precision. GitHub Actions run `43144988410` passed on exact current HEAD `443f811296e591d6669c9e26b22b5906d1ae979d` after a formatting-only final-newline repair.

### 2026-11-12 — direct-main commit and CI verification of solver attribution

The numerical diagnosis, reproducible experiment script, Rust trace-export example, CI syntax-coverage update, and research/status documentation were committed directly to `main` in `65607325083b1152867ef7add5ef8f72eb3d2505` (`research(neuro): attribute Wilbers AP1 solver residual`). Its first workflow attempt, run `43144643445`, failed only at `cargo fmt --all -- --check`: the file-transfer step omitted the Rust example's terminal newline. This was corrected in `443f811296e591d6669c9e26b22b5906d1ae979d` (`style(neuro): preserve final newlines for CI`), which passed CI before the subsequent documentation verification commit `2ede05110553837938ccfc0fbbbb7efdd898daf9`. GitHub Actions run `43144988410` completed successfully on that exact SHA; rustfmt, Clippy, Rust tests, all experiment Python syntax, both Wilbers validators, and repository policy all passed. The workflow now syntax-checks all `experiments/*.py`. The earlier format-only failed attempt remains visible in Actions history and is not concealed.

Current main tree SHA `94d5793aec8b09c94f60ba08f6403bc5d14f54c2` contains 74 entries (`truncated=false`). The branch listing contains only `main`; open issues and pull requests remain zero. No biological acceptance gate has changed. The spike-capable single-compartment model is still exploratory and not scientifically accepted.

### 2026-11-12 — secondary archive cross-check for Wilbers K-current source data

The primary Science Advances article (DOI `10.1126/sciadv.ade3300`) directs its public data, model files and scripts to Dataverse DOI `10.34894/L5J0SD`; its associated-data section lists Supplementary Text, Figs. S1–S7 and Tables S1–S3, without another linked raw-electrophysiology archive. Exact-title/site-restricted search returned no matching additional Wilbers K-current/per-cell kinetic deposit on DANDI, Zenodo, Dryad or Figshare. A Utrecht repository hit was a copy of the article, not an independent raw-data deposit. This is bounded index-search evidence, not proof of global absence. The previously checked Dataverse v3.0 65-file inventory still lacks per-cell K voltage-clamp traces and individual K-kinetic CSV targets. Distinguish the paper's published-conclusion data sufficiency from HumanJS's stronger cell-level reconstruction requirement. References and search limits are recorded in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`.

### 2026-11-12 — latest-main independent rerun

After synchronizing the local checkout to the latest `main` baseline `30dcee632b9ad5a64e4d6c1f496b9f00e03d3c64`, the local verification was repeated: `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace --locked` all passed (31 unit, 3 synapse integration, 6 passive membrane integration tests). The Rust AP1 trace example ran at both 20 µs (1,450 samples; peak 50.793612 mV at 4.16 ms) and 1 µs (29,000 samples; peak 50.818920 mV at 4.15 ms); both independently found 20-pA rheobase and applied 30-pA AP1. The 20-µs HumanJS trace's difference from its 1-µs trace is small relative to the original source-default residual.

The NEURON 9.0.2 diagnostic script was re-run end-to-end from this synchronized checkout with the pinned environment and checksum-verified Dataverse sources. It again found 20-pA rheobase and the unchanged source baseline comparison (1,450 common samples; RMSE 0.455221106542 mV; max residual 4.615872929631 mV at 3.94 ms). The controlled variants reproduced the earlier results: 20-µs CN/table-on RMSE 0.038124305 mV; 5-µs CN/table-on 0.024744611 mV; 5-µs CN/table-off 0.004756176 mV. The diagnostic command without the pinned `nrnivmodl` directory on `PATH` correctly failed with an actionable environment error; rerunning with `PATH=/tmp/hjvenv/bin:$PATH MAKEFLAGS=-j1 MPLBACKEND=Agg` succeeded. No generated traces or result JSONs were added to Git.

### 2026-11-12 — Wilbers AP1 internal gate-state comparison

The AP1 diagnostic now exports and compares the five source NMODL STATE variables (Na m/h, K m/h1/h2) with the five HumanJS live gate fractions. In the author-default 20-µs, secondorder=0, Na-table-on run, gate RMSEs are 0.003213 Na activation, 0.002729 Na inactivation, 0.001386 K activation, 0.0000810 K fast inactivation, and 0.0000770 K slow inactivation (dimensionless fractions). The largest state differences occur during the 3–4.2-ms spike upstroke/peak; pre-spike state differences are small. Applying the deposited conductance equations to gate traces gives derived Na/K conductance-density RMSEs of 0.1436/0.02367 pS/µm². These are model outputs, not measurements.

A 1-µs CN/table-off convergence diagnostic compared all 29,000 post-step samples against 1-µs HumanJS: gate RMSEs were 0.0001406 Na activation, 0.0000990 Na inactivation, 0.0000544 K activation, 0.00000352 K fast inactivation, and 0.000000572 K slow inactivation. This does not make the non-default NEURON solver the paper's baseline or establish biological fidelity. The Rust trace example and Python source diagnostic now optionally emit/compare gate CSVs; details and reproducible commands are in the Wilbers experiment note and research Section 6. The shared-voltage counterfactual now isolates the gate-update formula under a prescribed sampled voltage path; voltage-stage interpolation and coupled feedback remain to be decomposed.


### 2026-11-12 — internal gate-state feature commit and CI verification

Direct-main commit `ada7a9e8ecd478adfd3b411d2ccd0bdefbd1b137` (`feat(neuro): compare AP1 channel-gate trajectories`) adds optional five-gate recording to the Rust AP1 exporter, source NMODL gate recording and comparison to the NEURON diagnostic, and updated research/experiment/BOOT/status/handoff records. Actions run `43147714885` passed on the exact commit. The author-default 20-µs comparison shows gate RMSE fractions 0.003213 Na activation, 0.002729 Na inactivation, 0.001386 K activation, 0.0000810 K fast inactivation, 0.0000770 K slow inactivation. The high-resolution 1-µs CN/table-off comparison includes all 29,000 samples and reduces these values further. This remains model-to-model numerical analysis; it does not change the exploratory/unaccepted status.

### 2026-11-12 — shared-voltage gate-integrator decomposition

The diagnostic now applies both cnexp-equivalent and RK4 gate updates to the same source voltage samples, using the post-step voltage `V[n+1]`, common initial NMODL gate states, and the same continuous rate equations. The source exponential recurrence reproduces actual direct-rate NMODL gate states within a maximum 1.76e-6 fraction (diagnostic guard 1e-4). At 20 µs, the isolated RK4-versus-cnexp difference is 2.8221e-6 overall gate RMSE / 1.16295e-4 max, dominated by Na activation; at 1 µs it falls to 1.1710e-11 / 4.8856e-10. On the same path, Na TABLE versus direct-rate CNEXP yields 3.70195e-5 overall RMSE / 1.23720e-4 max, affecting only Na gates. These effects are much smaller than actual dynamic source-vs-HumanJS gate errors, so differing voltage paths/stage sampling/coupled feedback remain the main unresolved numerical contributors. No biological validity claim follows.


### 2026-11-12 — shared-voltage gate integrator and Na TABLE attribution committed

Direct-main commit `eec5651c80b71e0d7706f617d944cfad772c38fb` (`research(neuro): isolate gate solver effects on shared voltage`) adds a validated post-step voltage-sample counterfactual comparing exact exponential (cnexp-equivalent) and RK4 gate updates, plus the source's 200-node Na TABLE interpolation against direct rates. The matching CNEXP recurrence reproduces source NMODL gate states within 1.8e-6 gate fraction when rate modes match (guard 1e-4). At 20 µs, isolated RK4-versus-cnexp error is 2.8221e-6 overall RMSE / 1.16295e-4 maximum; at 1 µs it falls to 1.1710e-11 / 4.8856e-10. Na TABLE versus direct rates yields 3.70195e-5 overall RMSE / 1.23720e-4 maximum. These are numerical counterfactuals; the full dynamic gate residual remains much larger and is consistent with voltage-path/stage-coupling differences. Workflow `43149669478` passed on the exact commit. No biological acceptance claim is made.


### 2026-11-12 — voltage-stage sampling counterfactual added

The shared-voltage gate diagnostic now replays the recorded NEURON voltage path with four RK4 gate-voltage conventions: hold the left endpoint, hold the interval midpoint, hold the right endpoint (the previous comparison), or linearly interpolate voltage at the RK4 stage times. All four start from the same recorded NMODL gate state, use the same analytic Wilbers gate rates and fixed timestep sequence, and are compared against both the recorded NMODL gates and one another. The −10-mV channel shift is applied consistently. All replay trajectories are checked for finite gate fractions in [0, 1].

This isolates sensitivity to voltage sampling on a prescribed source voltage trajectory; the linear ramp is not the actual intermediate voltage of the coupled HumanJS membrane solver. The diagnostic does not yet partition the feedback difference between voltage and gates in a fully coupled run. Numerical outputs require the pinned Python 3.10 / NEURON 9.0.2 environment; the available session runtime is Python 3.13.5 without NEURON, so no new source replay numbers are claimed here. Run the documented solver diagnostic with the pinned environment to obtain the four per-gate error profiles. The spike-capable HumanJS mechanism remains exploratory and scientifically unaccepted.


### 2026-11-12 — executable tests for voltage-stage sampling counterfactuals

The shared-voltage gate replay now validates all five source gate traces against the voltage sample count, finite values, and [0, 1] bounds before integration. Its gate-metric helper rejects malformed, non-finite, or shape-mismatched arrays. A standard-library unittest suite exercises (1) constant voltage, where all sampling conventions must coincide, (2) a varying voltage path, where linear-ramp and right-hold RK4 must differ, and (3) malformed gate lengths and metric shapes. CI installs the already-pinned NumPy 1.26.4 test dependency and executes `python3 -m unittest discover -s experiments -p 'test_*.py' -v`. Workflow `43167476483` passed on exact commit `c3dcffcef5b07c40f100a3ed167944afc00b104d`; the new four tests passed, along with rustfmt, Clippy, all Rust workspace tests, experiment syntax, both Wilbers validators, and repository policy.

These are deterministic software tests of the counterfactual implementation, not a NEURON source replay and not biological validation. The pinned Python 3.10 / NEURON 9.0.2 end-to-end diagnostic still needs to be run to produce source-trace-specific sensitivity values. The exploratory single-compartment model remains unaccepted.


## Next concrete research action

The 441-point K activation voltage-grid comparison and both critical trap0-landmark regressions are now implemented. Next, probe the other K kinetic components (fast inactivation and its recovery rate) at their actual half-voltage parameters and verify their exact limiting behavior against the original NMODL equations. Keep rates and channel parameters unchanged; this remains software/source-equation verification, not biological validation.


## 2026-11-12 paired source/HumanJS voltage-path gate attribution

The source replay was subsequently executed in a disposable Ubuntu 22.04 environment with Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, and g++ 11.4.0. The Rust HumanJS trace exporter generated the matching 20-µs AP1 voltage and five-gate traces. The unchanged author-helper baseline reproduced exactly (1,451 samples); source-vs-HumanJS voltage RMSE was 0.4552211065 mV, maximum 4.6158729296 mV at 3.94 ms. In the canonical 20-µs, secondorder=0, Na-table-on run, five-gate RMSEs were 0.003212673 Na activation, 0.002729390 Na inactivation, 0.001386170 K activation, 0.0000810083 K fast inactivation, and 0.0000769564 K slow inactivation.

On the identical recorded NEURON voltage path, RK4 gate replay RMSE against NMODL gates was 0.00330024 for left-endpoint hold, 0.00161205 for midpoint hold, 0.00157222 for linear voltage ramp, and 0.0000369553 for right-endpoint hold. This independently confirms the source NMODL gate-state update is reproduced by the post-step voltage convention.

A second counterfactual replayed the source gate equations on the HumanJS voltage samples, with the same initial source gates. With direct analytic Na rates (table off), five-gate RMSE against HumanJS live gates was 0.00199367 for source-vs-HumanJS actual gate traces, 0.00161879 for right-endpoint CNEXP, 0.00172408 for left-endpoint RK4, 0.0000385578 for midpoint RK4, and 0.0000447473 for linear-ramp RK4. The midpoint replay reduces the aggregate five-gate residual by about 51.7-fold (98.07%). Enabling the source 200-node Na table raises the midpoint/linear replay residuals to 0.0000527946 / 0.0000587224. This strongly indicates that most of the observed gate mismatch comes from the different voltage trajectories and per-step voltage sampling, rather than a different set of gate-rate parameters.

The complete 12-variant source matrix (dt 20/10/5 µs, secondorder 0/1, Na table on/off) completed. Key source-vs-HumanJS voltage RMSEs were 0.455221 mV for the unchanged author baseline, 0.0381243 mV for 20-µs secondorder=1/table-on, 0.0127377 mV for 10-µs secondorder=1/table-on, and 0.00475618 mV for 5-µs secondorder=1/table-off. The diagnostic output and generated traces stayed outside Git.

Interpretation limits: source NMODL CNEXP effectively advances gates using the post-step voltage sample; HumanJS uses coupled RK4 with voltage evaluated at internal stages. Prescribed midpoint and linear interpolation on the HumanJS voltage path closely reproduce HumanJS gates, but neither captures the actual internal RK4 stage voltages. This is a numerical model-to-model attribution, not proof that either solver is biologically more accurate and not biological validation. The single-compartment spike-capable mechanism remains exploratory and unaccepted. The next experiment should capture the actual four RK4 stage voltages from the HumanJS step and compare exact stage replay with these midpoint/linear proxies, without changing biological parameters.



### Exact coupled RK4 voltage-stage capture and gate replay (2026-11-12)

HumanJS now exposes an opt-in `step_with_voltage_stages` diagnostic that returns the exact four membrane-voltage components of the intermediate state vectors passed to its coupled RK4 derivative evaluations: k1 at t, k2 at t+dt/2, k3 at t+dt/2, and k4 at t+dt. The ordinary `step` path does not materialize the diagnostic output. The AP1 example accepts `--stages-output` and writes one four-stage row per completed step; the NEURON diagnostic accepts `--humanjs-voltage-stages` and validates the stage CSV's columns, finite values, sample count, and timestamps before replay.

Pinned execution: Ubuntu 22.04, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, g++ 11.4.0, Rust 1.85.0. The final AP1 run exported 1,450 voltage-stage rows aligned to the 1,450 HumanJS voltage and gate samples. The unchanged author-helper source baseline remained 0.4552211065 mV voltage RMSE (4.6158729296 mV maximum at 3.94 ms) against HumanJS.

The source gate equations were then replayed using the four actual HumanJS voltage stages at each step, with identical initial gates and the same RK4 gate-stage update:
- Direct analytic Na rates (Na TABLE off): five-gate RMSE **2.45244e-8**, maximum absolute gate error **3.99679e-7**. Per-gate RMSE: Na activation 1.71060e-8, Na inactivation 2.86599e-13, K activation 5.21020e-8, K fast inactivation 2.86267e-13, K slow inactivation 2.83516e-13.
- Source 200-node Na TABLE enabled: five-gate RMSE **3.93000e-5**, maximum absolute error **1.25180e-4**. The residual is confined overwhelmingly to Na gates (activation 3.78226e-5; inactivation 7.93216e-5); K activation remains 5.21020e-8 and both K inactivation gates remain approximately 2.86e-13.

For context, the source NMODL gate traces versus HumanJS live gates have aggregate five-gate RMSE 0.00198518. Thus exact-stage replay reduces that discrepancy by about 80,900-fold with direct rates, and by about 50.5-fold with the source Na TABLE enabled. The remaining table-on difference is a lookup-table/direct-rate effect, not evidence of a different K gate mechanism. The k2 and k3 voltage stages are not interchangeable: their maximum absolute difference was 0.399717 mV at 3.98 ms; k1-to-k2 and k3-to-k4 differences reached 4.69044 and 4.57701 mV during the spike.

The complete 12-variant NEURON matrix (20/10/5 µs, secondorder 0/1, Na TABLE on/off) was rerun against the exact-stage trace. The HumanJS-stage gate replay is independent of the NEURON variant, while the source voltage comparisons retain the earlier solver sensitivity (author default 0.455221 mV; 20-µs CN/table-on 0.0381243 mV; 10-µs CN/table-on 0.0127377 mV; 5-µs CN/table-off 0.00475618 mV).

Interpretation: this is strong numerical evidence that the gate-update equations and RK4 gate-stage handling in HumanJS match the replayed Wilbers gate equations when supplied with HumanJS's actual coupled voltage stages. It does not explain away the remaining membrane-voltage trajectory difference, validate either solver biologically, or change the exploratory/unaccepted status of the single-compartment model. All stage traces and diagnostic JSON remained outside Git.

The source-order and CN replays now reproduce their NEURON variants within about 0.00056 mV. The 250-ns current-balance identities close, and the actual source/HumanJS voltage-residual derivative is accounted for by their current difference. Next, compare prescribed-path CN midpoint/left-gate current and fully evolved source/HumanJS current mismatch across timestep refinement and Na TABLE modes.


### Matched-state membrane-current balance and source-order replay (2026-11-12)

The remaining AP1 voltage discrepancy was isolated without changing any biological parameter. The Rust single-compartment simulation now provides opt-in current-balance diagnostics at the four actual coupled RK4 derivative stages. Each record contains sodium, potassium, leak, and injected current density in A/m² plus the voltage derivative in V/s. A non-advancing current_balance query exposes the live endpoint balance. The ordinary step path passes no diagnostic output and does not construct current-balance records. The AP1 exporter accepts --currents-output; its CSV contains all four stage balances and the committed endpoint balance.

The NEURON runner now calls h.fcurrent() after each h.fadvance() and manually samples ina, ik, and i_pas at that committed endpoint. This is necessary because Vector.record sampling of BREAKPOINT current values occurs before the next fixed-step current refresh; the manual samples align current values with the same endpoint voltage and gates. NEURON current density is converted from mA/cm² to SI A/m² by multiplying by 10. The comparison is restricted to the all-human kinetic endpoint (na_ratio=k_ratio=1) and secondorder=0; the HumanJS current-stage trace must have exactly aligned timestamps.

The measured source voltage update is:

    C_m * (V[n+1] - V[n]) / dt = I_inj[n] - I_ion(V[n+1], G[n])

The source voltage solve therefore uses the previous recorded gate state G[n] with the implicit endpoint voltage V[n+1]. The NMODL gates are then advanced by CNEXP using the post-step voltage sample V[n+1] (with the deposited -10-mV channel shift) to produce G[n+1]. The post-step BREAKPOINT current refreshed after fadvance uses G[n+1], and is not the same current evaluation that drove the preceding voltage solve. This is the source's sequential voltage/gate update ordering.

The current-law check at 20 µs, secondorder=0, Na TABLE on, compared the deposited Na/K/leak equations evaluated at the source endpoint state against the refreshed NEURON endpoint currents. Maximum absolute differences were 1.78×10⁻¹⁵, 3.33×10⁻¹⁶, and 1.39×10⁻¹⁷ A/m² respectively. The source voltage capacitor-equation residual using V[n+1] and G[n] was 1.60×10⁻¹³ A/m² RMSE and 3.71×10⁻¹² A/m² maximum. This confirms the current equations, signs, geometry/capacitance conversion, and endpoint sampling; it does not merely compare two unrelated voltage traces.

HumanJS's RK4 stage balances independently close: the weighted four-stage capacitance current versus the weighted stage current RHS has 2.73×10⁻¹³ A/m² RMSE and 9.35×10⁻¹³ A/m² maximum error. The RK4-weighted voltage derivative versus the recorded voltage increment has 2.03×10⁻¹¹ V/s RMSE and 4.96×10⁻¹¹ V/s maximum error. These identities are also covered by Rust regression tests.

At 20 µs, the source voltage-solver current (implicit endpoint voltage with G[n]) versus the HumanJS RK4-weighted stage current has 0.026606 A/m² total RMSE and 0.428910 A/m² maximum error. Component RMSEs are 0.025245 A/m² Na, 0.004299 A/m² K, and 0.000257 A/m² leak. The difference between the source solver current and its refreshed post-step current is itself substantial around the upstroke (Na 0.061751 A/m² RMSE / 1.139587 A/m² max; K 0.004484 / 0.037382; leak effectively zero), which is exactly where the source's sequential gate update matters most.

An independent source-order replay was added to the Python diagnostic. It solves the implicit voltage equation with the previous gate state, then advances all five gates by the deposited CNEXP equations using the new voltage. It uses the exact source conductance densities, temperature factor, reversal potentials, leak density, current pulse, and selected 200-node Na rate table; it does not fit or modify parameters. Results:

| Fixed step / Na rate mode | Source-order replay vs NEURON voltage RMSE | Maximum error | Source-order replay vs HumanJS at matching step |
|---|---:|---:|---:|
| 20 µs, Na TABLE on | 0.00053756 mV | 0.00718343 mV | 0.455684 mV RMSE |
| 10 µs, Na TABLE on | 0.00054825 mV | 0.00741506 mV | 0.205701 mV RMSE |
| 5 µs, Na TABLE on | 0.00055351 mV | 0.00757305 mV | 0.0901381 mV RMSE |
| 20 µs, direct Na rates | 0.00054034 mV | 0.00722508 mV | 0.479236 mV RMSE |

The source-order replay's gate RMSE against NEURON at the author-default 20-µs/Na-table-on condition is 2.81×10⁻⁶ overall, with maximum 6.52×10⁻⁵ gate fraction. Thus the independently coded update sequence reproduces the original NEURON trace within about 0.00054 mV, while the source-vs-HumanJS voltage difference falls as the first-order timestep is reduced. This attributes the remaining model-to-model voltage residual to the source's sequential implicit-voltage/CNEXP-gate update versus HumanJS's fully coupled RK4 stage updates, with the Na TABLE as a smaller rate-evaluation contribution. It does not imply that either solver is biologically superior.

Reproduce the 20-µs current-balance comparison and Na TABLE toggle (pinned Ubuntu 22.04, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4, g++ 11.4.0, Rust 1.85.0):

    cargo run -p humanjs-core --release --example wilbers_current_clamp_trace -- --step-us 20 --gates-output /tmp/humanjs-gates.csv --stages-output /tmp/humanjs-stages.csv --currents-output /tmp/humanjs-currents.csv > /tmp/humanjs-voltage.csv
    python3.10 experiments/diagnose_wilbers_neuron_solver.py --humanjs-trace /tmp/humanjs-voltage.csv --humanjs-gates /tmp/humanjs-gates.csv --humanjs-voltage-stages /tmp/humanjs-stages.csv --humanjs-current-stages /tmp/humanjs-currents.csv --dt-ms 0.02 --secondorder 0 --na-table 1 0 --trace-dir /tmp/wilbers-voltage --gate-dir /tmp/wilbers-gates --current-dir /tmp/wilbers-currents --output /tmp/wilbers-current-balance-results.json

The 10-µs and 5-µs matched-step convergence runs use the same exporter with --step-us 10 / --step-us 5 and the corresponding --dt-ms 0.01 / --dt-ms 0.005, without --humanjs-current-stages. All generated traces and JSON remain outside Git. The spike-capable single-compartment mechanism remains exploratory and unaccepted; these are numerical source-reproduction and software regression results, not biological validation.



### AP1 CN current replay — 2026-11-13

- The AP1 exporter now accepts integer nanoseconds while retaining the microsecond option. The 20-µs voltage CSVs from the old and new options were byte-identical; a 333-ns step is rejected because pulse/protocol boundaries do not align.
- The new independent CN replay uses the midpoint membrane voltage with G[n], then advances NMODL gates by CNEXP using V[n+1]. At 1 µs and 250 ns, replay-vs-NEURON voltage RMSE is approximately 0.000557 mV, and aggregate gate RMSE is approximately 2.862e-6.
- At 250 ns, the actual source CN midpoint-current balance closes to 1.48e-13 A/m² RMSE and HumanJS RK4 weighted current balance to 2.96e-13 A/m². The derivative of their actual voltage residual equals the negative source/HumanJS current difference to 4.12e-11 A/m² maximum.
- Actual source/HumanJS current mismatch is 1.742e-5 A/m² RMSE. In the upstroke, sodium dominates; during early repolarization, potassium dominates; in the post-spike tail, leak dominates.
- The same-HumanJS-path midpoint/left-gate current counterfactual gives 4.023e-4 A/m² total RMSE against RK4-weighted currents. This is a separate held-gate counterfactual, not a coupled CN run. Its difference from the actual source-path result shows why evolving state history must be retained in the interpretation.
- Exact HumanJS RK4-stage gate replay still matches HumanJS live gates at 250 ns with 2.5055e-8 aggregate gate RMSE.
- The 125-ns HumanJS voltage/gate/stage/current CSVs were generated (232,000 rows each), but the expanded NEURON run was killed by the 1-GiB VM memory limit (exit 137); no 125-ns current-balance result is claimed.
- Final local verification: 22 Python experiment tests, Python syntax, Rust format/Clippy/workspace tests, both Wilbers validators, repository policy and diff checks passed before documentation cleanup.

Next concrete step: compare prescribed-path CN midpoint/left-gate currents and fully evolved source/HumanJS current mismatch across matched timestep refinement and both Na TABLE settings. Keep biological parameters fixed and retain the author-default NEURON configuration.


### 2026-11-13 — matched 5-µs AP1 current-history refinement

The latest clean checkout was synchronized to parent dde92f10f229a7a3249cc32be4dcd9ac37726fe9. A fresh HumanJS 5-µs run exported 5,800 aligned post-step voltage, five-gate, voltage-stage and current-stage samples. The pinned research environment was Ubuntu 22.04, Rust 1.85.0, Python 3.10.12, NEURON 9.0.2, NumPy 1.26.4 and g++ 11.4.0. The unmodified author helper retained its 20-µs, secondorder=0, Na TABLE-on baseline; rheobase remained 20 pA and AP1 current 30 pA. No channel density or biological parameter changed.

| Na TABLE | HumanJS vs NEURON voltage RMSE | Actual source CN midpoint vs HumanJS RK4-weighted current RMSE | Source CN replay vs NEURON voltage RMSE |
|---|---:|---:|---:|
| On | 0.02487096 mV | 0.00208318 A/m² | 0.00055897 mV |
| Off | 0.00463648 mV | 0.000408145 A/m² | 0.00055720 mV |

The actual TABLE-off current components are Na 3.99798e-4, K 3.43948e-5 and leak 4.68564e-6 A/m² RMSE; TABLE-on components are Na 0.00203776, K 0.000162507 and leak 0.0000248763. Sodium dominates the upstroke; potassium grows comparable/larger during late repolarization; leak dominates the tail. The CN source and RK4 HumanJS capacitor-current identities close below 8.7e-13 A/m², and the voltage-residual/current-difference identity closes below 2.51e-12 A/m².

The prescribed-HumanJS-path CN midpoint/left-gate counterfactual is 0.00785330 A/m² RMSE for both table settings. It is not a coupled membrane trajectory and does not use the NEURON lookup-table setting. At TABLE off, current RMSE is about 23.4-fold higher at 5 µs than at the earlier 250-ns run; the held-left-gate counterfactual is about 19.5-fold higher. This is consistent with timestep sensitivity but does not establish convergence order. The Na TABLE-on comparison has a materially larger residual than the direct-rate counterfactual; TABLE off does not replace the author's reference setting.

A new matched 1-µs HumanJS trace was generated, but the two-mode NEURON extension did not finish: nrnivmodl exceeded a 600-s compiler allowance in the 1-GiB VM. No 1-µs current diagnostic JSON or metrics were produced; the cleanup exception after the compiler timeout is recorded as environment/tooling failure. The earlier 1-µs source/CN result remains separate. All generated traces and JSON remain outside Git. The single-compartment model remains exploratory and unaccepted; these numerical comparisons are not biological validation.

**Next step:** rerun the matched 1-µs and 250-ns Na TABLE on/off matrix in an environment with a reliable NEURON mechanism build, then assess current-residual scaling with at least three matched resolutions before making any numerical-order claim.


### 2026-11-13 — three-resolution AP1 current refinement

Matched 5-µs, 1-µs and 250-ns HumanJS/NEURON 9.0.2 secondorder=1 traces now have source CN current balances for both Na TABLE settings. The original author helper remains at 20 µs / secondorder=0 / Na TABLE on; all-human channel densities, 20-pA rheobase and 30-pA AP1 pulse were unchanged.

| Step | Na TABLE | Voltage RMSE (mV) | Evolved source/HumanJS current RMSE (A/m²) |
|---:|:---:|---:|---:|
| 5 µs | On / Off | 0.024871 / 0.004636 | 0.002083 / 0.0004081 |
| 1 µs | On / Off | 0.028692 / 0.001515 | 0.002474 / 0.00001277 |
| 250 ns | On / Off | 0.028847 / 0.001477 | 0.002490 / 0.00001742 |

Direct-rate voltage RMSE reaches a floor near 0.001476 mV between 1 µs and 250 ns. Switching the Na TABLE changes the source voltage trajectory by a nearly resolution-invariant 0.02907-mV RMSE (maximum about 0.408 mV around 3.912 ms); this perturbation correlates 0.9987 with the TABLE-on HumanJS residual at the two finer steps. On an identical prescribed voltage path, the 200-node table versus analytic rates leaves a stable 3.76e-5 aggregate Na-gate RMSE, while the direct-rate CNEXP/RK4 same-voltage gate difference falls to 4.9e-13 at 250 ns. The table interpolation, not direct-rate gate integration, is therefore the dominant identified source of the table-on floor.

The prescribed HumanJS midpoint/left-gate current counterfactual falls 0.0078533 → 0.0015841 → 0.0004023 A/m², with empirical refinement slopes about 0.99; it is not the fully coupled source trajectory. Actual TABLE-off source/HumanJS current RMSE is non-monotonic at the two finest steps (1.2767e-5 at 1 µs; 1.7423e-5 at 250 ns), so no convergence order is claimed. Capacitor-current balance identities remain closed to approximately 1e-13 A/m², and the voltage/current residual identity closes below 4.12e-11 A/m².

A 125-ns HumanJS trace was generated, but the new memory-reduced NEURON attempt produced no JSON and its failure mode was not captured. A previous 125-ns NEURON attempt was killed at the VM memory limit. No new 125-ns source current figures are claimed. No model parameters changed; the spike mechanism remains exploratory and unaccepted.


### 2026-11-13 — Na TABLE resolution and K trap0 interaction

A controlled 250-ns counterfactual varied only the temporary sodium TABLE from the original 200 nodes to 400, 800 and 1,600 nodes. The original 20-pA rheobase / 30-pA AP1 pulse, channel densities, secondorder=1, and direct-rate control were held fixed.

| Nodes | TABLE-on voltage RMSE (mV) | TABLE-off voltage RMSE (mV) | TABLE-on evolved current RMSE (A/m²) |
|---:|---:|---:|---:|
| 200 | 0.028847 | 0.001477 | 0.002490 |
| 400 | 0.006918 | 0.001477 | 0.0006111 |
| 800 | 0.002102 | 0.001477 | 0.0001640 |
| 1,600 | 0.001466 | 0.001477 | 0.00005147 |

The TABLE-on source/HumanJS voltage residual approaches the direct-rate floor as the grid is refined. The shared-voltage Na-gate interpolation error drops 63-fold from 200 to 1,600 nodes; the coupled source TABLE-on/off voltage perturbation drops about 65-fold. Both show approximately second-order scaling over these four accepted grid sizes. The direct-rate source control remains unchanged.

The 3,200-node TABLE-on trial is excluded: at 4.402 ms the source trajectory reaches the K activation guard where the deposited trap0 predicate checks v+th while its denominator singularity is at v-th. The independent K activation recurrence then fails its 1e-4 tolerance (maximum residual 1.385e-3). A 3,200-node TABLE-off-only control passes and reproduces the 250-ns direct-rate reference. No 3,200-node TABLE-on current/voltage result is accepted.

Original source files and HumanJS model parameters were not modified. Temporary copies, compiled libraries and traces stayed outside Git. The author baseline remains 200 nodes / 20 µs / secondorder=0 / TABLE on. This is numerical evidence, not biological validation; the spike mechanism remains exploratory and unaccepted.


### 2026-11-13 — direct K trap0 rate probe

A focused NEURON 9.0.2 probe evaluated the unchanged K NMODL rate procedure at 34°C around the wrong-sign branch. For tha=-29.961798 mV and qa=6.590406 mV, the predicate fabs((v+tha)/qa) triggers within only ±6.59041e-6 mV of v=-tha, although the denominator singularity is at v=tha.

At the trigger, the source rates are a=36.552210 and b=-23.371390, versus 1.106272 and +0.000124457 from the continuous source formula. The source mtau drops abruptly from about 0.903835 ms to 0.075868 ms (11.91-fold), while minf stays 0.925478. This confirms a finite branch discontinuity, not a true rate singularity. It explains why a fine-table trajectory can trigger a large K activation recurrence error. Original NMODL source and HumanJS parameters are unchanged; no biological validation is claimed.


### 2026-11-13 — high-resolution Na TABLE and K trap0 control

A fresh pinned NEURON 9.0.2 run regenerated the 250-ns HumanJS AP1 trace (116,000 post-step samples). The original 3,200-node Na-table / original-K run reproduced the gate-replay failure: m_k maximum error 0.00138525 at 4.402 ms. The wrong-sign guard fabs((v+th)/q) triggered at 2.37e-7 although the true denominator distance fabs((v-th)/q) was 9.09255.

A temporary K-only mathematical control changed the guard to v-th and the small-x limit to a*q; no parameters changed and no repository source was patched. The same 3,200-node AP1 run then passed the gate check (corrected m_k maximum replay error 1.5844e-5, 87.4-fold lower). A 6,400-node run also passed. At 3,200/6,400 nodes, TABLE-on voltage RMSE was 0.0014623/0.0014729 mV and evolved current RMSE 2.4856e-5/1.9107e-5 A/m²; the direct-rate control stayed at 0.0014774 mV and 1.7423e-5 A/m². Shared-path Na-table gate error and actual source TABLE-on/off voltage perturbation each fell about fourfold when the grid doubled from 3,200 to 6,400 nodes. The result extends the prior approximately second-order table-spacing trend but is still a bounded numerical counterfactual, not a biological comparison.

The corrected-K source CN replay matches NEURON within about 0.000557 mV; its aggregate gate replay RMSE is 2.86e-6 and maximum error 6.76e-5. Current-balance identities remain closed at approximately 1e-13 A/m². Original Dataverse mechanisms, 20-pA rheobase, 30-pA AP1 stimulus, and conductances were preserved; modified NMODL copies and all traces remained outside Git. The author baseline remains 200 nodes / 20 µs / secondorder=0 / TABLE on.


### 2026-11-13 — 12,800-node Na TABLE extension

The corrected-K 250-ns counterfactual was extended to 12,800 Na-table nodes. TABLE-on voltage/current RMSEs are 0.00147610 mV and 1.78514e-5 A/m², versus 0.00147738 mV and 1.74232e-5 A/m² for the matched direct-rate control. The current mismatch is now 1.0246× the direct-rate residual (1.0967× at 6,400; 1.4266× at 3,200). Shared-path Na gate error is 9.22e-9; source TABLE-on/off trajectory delta is 7.19e-6 mV RMSE. Doubling 6,400→12,800 lowers the shared-path gate error 4.00× and the trajectory delta 3.79×. Current identities remain closed at approximately 1e-13 A/m².

The current Rust implementation's trap0 helper already uses the correct v-th offset, analytic prefactor×slope limit, exp_m1 and asymptotic branches; its existing continuity unit test passed. No HumanJS code change was needed. Temporary corrected-K/12,800-node NMODL files and outputs remained outside Git. This remains a numerical counterfactual, not biological validation or a replacement for the author's 200-node baseline.


### 2026-11-13 — Human K activation trap0 regression

Added `human_potassium_activation_rate_is_continuous_at_both_trap0_voltage_landmarks` in `crates/humanjs-core/src/ion_channels.rs`. It compares HumanJS K activation tau with an independent `exp_m1)-based source-equation evaluation at the former wrong-sign guard (v=-theta), both guard edges, the true denominator singularity (v=theta), and nearby points. The tested discrepancy tolerance is 1e-12 ms. The targeted test and full Rust suite pass. No biological parameter or runtime implementation changed; this is a software regression only.

### 2026-11-13 — K activation source sweep and Rust regressions

An unchanged NEURON 9.0.2 K mechanism was evaluated at 441 voltages from -120 to +100 mV (0.5-mV spacing). Outside the tiny branch/limit regions, source activation tau matched the analytic equation within 9.77e-15 ms; steady states matched. The exact original false guard v=-theta causes an approximately -0.828-ms tau jump only inside +/-6.59041e-6 mV, while the true singularity v=theta returns NaN in NMODL instead of the 4.11000492924-ms analytic-limit tau.

Added two Rust tests: human_potassium_activation_rate_is_continuous_at_both_trap0_voltage_landmarks and human_potassium_activation_rates_match_source_equations_over_voltage_grid. They cover both singularity landmarks and 441 voltages after the explicit -10-mV channel shift. All 34 Rust unit tests pass; this remains software/source-equation verification, not biological validation.

### 2026-11-13 — K fast-inactivation trap0 regression

The original K NMODL fast-inactivation alpha and recovery beta rates exhibit the same wrong-sign guard defect. NEURON 9.0.2 returned negative tau_h1 at the alpha false guard (v=-thi1: source -0.0725058005 ms vs analytic 143.684108 ms) and beta false guard (v=-thi2: source -0.0132529631 ms vs analytic 12.2636432 ms). At the true denominator singularities v=thi1 and v=thi2, the original source returned NaN instead of analytic-limit tau values 22.0986469 and 360.921209 ms. The independent steady-state inactivation sigmoid remained correct.

Added Rust tests for all four landmarks and a 441-point -120 to +100 mV comparison of fast-inactivation tau and steady state with the independent source equation, applying the -10-mV channel shift explicitly. The 441-point unchanged-source sweep was finite and matched the analytic tau within 6.86e-13 ms. Full suite: 36 Rust unit, 3 synapse integration, 6 passive membrane integration and 22 Python tests passed. This is software/source-equation verification, not biological validation.


### 2026-11-13 — direct sodium trap0 rate probe

NEURON 9.0.2 direct calls to the unchanged human sodium `rates(v)` procedure confirm the same wrong-sign trap0 guard already identified in K. The three false guards occur at effective voltages +58.59235669 mV (m activation), +39.29867691 mV (h alpha) and +77.16674532 mV (h beta), with half-widths only 9.21455e-6, 7.21636e-6 and 4.74945e-6 mV. At those centres the source taus are 0.0256413, 0.0101590 and −0.00706676 ms; the analytic continuations are 0.0188446, 0.126201 and +0.0851694 ms. At the three true denominator singularities, direct NMODL rates return NaN rather than finite analytic-limit taus (0.119828, 1.37393 and 7.12695 ms).

The 441-point direct-rate sweep (−120…+100 mV, 0.5-mV spacing) avoids these microscopic windows and agrees with the analytic equations to below 6.3e-15 ms. The default 200-node TABLE path stays finite at all six landmarks and on the sweep; its maximum sweep interpolation errors are 3.55e-5 ms for m and 0.01984 ms for h. Thus the TABLE path masks the micro-window faults at these exact landmarks, but the underlying direct NMODL rate function remains defective. The original source hash and author TABLE baseline are preserved. Numerical/source analysis only; no biological validation.


### AP1 path check — sodium trap0 windows were not sampled

The matched original-source 250-ns AP1 run (both Na TABLE off/on, 116,001 samples, secondorder=1, 20-pA rheobase/30-pA pulse) did not enter any Na false-guard window or land exactly on a true singularity. The closest point was the h-alpha false guard: 0.00103467 mV away with TABLE off (143× guard half-width), and 0.0000882037 mV away with TABLE on (12.2×). The other two false guards were outside the trajectory's effective-voltage range. The nearest true singularity was h-beta, still 7.34e-6 normalized q away in the direct-rate path.

Therefore the direct sodium branch faults characterized at exact landmarks do not explain this specific AP1 voltage residual. The 200-node TABLE-on/off difference remains an independent interpolation/state-history effect (0.0288472 vs 0.00147738 mV voltage RMSE). This is only a path-specific check, not a guarantee for other stimuli or step sizes.

### Latest handoff — sodium regression pass (2026-11-13)

The HumanJS Rust sodium channel now has channel-specific regression coverage for the three wrong-sign guard windows and three true denominator singularities discovered in unchanged Wilbers `na_human.mod`. The 441-voltage grid test checks m/h kinetics and steady state against the independent continuous equation. CI is green on code commit `ed07cec9982622f9c3dcb8c0825c7951c3515442` (run 43425235022).

**Next concrete step:** audit temperature behavior as a complete contract rather than only checking one Q10 point. Add independent tests for sodium and potassium rate scaling and the different source conductance-temperature treatment across a small explicit temperature grid, while keeping channel parameters fixed. Continue to classify this as software/source-equation validation only. Raw human K kinetic targets and per-cell voltage-clamp traces remain unavailable in the inspected Dataverse v3.0 inventory; do not contact researchers and do not promote the provisional spike mechanism.

### Latest handoff — channel temperature contract regression (2026-11-13)

The current Rust implementation's temperature behavior is now tested at 20, 25, 30, 34 and 37°C. Na uses its 25°C reference; K uses its 34°C reference; each rate family uses Q10=2.3. Gate time constants scale inversely with `T_adj`, steady-state gates do not change, and the two K slow-gate branch constants remain fixed. The actual current-balance test verifies that Na conductance/current is multiplied by `T_adj`, while K conductance and passive leak are not. At the 34°C current-clamp condition, Na `T_adj = 2.3^0.9 ≈ 2.11619` and K `T_adj = 1.0`.

**Next concrete step:** keep the remaining ADR-014 gate explicit. The temperature regression proves that HumanJS applies the source's different Na/K Q10 placements; it does not validate this Q10 law biologically across the whole 20–37°C grid. Continue with a bounded source-protocol audit of the sodium voltage-clamp gates at the paper's 25°C and compare the existing Rust kinetics against the public human summary targets, clearly separating gate taus from current-fit apparent taus. Do not contact researchers, invent missing raw K data, or promote the single-compartment model.

### Latest handoff — Na voltage-clamp protocol and Figure 3 data audit

The pure Wilbers Na voltage-clamp gate paths are now explicitly replayed in Rust at 25°C with zero voltage shift. The Na_IV/Na_IV_ss test covers the 2-ms −120-mV hold and 19 test voltages (−80…+10 mV); the Na_IV_inact test covers a 1-ms −70-mV initial segment, 50-ms conditioning prepulse over −105…−47 mV and the first 5 ms of the −10-mV test segment. Both use independent `exp_m1` rate evaluations and analytic first-order gate updates.

The derived Figure 3 file `research/HUMAN-L23-WILBERS-FIG3-NA-IV-TAU-SUMMARY.csv` summarizes the released workbook's existing per-cell `iv_tau_m/h` fits using the official `RsComp`, exclude, GOF and voltage-range filters. It is validated by `experiments/validate_wilbers_na_iv_tau_summary.py`, wired into CI. These are composite/current-derived fitted fields rather than direct gate tau targets; the workbook 25-point grid (−65…+55 mV) is not the same as the model-side 19-point Na_IV protocol. The inspected Dataverse release still contains no raw NWB voltage-clamp traces, so no trace-level refit is possible from that release.

**Next concrete step:** inspect and independently replay the source Na_IV composite-current fitting path separately from the gate-only regressions. Keep its 50-µs delayed waveform and the source's asymmetrical tau output mapping explicit: `tau_m` is taken from the joint current-waveform fit, whereas the published helper retains the preliminary decay estimate for `tau_h`. Do not use the workbook IV taus as individual channel-gate targets and do not promote the model.

### Latest handoff — Na_IV composite-current fit replay (2026-11-13)

The source fitting path is now implemented in experiments/replay_wilbers_na_iv_current_fit.py. It simulates the pure human Na gates at 25°C under the deposited 2-ms −120-mV hold and 19 test voltages, derives a normalized inward current, runs the source preliminary exponential estimates, and fits the source 50-µs-delayed composite current equation with the deposited p0/bounds/R² rule. A 19-row derived table is preserved in research/HUMAN-L23-WILBERS-NA-IV-CURRENT-FIT-REPLAY.csv; experiments/validate_wilbers_na_iv_current_fit_replay.py verifies all recorded values against the runner and checks source provenance/caveats.

The R² criterion passes for −75…+10 mV and fails at −80 mV. The implementation deliberately does not claim the exact original source runner's accepted fit set because its absolute current selection threshold cannot be evaluated without the source calling cell's exact conductance/area amplitude. Returned apparent tau_m and tau_h remain current-fit parameters, not individual Markov/Hodgkin–Huxley gate taus. At −70 mV the gate time constants (≈0.225/22.03 ms), preliminary apparent current-fit values (≈0.386/24.98 ms), and joint fit values (≈0.364/49.96 ms) differ substantially; the source returns the joint tau_m but the preliminary tau_h.

**Next concrete step:** independently reconstruct the pure NMODL voltage-clamp absolute current scale and source-cell initialization so the I.min() < -1e-6 gate can be evaluated. Only then can we decide whether this normalized replay reproduces the full deposited Na_IV fitting selection. Do not use it as raw experimental validation and do not promote the single-compartment model.


### Latest handoff — original Wilbers sodium voltage-clamp source execution (2026-11-13)

The canonical NEURON runner is experiments/replay_wilbers_na_iv_neuron.py. It downloads, verifies byte counts and SHA-1 values, and compiles the original pure human na_human.mod unchanged. It executes the deposited Na_IV, Na_IV_inact and Na_recovery functions with NEURON 9.0.2, the source fitting caller's cell setup (10-µm diameter, default 100-µm length, Ra=200, cm=1, ena=141 mV, default gbar=40 pS/µm², vshift=0), and built-in VClamp defaults gain=100000, rstim=1 MΩ, tau1=0.001 ms, tau2=0 and fac=0. NEURON secondorder remains 0.0.

- Na_IV: 25°C; 2-ms −120-mV hold; 19 × 10-ms test commands −80…+10 mV in 5-mV steps at dt=0.01 ms. Source current-density selection passes 19/19; composite-fit R²>0.95 passes 17/19. At −70 mV the NEURON run's preliminary apparent taus are 0.400089/24.997752 ms and joint fit values are 0.386745/43.478711 ms; the returned source values are 0.386745 ms tau_m and preliminary 24.997752 ms tau_h.
- Na_IV_inact: 25°C and dt=0.005 ms; 1 ms at −70 mV, 30 conditioning steps −105…−47 mV, 50 ms each, then 10 ms at −10 mV. Source Boltzmann Vhalf/slope: −68.251977/8.472251 mV. The literal source denominator term +1e10 is preserved.
- Na_recovery: 25°C and dt=0.02 ms; 2 ms at −120 mV, 10 ms at 0 mV, 12 recovery intervals 1²…12² ms at 13 voltages −90…−66 mV, then a 2-ms test at 0 mV. All 156 paired-pulse traces are recorded, and 13/13 source apparent recovery tau fits are finite.

The three source-execution result records are tracked in the corresponding HUMAN-L23-WILBERS-NA-*-NEURON-REPLAY.csv files, with validators in experiments/. For Na_IV_inact and Na_recovery the strict source time masks are evaluated against the actual floating-point NEURON time vector; per-row sample count and first/last included timestamps are recorded. CI [43440747867](https://github.com/codexclai/HumanJS/actions/runs/43440747867) passed on exact code HEAD 82b361d5359574cb4f02dffdfc63d7cb95e2c1b5, including 31 Python tests and all three NEURON source protocol executions and recorded-result validators.

Limits: the inspected 65-file Dataverse v3.0 inventory has no raw human NWB voltage-clamp current traces. These runs reproduce original model/source code and its analysis functions; they do not compare to raw experimental recordings, establish biological validity, or clear ADR-014. The Rust single-compartment Na/K spike mechanism remains exploratory and unaccepted.

**Next concrete step:** inspect the original potassium voltage-clamp protocol path and determine which complete source routines can be faithfully executed and recorded using the deposited pure human K mechanism, preserving its known trap0 defects and clearly separating source execution from unavailable raw human K current data. Do not patch the original NMODL or invent missing kinetic target CSVs.


### Latest handoff — original human sodium and potassium voltage-clamp source execution (2026-11-13)

**Verified code state:** f6c567bc6bae159e21ee6f18fa688e537f9199f4; full GitHub Actions workflow [43452329852](https://github.com/codexclai/HumanJS/actions/runs/43452329852) passed on this exact commit. The public repository is main-only, with a 93-entry non-truncated tree, zero open issues and zero open pull requests.

The pure-human Na and K NMODL mechanisms have both now been compiled unchanged and executed with NEURON 9.0.2 and the original Dataverse `channel_tools.py` numerical protocol helpers. No original mechanism file or biological parameter was patched.

**Sodium source coverage:** Na_IV covers 19 test voltages (19/19 current-density selections, 17/19 joint-fit R² passes); Na_IV_inact covers 30 conditioning voltages (Vhalf/slope −68.251977/8.472251 mV); Na_recovery covers 156 paired pulses and yields 13/13 finite apparent recovery taus. The ideal-command Na_IV equation replay remains separate from the finite-feedback VClamp run.

**Potassium source coverage:** K_IV covers 34 voltages at 34°C, with 32/34 finite activation fits and 27/34 finite fast-inactivation fits. Source Boltzmann activation Vhalf/slope are −2.666291/14.516246 mV; inactivation Vhalf/slope are −50.891061/12.286798 mV. The fixed slow inactivation component is 450 ms. K_recovery covers 50 paired-pulse traces (five recovery voltages × ten delays) and all five voltages produce finite fast and slow source recovery-fit components. Result tables are `research/HUMAN-L23-WILBERS-K-IV-NEURON-REPLAY.csv` and `research/HUMAN-L23-WILBERS-K-RECOVERY-NEURON-REPLAY.csv`.

**Source correction and limitation:** the exact deposited `get_tau_inact_double_fixedtau2` has four free parameters and four `p0` values; `tau2` is fixed at 450 ms. The previous documentation's claim of a five-value `p0` and SciPy arity error was false and has been corrected. The K_IV fast-inactivation fitted tau is sensitive across repeated hosted runs: at −70 mV the preserved reference is 213.819 ms and the latest run returned 183.493 ms, while activation/current peak and steady-state Boltzmann quantities were unchanged. The output validator therefore verifies the source pass/availability state and parameter bounds, but does not claim exact repeatability of these nonlinear tau estimates. This sensitivity deserves a separate numerical investigation before using those estimates as stable kinetic targets.

**Limits:** the inspected 65-file Dataverse v3.0 inventory has no raw human K NWB voltage-clamp traces or individual K tau CSVs. The available NEURON executions reproduce the deposited model and source analysis software, not empirical raw-current refits or biological validity. The Figure S5 final plotting script is still not in the deposit. The HumanJS Na/K single-compartment spike mechanism remains exploratory and unaccepted under ADR-014. No outreach to authors/researchers is permitted or planned.

**Next concrete step when work resumes:** isolate the K_IV fast-inactivation optimizer sensitivity with repeated source runs and inspect fit conditioning, starting values and source acceptance rules; keep empirical K validation blocked until public per-cell/raw human data become available. 


### Latest handoff — original human potassium voltage-clamp source execution (2026-11-13)

Latest code HEAD before this documentation update: f6c567bc6bae159e21ee6f18fa688e537f9199f4; GitHub Actions [43452329852](https://github.com/codexclai/HumanJS/actions/runs/43452329852) passed on that exact main commit. The repo has 93 tracked entries, one branch (`main`), zero open issues and zero open PRs.

The original pure-human `k_human.mod`, Dataverse `channel_tools.py`, and `fit_k_hh_cma_human.py` were hash/size verified, the original NMODL compiled unchanged, and the K_IV/K_recovery numerical routines ran with NEURON 9.0.2/VClamp. K_IV completed 34 voltage commands with 32 finite activation fits and 27 finite fast-inactivation fits; Boltzmann activation Vhalf/slope −2.666291/14.516246 mV and inactivation −50.891061/12.286798 mV. K_recovery completed 50 paired-pulse traces; all five recovery voltages had finite fast and slow source fit outputs. Original result CSVs and the runner/test/validator are listed above and in `research/` and `experiments/`.

The earlier source-helper defect claim is retracted: exact `get_tau_inact_double_fixedtau2` has four free parameters, four starting values, and fixed `tau2=450 ms`. The final Figure S5 generator and raw human K data files remain absent. K_IV nonlinear fast-inactivation tau outputs showed repeat-run sensitivity (−70 mV: stored 213.819 ms, latest replay 183.493 ms), while current maxima and Boltzmann fits remained stable. The validator therefore checks fit acceptance/availability and source bounds but not exact equality of this nonlinear tau estimate. This is unresolved numerical sensitivity, not biological evidence.

No raw human K NWB recordings or individual K tau data CSVs were included in the inspected 65-file Dataverse release. No biological validation, raw-trace refit, human-only reparameterization, or acceptance of the exploratory spike model is claimed. No authors or researchers are to be contacted.

**Next work item if resumed:** investigate the K_IV fast-inactivation optimizer sensitivity under the pinned NEURON/NumPy/SciPy environment and preserve each independently reproduced fit outcome. Keep empirical K validation blocked until raw/per-cell human data are publicly available.


### Latest handoff — K_IV fast-inactivation optimizer/profile diagnosis (2026-11-13)

**Live repository snapshot:** main HEAD `85093a42d53d498be76c8eac12785b42f2a23db9`, complete 99-entry tree, exactly one branch (`main`), zero open issues and zero open PRs. The full code workflow [43458532278](https://github.com/codexclai/HumanJS/actions/runs/43458532278) passed on exact code HEAD `f2df2e2e27b5b53a97a84f7c6b472f503c8f504d`.

The K_IV source helper was verified directly again: it shifts `x` by subtracting `x[0]`, fits `a1*exp(-t/tau1) + a2*exp(-t/450 ms) + ss`, uses source `p0=((y0-yend)/2,(y0-yend)/2,30,y0/10)`, bounds `0 < tau1 <= 300 ms`, and accepts R²>0.95. Its second initial value is a current-density difference placed in the `tau1` slot; its default 30 is placed in the `a2` amplitude slot. At −70 mV those starts are 3.14164 × 10⁻⁵ ms and 30 mA/cm², the latter about 59,965 times the observed peak current density.

The integrated runner uses exactly the same post-peak samples and source time shift for six initializations at each of 32 fit-attempted voltages (192 fits total). At −70 mV, all six pass R²>0.95 but yield 186.610–213.819 ms; at −85 mV the maximum accepted within-voltage spread is 111.420 ms. The fixed-`tau1` profile puts the best point at the 300-ms source upper bound. An explicitly out-of-source-bound extension to 1200 ms found a coarse best grid point at 338.237 ms. An 801-point local profile (320–360 ms, about 0.05-ms spacing) refines this to 339.411255 ms, R² 0.999999577179 and RMSE 1.167677×10⁻⁸ mA/cm². The 1%-RMSE band spans 326 points from 331.461 to 347.706 ms. Across that band a1/a2 trade off with Pearson r = −0.99999896; ss varies by about 0.114%. These are descriptive correlations on one deterministic model-current profile, not statistical confidence intervals.

The exported residual waveform contains 4,890 samples at 0.1-ms spacing. Its RMSE is 1.167677×10⁻⁸ mA/cm²; the largest residual is at t=0 ms and the residual changes sign at 4.0 ms. First-10-ms RMSE is 7.80270×10⁻⁸, versus 3.28972×10⁻⁹ for the remaining 4,789 samples. Lag-1 correlation is 0.9284 overall and 0.9979 after 10 ms. These are smooth deterministic model residuals, not a measurement-noise analysis.

**Canonical records:** `research/HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md`; `research/HUMAN-L23-WILBERS-K-IV-FIT-START-DIAGNOSTICS.csv`; `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE.csv`; `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-EXTENDED.csv`; `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-LOCAL.csv`; `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv`. Implementation is in `experiments/wilbers_k_iv_fit_diagnostics.py`, integrated by `experiments/replay_wilbers_k_iv_neuron.py`; the related validators and tests are under `experiments/`, and CI runs them from `.github/workflows/repository-policy.yml`.

This resolves the optimizer-sensitivity audit only. These are fits/profiles of model-generated source currents, not raw experimental human current traces, microscopic gate taus, or biological validation. The inspected 65-file Dataverse release still lacks raw K NWB voltage-clamp currents and individual K kinetic CSVs. The HumanJS single-compartment spike model remains exploratory and unaccepted; ADR-014 remains open.

**Next concrete step:** evaluate one explicitly non-source three-component counterfactual aimed at the first 10 ms after the peak, then compare its improvement against the full-waveform objective and its effect on the other amplitudes. Keep the original helper, caller and NMODL unchanged.


### Residual waveform validation and transient localisation

The local-profile residual export was validated for 4,890 samples (NEURON time 30.9–519.8 ms; shifted source-fit time 0–488.9 ms). At the best local tau1 (339.41125497 ms), the fit coefficients are a1=6.00828885×10⁻⁵, a2=2.60772361×10⁻⁵ and ss=4.14437813×10⁻⁴ mA/cm²; the reconstructed RMSE and R² match the local profile. Residual RMSE is 7.80270×10⁻⁸ over the first 10 ms and 3.28972×10⁻⁹ over the remaining 4,789 samples. The initial residual is negative, crosses zero at 4.0 ms, and then remains much smaller. The lag-1 correlation is high (0.9284 overall, 0.9979 after 10 ms), as expected for a smooth deterministic residual. Do not interpret this as measurement noise.

An initial unit-test attempt demanded absolute synthetic residuals below 10⁻¹² mA/cm². That test was overstrict because the synthetic best tau is selected from a finite grid. It was corrected to compare the reconstructed residual RMSE with the profiled fit objective and check finiteness. The full subsequent CI run [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed.


## Latest handoff — non-source K_IV early-transient residual correction (2026-11-13)

The previous K_IV analysis localized the largest deterministic model-current residual to the first few milliseconds after the activation peak. This session added experiments/wilbers_k_iv_three_component.py, a standalone experiment that reads the tracked 4,890-sample HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv and chooses tau1 directly from the checked-in high-resolution local profile. It fixes the 450-ms source slow component and profiles a non-source third exponential over 801 tau3 points from 0.6 to 2.0 ms. All coefficients are optimized against the full waveform; the first-10-ms and later windows are diagnostics, not fitting weights.

The best signed correction is about 1.2335 ms with a negative coefficient of approximately −3.18×10⁻⁷ mA/cm² (0.064% of peak). Full RMSE improves by about 79.0%, first-10-ms RMSE by 94.0%, and post-10-ms RMSE by 27.6%. Original first/slow amplitudes shift only +0.37%/−0.93%; offset changes +0.0077%. A nonnegative extra-amplitude control at the signed optimum sets that term to zero and returns the two-exponential baseline. Interpret the added term strictly as a small signed correction to deterministic residual structure—not as a biological channel component or gating process. No raw human current trace is involved.

The original Dataverse channel_tools.py, fit_k_hh_cma_human.py, and k_human.mod were not modified. No Rust runtime or biological parameter changed. Three synthetic regression tests and the new source-provenance/data validator are integrated into the main CI workflow. Implementation commit: 46586e97695eae9b756e3d007b4daeb4069ae683; workflow [43466274672](https://github.com/codexclai/HumanJS/actions/runs/43466274672) passed on that exact commit.

**Next concrete step:** export the corresponding post-peak residuals for one or two adjacent K_IV command voltages from the same unchanged NEURON replay, then test whether the signed short-time correction generalizes across voltages under the same model form. Keep any resulting fit explicitly model-side; do not infer biological K-channel kinetics or accept the exploratory spike model without raw human evidence.


## Latest handoff — cross-voltage K_IV short-time residual correction (2026-11-13)

This session tested whether the non-source signed short-time correction previously observed at -70 mV persists at adjacent K_IV command voltages. The NEURON source runner now preserves the exact post-peak samples at -75, -70 and -65 mV, with both shifted fit-time and original NEURON clock. The analysis profiles long tau1 separately for each waveform, retaining the deposited fixed tau2=450 ms, then profiles a signed tau3 from 0.6 to 2.0 ms. All coefficients are refit against the complete waveform, not a first-10-ms-only fit.

Results: the signed extra term is negative at all three commands. Fitted tau3 progresses 1.111, 1.2335 and 1.384 ms for -75, -70 and -65 mV. Full-waveform RMSE reductions are 80.386%, 79.023% and 77.371%; the first 10 ms improve by 94.278%, 94.034% and 93.789%; the remainder after 10 ms improves by 27.728%, 27.614% and 27.433%. The negative extra coefficient is 0.0391%, 0.0636% and 0.1060% of peak current. A nonnegative-extra-amplitude control collapses to zero for each waveform at the signed optimum. Local tau1 is outside the deposited 0-300-ms bound for -75/-70 mV, so these long components remain non-source profile diagnostics.

Interpretation: the model-generated short-time residual correction generalizes across these three adjacent voltage commands with a smooth tau3 trend, but it is tiny, negative, and compensates deterministic fit residuals. It is not evidence for a positive current component, a microscopic gate, or a biological voltage-dependent inactivation time constant. No raw human current trace is involved, and the original source helper/caller/NMODL plus HumanJS Rust parameters remain unchanged.

Canonical result: research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv. Implementation and test paths: experiments/wilbers_k_iv_multivoltage.py, experiments/analyze_wilbers_k_iv_multivoltage.py, experiments/test_wilbers_k_iv_multivoltage.py, and experiments/validate_wilbers_k_iv_multivoltage.py, integrated with the post-peak export in experiments/replay_wilbers_k_iv_neuron.py. CI [43469283136](https://github.com/codexclai/HumanJS/actions/runs/43469283136) passed on exact code/data commit 5d5e180bc5068f647edc040de39481801be52a0e: 41 Rust unit tests, 3 synapse integration tests, 6 passive membrane integration tests, 43 Python tests, 28 experiment scripts parsed, all original Na/K source replays, all related validators and repository policy.

Next concrete step: extend the same signed-residual profile to a broader, predeclared subset of the K_IV voltage commands where the original source fit is attempted and finite. Record all failures and source-gate exclusions rather than selecting only voltages where the correction looks good. This will test whether the negative correction and tau3 trend persist beyond the three adjacent commands, while remaining strictly a model-output residual analysis. Raw human K voltage-clamp data are still absent; do not transfer any fitted exponential into Rust channel parameters or promote the exploratory spike model.


## Latest handoff — full finite-positive K_IV residual profile (2026-11-14)

### Verified repository state

- Canonical repository: `codexclai/HumanJS`; default branch and only branch: `main`.
- Code snapshot before this handoff documentation commit: `dff6fc6af7959a74263646f96ceb69e62fb725eb`; recursive tree: 111 entries, not truncated; zero open issues and zero open pull requests.
- GitHub Actions [43488672121](https://github.com/codexclai/HumanJS/actions/runs/43488672121) passed on exact code SHA `dff6fc6af7959a74263646f96ceb69e62fb725eb`. Verified steps include Rust formatting, Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 44 Python tests, source/experiment validators, all original Wilbers NEURON Na/K protocols, exact 27-row K_IV result comparison and repository policy.

### Work completed

Extended the source-model K_IV post-peak residual study from three adjacent voltages to the complete predeclared finite-positive source-fit command set. Source selection is exhaustive and predeclared from the original K_IV helper: 34 commands were run; the source current threshold passed at 32 (-100 through +55 mV); five attempted fast fits were non-finite (-100, -95, -90, -85 and -80 mV); and the remaining 27 commands (-75 through +55 mV) had finite positive source fast-fit estimates. The two threshold exclusions (-110 and -105 mV) and the five non-finite fit attempts are recorded separately and are not treated as missing-at-random samples.

The source runner now validates all three disjoint source outcome groups and exports exact NEURON/VClamp model-current samples only at the 27 finite-positive commands. The separate analysis profiles long tau1 and non-source signed short tau3, refitting coefficients across each complete waveform. The expected data file `research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv` records 27 rows × 39 columns and is compared field-by-field in CI. Research methods, decision follow-up, roadmap, status and boot records have been refreshed.

### Result interpretation

Across the 27 eligible model-generated waveforms, the signed non-source third-exponential coefficient was negative at all 27 commands; the nonnegative-amplitude control collapsed the extra term to zero at all 27 signed optima. Full-waveform RMSE reduction ranged from 55.467% to 80.386% (median 66.126%); first-10-ms reduction ranged from 75.608% to 94.278% (median 84.935%). After-10-ms RMSE improvement ranged from -41.467% to +27.728% (median +20.814%); the late-window error worsened at +25 through +55 mV (seven commands), despite lower full-waveform error at every command. The extra coefficient magnitude ranged from 0.0391% to 2.0965% of peak current.

The non-source tau3 optimum ranged from 0.6 to 2.0 ms (median 1.384 ms), with 11/27 profiles at one of the declared grid boundaries: 2.0 ms at -50 through -15 mV, and 0.6 ms at +45, +50 and +55 mV. Tau3 is not globally monotonic and these boundary outcomes are not interior estimates. Local tau1 ranged 17.195-393.404 ms; only -75 and -70 mV exceeded the deposited source helper's 300-ms upper bound. These findings describe a chosen numerical correction family on deterministic NEURON/VClamp model output, not human experimental current, a positive ionic component, a microscopic gate, or biological channel kinetics. The inspected DataverseNL v3.0 public inventory still lacks raw human K voltage-clamp NWB traces and individual K tau target CSVs. The deposited helper, caller, pure-human NMODL, and HumanJS runtime parameters were not changed; ADR-014 remains open.

The apparent direction/sign consistency should not be overread: the profile family itself is non-source, tau3 has 11 boundary outcomes, and its late-window residual worsens at seven depolarized commands. The test verifies computational repeatability of these deterministic model-current results, not biological fit. The raw human K voltage-clamp NWB data and per-cell kinetic targets remain unavailable in the inspected 65-file DataverseNL v3.0 release. No author or researcher was contacted. Do not change the deposited source helper, caller or NMODL; do not add the signed correction to Rust parameters or gate equations. ADR-014 remains open and the spike-capable one-compartment code remains exploratory and unaccepted.

### Changed paths in this continuation

- `.github/workflows/repository-policy.yml`
- `experiments/replay_wilbers_k_iv_neuron.py`
- `experiments/wilbers_k_iv_multivoltage.py`
- `experiments/analyze_wilbers_k_iv_multivoltage.py`
- `experiments/test_wilbers_k_iv_multivoltage.py`
- `experiments/validate_wilbers_k_iv_multivoltage.py`
- `research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv`
- `research/HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md`
- `docs/decisions/DECISIONS.md`
- `docs/roadmap/MASTER-ROADMAP.md`
- `docs/status/STATUS.md`
- `docs/status/SESSION-HANDOFF.md`
- `docs/BOOT.md`

### Commits and verification

- `2ba25af1fa1e1f745982b45ca5eac04edf2df165` — expand source replay/analysis/tests to all finite-positive source-fit voltages.
- `2368066b9602c846e527211d7d5d80ef0c6008c6` — correct waveform CSV test fixture newlines.
- `275c10fa649fdc7a9cb7a341f8d439f7f3474edc` — commit 27-row generated reference and research analysis.
- `dff6fc6af7959a74263646f96ceb69e62fb725eb` — preserve the correct multiline test fixture in the resulting Git tree.

Workflow [43488672121](https://github.com/codexclai/HumanJS/actions/runs/43488672121) passed on exact `dff6fc6`. In particular, CI reports the original K_IV replay ran 34/34 commands; source fast fits are finite at 27/34; the K_recovery replay ran 50/50 paired-pulse traces; 192/192 same-waveform multi-start fits converged; the 44 Python tests passed; the expanded 27-command signed-residual analysis matched the committed table exactly; the three-exponential diagnostic and repository policy passed. No local clone or local Rust/NEURON execution was performed in this session; those checks were run and verified on GitHub Actions.

### Next concrete step

Investigate tau3 boundary sensitivity using a broader, predeclared grid (for example 0.1–5 ms) across all 27 waveforms, with the full-waveform objective unchanged and early/late windows retained as diagnostics. Report boundary hits and where the after-10-ms residual worsens. This remains a model-current numerical exercise; do not convert it into biological channel kinetics or a Rust runtime change.


## Latest handoff — extended K_IV tau3 profile (2026-11-14)

### Verified repository state before documentation refresh

- Canonical repository: `codexclai/HumanJS`; default branch and only branch: `main`.
- Code/data HEAD: `8f4dc55bb0af0580b63e0bdac1c375b1d1df2e38`; complete recursive tree: 112 entries, not truncated; zero open issues and zero open pull requests.
- GitHub Actions [43492075297](https://github.com/codexclai/HumanJS/actions/runs/43492075297) passed on exact code/data SHA `8f4dc55bb0af0580b63e0bdac1c375b1d1df2e38`: 32/32 workflow steps succeeded.

### Work completed

Made the tau3 interval configurable through the multivoltage analyzer and validator. The default committed 0.6–2.0-ms output remains a distinct baseline reference; the workflow now additionally reruns the same 27 exact source-model waveforms over 0.1–5.0 ms at 2,801 points. The extended table is committed as `research/HUMAN-L23-WILBERS-K-IV-TAU3-EXTENDED-RESIDUAL-SUMMARY.csv` and CI compares all 42 columns across 27 rows against the regenerated output. Added synthetic coverage for a known short component outside the former interval and for explicit tau3 boundary-flag validation.

All 27 profile inputs remain the finite-positive fast-inactivation fits selected by the unchanged source routine: 34 commands were executed; the source current-selection threshold passed at 32 (-100 through +55 mV); five attempted fits (-100, -95, -90, -85 and -80 mV) returned non-finite fast taus; and the remaining 27 commands (-75 through +55 mV) returned finite positive values. The two threshold exclusions (-110 and -105 mV) and five non-finite attempts remain disjoint, explicitly recorded exclusions.

### Expanded-grid results and interpretation

All 27 selected tau3 values are now strictly interior to the expanded 0.1–5.0-ms grid: there are **zero tau3 boundary hits**, compared with 11/27 hits on the narrower 0.6–2.0-ms search. The fitted tau3 values span 0.49725–2.9805 ms (median 1.38275 ms) and are **not globally monotonic** with voltage; the largest selected value is 2.9805 ms at -30 mV.

The signed added amplitude remains negative at all 27 commands, and the nonnegative-amplitude control still collapses to zero at all 27 selected optima. Full-waveform RMSE reduction is 59.945–80.386% (median 66.126%); first-10-ms RMSE reduction is 82.625–94.280% (median 89.018%). After-10-ms RMSE reduction ranges from -35.719% to +27.726% (median +20.817%): the late-window error still worsens at +25 through +55 mV (seven commands), even though the full-waveform fit improves at all 27 commands. The absolute added-amplitude magnitude is 0.0391–1.8791% of peak current (median 1.5976%).

The expanded interval removes the earlier grid-boundary ambiguity for this particular discrete search, but it does not establish a biological time constant or a voltage-dependent kinetic law. The selected tau3 profile remains non-source and non-monotonic; the fit's full-waveform objective can trade late-window accuracy for a lower total residual, as reflected by the seven depolarized commands whose after-10-ms error increases. These currents are generated by the deposited pure-human model under NEURON 9.0.2/VClamp, not raw human experimental recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. Do not transfer tau3 or the signed term into Rust channel parameters or gate equations; the deposited helper, caller, NMODL and HumanJS runtime parameters remain unchanged. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The wider interval removes the earlier profile-boundary hits, but the result is still a non-source descriptive fit to deterministic model-generated current. The late-window mismatch remains visible and should not be hidden behind the full-waveform improvement. No raw human K-current recording or per-cell kinetic target was added; no researchers were contacted. The source fitting helper, caller and NMODL remain unchanged. No tau3 value or signed correction was transferred into Rust. ADR-014 remains open; the single-compartment spike-capable model remains exploratory and unaccepted.

### Changed paths in this continuation

- `.github/workflows/repository-policy.yml`
- `experiments/wilbers_k_iv_multivoltage.py`
- `experiments/analyze_wilbers_k_iv_multivoltage.py`
- `experiments/validate_wilbers_k_iv_multivoltage.py`
- `experiments/test_wilbers_k_iv_multivoltage.py`
- `research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv`
- `research/HUMAN-L23-WILBERS-K-IV-TAU3-EXTENDED-RESIDUAL-SUMMARY.csv`
- `research/HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md`
- `docs/decisions/DECISIONS.md`
- `docs/roadmap/MASTER-ROADMAP.md`
- `docs/status/STATUS.md`
- `docs/status/SESSION-HANDOFF.md`
- `docs/BOOT.md`

### Commits and verification

- `70e0af4826e34f350be7c78b81698e19fd29f42b` — parameterize the tau3 grid and add the broad-profile workflow/test.
- `590a638a9dafd430a120b75f5cf5e69323dd4fc9` — correct the synthetic recovery test to hold long tau1 fixed while recovering a known tau3.
- `18ae27dd6b44d4793e31a3060ad8b509fae2511b` — normalize stored baseline CSV Boolean tokens to the validator's established format.
- `8f4dc55bb0af0580b63e0bdac1c375b1d1df2e38` — commit the extended-grid expected CSV and restore strict field-by-field CI comparison.

Workflow [43492075297](https://github.com/codexclai/HumanJS/actions/runs/43492075297) passed on exact `8f4dc55`: 41 Rust core unit, 3 synapse integration and 6 passive-membrane integration tests; rustfmt/Clippy; syntax parsing for 28 Python experiment scripts; 46 Python tests; all original Wilbers Na/K NEURON source protocol replays and validators; strict comparison of both the baseline 0.6–2.0-ms and extended 0.1–5.0-ms result CSVs; three-exponential residual validator; and repository policy. No local clone or local Rust/NEURON execution was performed in this session; verification was performed in GitHub Actions.

Two intermediate workflow failures were diagnosed and corrected: an initial synthetic test allowed long tau1 to reprofile while demanding recovery of a known tau3, so the test was isolated to hold tau1 fixed; a generated CSV appended lowercase Boolean tokens, which were corrected to the validator's established `True/False` format. No scientific threshold or acceptance criterion was weakened.

### Next concrete step

Inspect the local *full-waveform* objective shape around each of the 27 interior tau3 minima, using the already declared 0.1–5-ms domain and the same fixed per-voltage tau1 solutions. Quantify local profile curvature/near-minimum flatness descriptively, retain full/early/late error partitions, and do not call the resulting width a statistical confidence interval or biological uncertainty. This will assess whether the now-interior values are numerically well-localized before any further mechanistic interpretation.
