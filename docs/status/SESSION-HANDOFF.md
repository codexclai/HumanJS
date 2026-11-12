# HumanJS — current session handoff

**Updated:** 2026-11-12  
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.  
**Latest implementation/test change:** `adfacd7f8d3f8b6e7088a00507af4e51832a80d8` (paired mouse K+ current-fit tests added in `42c32ca69b7167076171f9b0adcda5ed11148dc8`, formatted in `78246ee3c810092605e145604740b3ca40953d28`, then accurately renamed in `adfacd7f8d3f8b6e7088a00507af4e51832a80d8`).  
**Latest research record:** `2c47917b407052c4cbe768ddda22ea08406c5462`.  
**Latest documentation baseline before this handoff update:** `8a31e626f5f7c70892dae93acee94b634e0f979e` (BOOT/status refreshed; research provenance reconciled).  
Verify the live HEAD and newest workflow before relying on this handoff.

## Verified repository state at handoff

- Public repository; default branch `main`; verified live HEAD immediately before this handoff update: `8a31e626f5f7c70892dae93acee94b634e0f979e`.
- Full recursive tree: 67 entries, not truncated. Live branch listing: exactly `main`. No open issues or pull requests.
- GitHub Actions run `43128214721` passed on exact HEAD `8a31e626f5f7c70892dae93acee94b634e0f979e`: https://github.com/codexclai/HumanJS/actions/runs/43128214721. The job passed Rust formatting, Clippy, workspace tests, Python experiment-runner syntax, the Figure S5 validator, the current-clamp grid validator, and repository policy. This run predates the handoff-file commit; verify that final commit's own workflow after updating this file.
- Fresh independent NEURON 9.0.2 `modlunit` invocation on unmodified `k_human.mod` and `k_mouse.mod` again failed at the untyped `trates(v+vshift)` call, line 82. Both species' repeated diagnostics are now recorded in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The original files still compile with `nrnivmodl`; see ADR-014 for the temporary typed-probe findings. No source file was changed. The same research record clarifies that the article's public Dataverse data statement is satisfied by deposited summary/model files; it does not mean the missing per-cell K kinetic CSVs or raw voltage-clamp traces occur in the inspected 65-file v3.0 inventory.
- No fresh local Rust test run is claimed; the Rust checks above were run in GitHub Actions.

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
- **Critical source-path defect:** deposited version-2 `channel_tools.py` (file 326242; SHA-1 `615595a270c6170987757cd35743f5d5b5b2af0e`) defines `get_tau_inact_double_fixedtau2` with four free fit parameters but supplies five values in its `curve_fit` initial vector. SciPy raises a parameter-count error; the helper catches it and returns NaNs. The inspected 65-file Dataverse v3.0 inventory contains no separate final Figure S5 plotting script. Therefore, the reconstructed J/K values and marker residuals are **not exact reproductions of the published red/blue J/K model lines**. The actual plotting path for those lines remains unresolved.
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

1. Make a targeted request to the Wilbers corresponding authors for the exact Figure S5 J/K/M/N plotting/export source state, the per-cell human K kinetic CSVs, and the raw K voltage-clamp recordings; ask for an explicit availability statement if these cannot be shared. The final published availability statement points to Dataverse, whose verified v3.0 manifest does not list these inputs.
2. Independently digitize model-line pixels in panels J/K/M/N from the official supplement when its page raster can be retrieved. Preserve these as raster-derived estimates distinct from measured group-mean markers, and do not present them as exact source fit outputs or substitutes for raw traces.
3. Keep human-only recovery parameters unresolved: the source's 236.824345-ms fast and 2789.7929-ms slow model constants are pooled human/mouse means, not human-only targets. Do not refit on raster points or infer that missing data were withheld.
4. Reassess the exploratory single-compartment spike model only after kinetic source, fit-objective, preparation-equivalence, and relevant human validation gates are independently satisfied. Keep AIS-resolved modeling separate; human NaV1.2/NaV1.6 immunostaining does not provide functional conductance densities or gating parameters.

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


### 2026-11-12 — corresponding-author contact verified; next action ready

- Queried the final publisher page for DOI 10.1126/sciadv.ade3300. It names Huibert D. Mansvelder (h.d.mansvelder@vu.nl) and Natalia A. Goriounova (n.a.goriounova@vu.nl) as corresponding authors.
- The publisher's data-availability statement points to Dataverse DOI 10.34894/L5J0SD. The previously audited released v3.0 manifest contains 65 files and does not list the K kinetic mean CSVs, data_fig5.xlsx, raw K voltage-clamp recordings, or a separate Figure S5 plotting/export script.
- A targeted request is now ready: ask for the exact J/K/M/N plotting/export code and parameter state; the missing per-cell human K activation/inactivation/recovery tables; raw K voltage-clamp recordings plus acquisition/protocol metadata if shareable; and an explicit availability statement for anything not retained or not distributable. Acknowledge the published Dataverse deposit and keep the tone neutral.
- **No email has been sent.** Contact discovery is not new experimental evidence and does not change the exploratory/unaccepted status of the Rust spike mechanism.
- Next: send the focused request only with the owner's authorization, then record any response and provenance. Independently digitize J/K/M/N model-line pixels as raster estimates only; do not substitute them for source code or raw recordings.


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
