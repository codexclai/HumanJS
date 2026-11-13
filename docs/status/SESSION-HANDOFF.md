# HumanJS — current session handoff

**Updated:** 2026-11-13
**Canonical repository:** `codexclai/HumanJS`, branch `main` only.
**Latest verified base before the K activation voltage-grid regression:** `8d0badddbafb4254b3837b72021a5c763d44bd1b` (former false guard/true singularity test; Actions run `43416217045` passed).
**Previous evidence availability cross-check:** `30dcee632b9ad5a64e4d6c1f496b9f00e03d3c64` (bounded public-archive search).
**Re-fetch the current main HEAD and newest workflow before relying on this handoff; the 441-point K activation equation regression is being recorded directly on main.**
Verify the live HEAD and newest workflow before relying on this handoff.

## Verified repository state at handoff

- Public repository; default branch `main`; live parent HEAD before this update: `8d0badddbafb4254b3837b72021a5c763d44bd1b`; recursive tree 75 entries, not truncated; exactly one branch (`main`); no open issues and no open pull requests.
- GitHub Actions run `43416217045` passed on that exact parent HEAD: https://github.com/codexclai/HumanJS/actions/runs/43416217045. It passed formatting, Clippy, Rust workspace tests, Python experiment syntax/unit tests, both Wilbers validators, and repository policy. Numerical source/model results are not biological validation.
- Fresh independent NEURON 9.0.2 `modlunit` invocation on unmodified `k_human.mod` and `k_mouse.mod` again failed at the untyped `trates(v+vshift)` call, line 82. Both species' repeated diagnostics are now recorded in `research/HUMAN-NEOCORTICAL-SPIKE-INITIATION.md`. The original files still compile with `nrnivmodl`; see ADR-014 for the temporary typed-probe findings. No source file was changed. The same research record clarifies that the article's public Dataverse data statement is satisfied by deposited summary/model files; it does not mean the missing per-cell K kinetic CSVs or raw voltage-clamp traces occur in the inspected 65-file v3.0 inventory.
- On a clean clone of the parent commit, `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, and `cargo test --workspace --locked` passed (31 unit tests, 3 synapse integration tests, 6 passive-membrane integration tests). All five experiment scripts parsed, both Wilbers validators passed, and repository policy passed. HumanJS 20-µs and 1-µs examples emitted the expected 1,450 and 29,000 post-step samples; the optional gate CSVs contain matching row counts.
- The NEURON 9.0.2 source baseline was independently rerun and the diagnostic passed end-to-end with pinned Python dependencies. Temporary counters recorded zero entries into the flawed `trap0` fallback; its instrumented and unmodified source traces were identical. The new gate comparison records five NMODL states and confirms that the biggest internal-state errors are in the fast gates during the AP upstroke.

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
