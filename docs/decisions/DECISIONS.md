# HumanJS — decision record

**Decision authority:** project owner.  
**Updated:** 2026-11-14.

This is the canonical record of currently accepted decisions. Later explicit owner decisions may supersede these entries.

## ADR-001 — Project identity and scope

**Status:** Accepted · **Date:** 2026-11-10

- Name: HumanJS; lowercase identifier: humanjs; short identifier: ajs.
- Scope: computational human brain only.
- Not a chatbot, external-LLM wrapper, whole-body simulator, or claim of consciousness, sentience, subjective experience, or human equivalence.

## ADR-002 — Approved implementation stack

**Status:** Accepted · **Date:** 2026-11-10

Active implementation technologies are Rust, WGSL, Python, C, and C++. Rust is the native core; WGSL is for GPU compute; Python is the primary developer interface; C ABI and C++ provide interoperability. Node.js, JavaScript, TypeScript, npm, package.json distribution, and JavaScript runtimes are discontinued. No compatibility port is required.

## ADR-003 — GitHub is the sole source of truth

**Status:** Accepted · **Date:** 2026-11-10

The HumanJS GitHub repository, branch `main`, is the sole canonical source for current code, docs, requirements, decisions, research, experiments, issues, workflows, and history. Each ChatGPT session refreshes from live GitHub at startup. The ChatGPT Project Sources area may remain empty; no uploaded or separately synchronized project source is required. Releases, Packages, and Deployments are optional and used only when a real distribution or hosted-service need exists.

## ADR-004 — Public repository and Apache-2.0

**Status:** Accepted · **Date:** 2026-11-10

The repository is public and uses Apache License 2.0. Owner original contributions are attributed in `NOTICE`. Contributors retain copyright in their own contributions; the repository license governs redistribution and use. Public source cannot be made uncopyable through repository settings or a license.

## ADR-005 — Keep the working tree current and minimal

**Status:** Accepted · **Date:** 2026-11-10

The working tree contains current accepted requirements, architecture, source, reviewed research, reproducible experiments, tests, and necessary tooling. Do not maintain duplicate input bundles, retired project snapshots, unreviewed implementation dumps, or general-purpose backup trees. Git history provides the ordinary record of project and code changes. Promote research or experimental material only when relevant to a concrete task and after provenance, evidence quality, and redistribution review.

## ADR-006 — Data formats may be redesigned

**Status:** Accepted · **Date:** 2026-11-10

Former Node-specific persistence and API formats are not binding. Applicable inspectable brain/model/IR data should use JSON. Model definitions, initial conditions, live state, learned state, and checkpoints are distinct. Choose runtime persistence representation after correctness, safety, size, inspectability, and performance testing.

## ADR-007 — Retained runtime requirements

**Status:** Accepted · **Date:** 2026-11-10

Save/restore remains required. Native worker/multi-threaded execution remains required and must use Rust-native concurrency. A configurable default of 10,000 spiking neuron units remains required. Rate/mean-field units and state variables are counted separately. The default is an engineering choice, not a biological count or hard maximum.

## ADR-008 — Biological mechanisms, not software stand-ins

**Status:** Accepted · **Date:** 2026-11-10

Cognition and biological function must arise from causal, interacting, appropriately evidenced systems. Do not substitute fact/grammar tables, object-ID registries, goal slots, fixed switching timers, capped sequence tables, global scalar neuromodulators, or simplistic sensory transforms for biological mechanisms. Record uncertainty and evidence provenance.

## ADR-009 — Public-project safety and repository hygiene

**Status:** Accepted · **Date:** 2026-11-10

The repository is public. Keep credentials, secrets, private data, temporary output, duplicate snapshots, and unlicensed material out of the working tree and Git history. Use canonical paths for current research and experiments. Keep workflows read-only unless a specific write permission is necessary, pin external actions to reviewed immutable SHAs, and verify results.

## ADR-010 — Permanent main-only workflow

**Status:** Accepted · **Date:** 2026-11-10

`main` is the only branch to use permanently. Never create, check out, update, merge, or otherwise use another branch. Make authorized changes directly to `main`. Do not create project pull requests or branch-generating automation. Do not require or configure rulesets, branch protection, or branch-deletion-prevention settings. Force pushes are permitted but exceptional, inspected, and verified. Existing non-main refs are unused leftovers; inspect unique commits before deletion and report tool limitations honestly.

## ADR-011 — No unnecessary credential or environment infrastructure

**Status:** Accepted · **Date:** 2026-11-10

HumanJS has no requirement to store credentials, private user data, or secrets. Do not add authentication, secret-management systems, `.env`, `.env.example`, dotenv, or generic environment-file infrastructure without a specific approved product requirement.

## ADR-012 — First CPU mechanism is a bounded passive membrane patch

**Status:** Accepted · **Date:** 2026-11-10

Start the native Rust implementation with a single-compartment passive membrane patch. It solves the lumped RC equation for a piecewise-constant injected current using its analytic exponential solution. This establishes typed SI quantities, integer simulation time, separation of model parameters/initial conditions/live state, and testable CPU behavior without claiming a complete neuron.

No universal human parameter defaults are introduced. Where input resistance and membrane time constant are supplied, the model may derive lumped total leak conductance and capacitance through `G = 1/R` and `C = tau/R`. The effective zero-current equilibrium is a reduced-model operating point, not necessarily a measured single-channel reversal potential.

The initial slice omits active currents, synaptic transmission, dendritic cable structure, spike initiation, populations, networks, persistence, concurrency, Python/C/C++ bindings, JSON loading, and GPU execution. Numerical tests validate the declared equation and software implementation only; they are not biological validation.

## ADR-013 — First glutamatergic synapse is an evidence-bounded effective conductance model

**Status:** Accepted · **Date:** 2026-11-10

Implement the first excitatory synaptic component as an AMPA/NMDA conductance input to the existing passive membrane, scoped to adult human L2/L3 pyramidal-to-pyramidal cortical connections. Use receptor-specific normalized biexponential conductance waveforms, voltage-dependent NMDA magnesium unblock, and a deterministic short-term resource model using fitted connection-level utilization/recovery parameters.

The literature-derived AMPA/NMDA waveform and peak-conductance parameters are fitted/effective parameters, not direct measurements of molecular receptor transition rates at an individual synapse. The short-term-depression utilization and recovery parameters are fitted to human paired-recording responses; applying connection-level dynamics to one effective contact is an explicit computational reduction. Keep these parameters explicit in model construction and evidence records; do not use them as universal defaults.

The first implementation deliberately excludes stochastic vesicle fusion, explicit presynaptic calcium/docking/release-site machinery, synaptic-cleft glutamate dynamics and uptake, molecular receptor Markov/desensitization states, dendritic spines/cable morphology, and inhibitory synapses. It integrates interval-mean synaptic conductances and evaluates NMDA magnesium unblock at an estimated midpoint voltage. Software tests support only these computational equations and interfaces; they do not establish biological validation.


## ADR-014 — Intrinsic spike initiation is evidence-gated and soma/AIS scopes remain distinct

**Status:** Accepted · **Date:** 2026-11-10

Do not add a threshold-only spike generator or generic rodent Hodgkin–Huxley mechanism and label it a human cortical neuron. The first possible spike-generation increment is a clearly named human somatic nucleated-patch equivalent. It must preserve the distinction between direct human somatic measurements, fitted model conductances, and transferred gating functions. It must not claim anatomical AIS resolution, dendritic propagation, or intact whole-neuron behavior.

An anatomical soma/AIS model is a separate milestone. Human NaV1.2/NaV1.6 immunolocalization constrains subtype location qualitatively but does not supply absolute functional channel density or gating kinetics. Do not convert staining intensity or peak position into conductance parameters.

The pure human \`na_human.mod\` and \`k_human.mod\` files were retrieved from the CC0 DataverseNL deposit and compiled unchanged with NEURON 9.0.2. Both explicitly set Rb equal to Ra. Direct calls at exact stored \`trap0\` singularities return non-finite values. The active Na+ 200-node lookup table over −120 to +100 mV produced finite activation/inactivation time constants at every grid node; disabling that table exposes non-finite exact-singularity rates. The K+ mechanism has no active rate table; exact singularities are non-finite and two opposite-sign branch triggers produce negative inactivation time constants. These are source/runtime issues, not license to silently patch the original and call it exact reproduction.

The K+ mechanism file matches Table S2 and the first optimizer result. Inspection of the deposited script shows that its later alternate dictionary is a bare literal never applied; the executed fitting sequence applies the first optimizer result. The script assigns `h12factor_k_human`, but all three inspected pure/hybrid K+ NMODL variants contain only a commented-out `h2tau = h1tau * h12factor` line, with no active declaration or use; the deposited protocol helper also does not read the Python attribute. The article's 14-parameter description is broader than the deposited optimizer sequence: two inactivation steady-state values are assigned from experimental fits and `Rb` is constrained equal to `Ra`, leaving 11 optimizer variables. The pure Na+/K+ NMODL files declare rate prefactors as `/ms`, but the active `trap0` equation multiplies them by a voltage numerator and therefore requires `mV^-1 ms^-1` for a rate output in `ms^-1`. NEURON 9.0.2 `modlunit` on each unmodified file stops earlier at the untyped `trates(v+vshift)` call (K line 82; Na line 80). Temporary typed diagnostic copies expose the prefactor mismatch, the dimensionally invalid fallback (which omits the prefactor), the wrong-sign branch predicate (`v+th` versus the denominator's `v-th` singularity), the missing temperature unit in the Q10 exponent, and omitted units on activation midpoint/slope parameters. With equation-consistent annotations and the commented-out `a*q` limit, temporary K/Na copies pass `modlunit`; the original deposited files remain unchanged. `nrnivmodl` compiles both original files but emits a non-thread-safe GLOBAL `tadj` assignment warning. HumanJS retains the source numeric prefactors but uses the equation-consistent internal unit and a stable analytic limit; this is an explicit correction, not exact NMODL reproduction. A Rust-side K_IV_ss replay now compares activation/inactivation half-range crossings and availability at −80 mV with published group means; all are within the reported human SD. The public deposit still lacks the exact K tau CSV targets and raw K voltage-clamp traces, so kinetic refitting and raw-trace reproduction remain outstanding.

The original Eyal et al. ModelDB archive was retrieved and audited. HOC templates for all six cells map directly to Table S4. The six Figure 7A spike models insert nine conductance mechanisms (NaTg, Nap_Et2, K_Tst, K_Pst, SKv3_1, Ca, Ca_LVAst, SK_E2, Im) plus CaDynamics_E2 in soma and a two-section 60 μm axon stub; dendrites are passive. Ca_HVA is present in the archive but is not inserted in these six HOC spike models; NMDA.mod is used by separate synaptic workflows. Table S4's 29 parameters are fitted values, not direct human channel-density measurements. The models assume rodent-like gating kinetics.

The ten mechanisms actually inserted by the six HOC templates were compiled with NEURON 9.0.2. A Python 3 reproduction followed the Figure 7A construction and selected stimulus protocol for all six cells and compared first-spike metrics against released human current-clamp repetitions. Results and the checked-in runner are documented in \`experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md\`. This verifies canonical source mapping and selected model execution; it is not an independent refit, exact trace match, or biological validation.

**Implementation gate:** no intrinsic spike-generating code is accepted as a scientifically defensible HumanJS mechanism until the deposited source equations, fit constraints, dimensional conventions, and temperature behavior are independently reproduced and a numerically stable human somatic-patch model is validated against human voltage-clamp targets. Keep it separate from an anatomical soma/AIS model. No AIS conductance may be inferred from immunostaining. Keep transferred kinetics distinct from human-fit conductances. Exploratory spike-capable code was subsequently added; ADR-016 records that it does not satisfy this gate and must remain explicitly provisional. No biological validation is claimed.

### ADR-014 follow-up — Na TABLE refinement exposes the K trap0 wrong-sign branch (2026-11-13)

A controlled 250-ns counterfactual changed only the temporary pure-human Na NMODL TABLE size from 200 to 400, 800 and 1,600 nodes, while holding the original 20-pA rheobase, 30-pA AP1 stimulus, channel densities and secondorder=1 fixed. Same-voltage Na gate interpolation error and the coupled source TABLE-on/off voltage perturbation each fell approximately quadratically with grid spacing across these accepted variants. The source-table interpolation is therefore a material numerical component of the 200-node TABLE-on residual; it is not a biological parameter discrepancy. The original 200-node source baseline is preserved.

A 3,200-node TABLE-on counterfactual is not accepted: its source voltage path reaches the known K activation trap0 wrong-sign guard at approximately 4.402 ms. The effective K activation voltage is 29.961796 mV, essentially the negative of the source activation midpoint parameter (tha = -29.961798 mV); the source condition tests fabs((v+th)/q), although the denominator singularity is at v-th. The predicate therefore enters the defective fallback while the denominator is far from zero. An independent same-voltage CNEXP replay records a 0.001385 gate-fraction maximum error in K activation and fails its 1e-4 recurrence check. A TABLE-off-only control with the same 3,200-node compiled library passes and reproduces the earlier direct-rate reference. This identifies a coupled interaction between a higher-resolution sodium-table trajectory and the pre-existing K source branch defect; it does not justify silently patching the deposited source or altering HumanJS parameters. The original source files and their checksums remain unchanged. Detailed methods/results are in the Wilbers experiment record and human spike-initiation research note.


### ADR-014 follow-up — direct K trap0 branch discontinuity measured (2026-11-13)

A targeted NEURON 9.0.2 probe of the unchanged deposited K mechanism at 34°C confirms that its wrong-sign trap0 guard is discontinuous near v=-tha, not at the denominator singularity v=tha. For the K activation parameters tha=-29.9617980169 mV, qa=6.59040568888 mV and Ra=Rb=0.0184592505854/ms, the source predicate switches branches within ±6.59041e-6 mV of the opposite-polarity point. At the trigger, the source produces a=36.552210 and b=-23.371390, whereas the same source numerator/denominator formula evaluated away from its true singularity gives a=1.106272 and b=+0.000124457. The resulting source mtau is 0.075867814 ms rather than 0.903835007 ms; minf remains 0.925478206. Thus the faulty branch reverses the sign of one component and shortens the activation time constant by 11.91-fold. See the 2026-11-13 direct-rate probe in the canonical Wilbers experiment/research records. Original NMODL files and HumanJS parameters remain unchanged.


### ADR-014 follow-up — 3,200/6,400-node table counterfactual and K trap0 continuity (2026-11-13)

The deposited K activation expression has a wrong-sign small-argument guard: the denominator is singular at v=th, but the source tests v+th. At the 3,200-node Na-table AP1 trajectory this enters the fallback at 4.402 ms with fabs((v+th)/q)=2.37e-7 while fabs((v-th)/q)=9.09255. The original-source independent K-gate replay error is 0.00138525. A temporary, non-committed mathematical control changed only that guard to v-th and the limiting expression to a*q. With that control, the same 3,200-node run passes the existing gate check and a 6,400-node run also passes. The source TABLE-on/off voltage perturbation and shared-voltage Na gate interpolation error each drop approximately fourfold when the grid doubles 3,200→6,400; the direct-rate control remains unchanged. This isolates the interaction between the Na-table-driven voltage path and the K trap0 branch defect. It does not authorize patching the published mechanism or changing HumanJS biological parameters. See the 2026-11-13 high-resolution extension in the canonical Wilbers experiment and spike-initiation research records for source hashes, fixed protocol, current balances and numerical limits.


### ADR-014 follow-up — HumanJS Rust trap0 is already continuous; Na-table residual approaches the direct-rate floor (2026-11-13)

A 12,800-node sodium-table extension of the temporary corrected-K AP1 comparison reduced the actual source TABLE-on/off trajectory difference to 7.185e-6 mV RMSE and the shared-path Na gate interpolation residual to 9.219e-9. The TABLE-on evolved current RMSE (1.78514e-5 A/m²) is within 2.46% of the matched direct-rate control (1.74232e-5 A/m²). Doubling from 6,400 to 12,800 nodes reduced the shared-path gate error 4.00-fold and the coupled voltage-trajectory difference 3.79-fold.

The same investigation checked crates/humanjs-core/src/ion_channels.rs: HumanJS computes the rate from voltage minus half-voltage, uses a small-x analytic series and exp_m1/asymptotic branches, and applies the prefactor×slope limit. The existing trap0_uses_the_analytic_limit_and_is_continuous unit test passed. Thus the wrong-sign small-argument guard is specific to the deposited Wilbers NMODL reference; the current Rust helper already uses the mathematically continuous formulation. No HumanJS source change is warranted by this source-only numerical counterfactual. Detailed protocol, hashes and residual limits are recorded in the canonical experiment and research notes.


### ADR-014 follow-up — sodium trap0 false guards and TABLE masking (2026-11-13)

The unchanged pure-human `na_human.mod` has the same false-guard predicate and incorrect fallback structure as the K mechanism. In direct NEURON 9.0.2 rate calls, the m activation, h alpha and h beta paths produce discontinuous or negative time constants at the false guards, and NaN at their true denominator singularities. Their analytically continued taus remain finite. The deposited 200-node Na TABLE path avoids these microvolt-scale samples and returns finite interpolated values, with bounded but nonzero interpolation error over an ordinary voltage grid. Therefore direct-rate and default TABLE execution must be distinguished when interpreting numerical source reproductions. The original Na source remains unchanged; detailed values and method are in the 2026-11-13 sodium probe records.


### ADR-014 follow-up — AP1 does not enter the narrow Na trap0 windows (2026-11-13)

The matched original-source 250-ns AP1 trajectories with Na TABLE off and on did not enter any of the Na false-guard windows or land exactly on a true singularity. The closest false guard was h-alpha: the direct-rate sample remained 0.00103467 mV from its centre (143 times its microvolt-scale half-width), while the TABLE path remained 0.0000882037 mV away (12.2 times the half-width). The other false guards were outside this AP1 path's effective-voltage range. Therefore, do not attribute the AP1 TABLE-on/off voltage residual to a Na false-guard activation. The result is stimulus/step-specific and does not generalize to all possible voltage paths. See the detailed 2026-11-13 trajectory check in the canonical experiment and spike-initiation records.


## ADR-015 — Published-model reproduction is evidence, not HumanJS implementation

**Status:** Accepted · **Date:** 2026-11-11

The canonical Eyal et al. 2018 ModelDB archive may be used in a separately documented experiment to verify original source availability, parameter mapping, compilation and selected model behavior. Such an experiment must identify archive integrity, execution environment, model configuration, stimulus, comparison metric, released data, deviations and limitations. External model execution does not implement an AP mechanism in the HumanJS Rust core, does not validate HumanJS biologically, and does not establish whole-brain functionality. Do not copy the external model wholesale into HumanJS or silently describe transferred rodent kinetics as human measurements.


## ADR-016 — Exploratory human L2/L3 single-compartment spike code remains unaccepted

**Status:** Accepted classification and corrective action · **Date:** 2026-11-11

The Rust core now contains `HumanL23SingleCompartmentModel` in `crates/humanjs-core/src/ion_channels.rs`. It is capable of generating an action potential in a specified current-clamp software fixture. This code was added before the evidence gate in ADR-014 had been closed. Its existence must be documented accurately, but its presence does not waive or retroactively satisfy that gate.

Classify the implementation as **exploratory and not scientifically accepted** until the remaining source and validation questions are resolved. It uses human Na+ gate parameters from the pure Wilbers source, K+ parameters matching the pure mechanism and Table S2 / first optimizer result, and current-clamp fitted conductance densities and setup. The latter are fitted against cross-species mean AP features, not direct human channel-density measurements. The Rust `trap0` uses the analytic mathematical limit rather than reproducing the source's defective branch behavior. The selected K+ inactivation set matches the parameters actually applied by the deposited script. A Rust model-side K_IV_ss replay now covers the deposited steady-state voltage grid and its activation/inactivation half-range crossings and −80-mV availability fall within the published human group mean ± SD. This remains a coarse summary check: the exact K+ kinetic CSV targets and raw voltage-clamp traces are absent, so fast/slow time-constant reproduction remains outstanding. The article's 14-parameter description versus the deposited 11-variable optimizer sequence is now explained by fixed experimental inactivation steady states and `Rb = Ra`, though independent protocol reproduction remains outstanding. The article Discussion also acknowledges that its HH models do not accurately reproduce all potassium-channel properties, especially K+ inactivation, and that this likely contributes to poor fits of K+ currents and AP falling speeds (Wilbers et al., 2023, https://doi.org/10.1126/sciadv.ade3300).

Do not remove or extend this exploratory mechanism merely to make the documentation appear consistent. First complete the evidence audit, unit/temperature review, voltage-clamp comparisons, current-clamp setup review, and independent regression tests recorded in the architecture and research documents. Keep all claims limited to software-level behavior until evidence-based validation is complete. The model is one lumped compartment and is not an anatomical soma/AIS neuron, full pyramidal neuron, or biological validation result.


### ADR-016 follow-up — current-clamp conductance source mapping (2026-11-12)

The current-clamp conductance values are no longer provenance-ambiguous. The unrestricted Dataverse v3.0 files `AP1comparison.csv`, `gbar_na.csv`, `gbar_k.csv`, and the complete `cc_tools.py` helper were retrieved and SHA-1 verified. The exact all-human-kinetics (Na ratio=1, K ratio=1) endpoint is 114.47654963753565 pS/μm² Na and 29.045736151752504 pS/μm² K, matching the Rust preset after rounding. However, the optimizer's three AP targets remain the 50:50 human/mouse median values. The preset is therefore an all-human kinetic mixture fitted to cross-species midpoint AP features—not a human-only AP fit and not a direct measurement of human channel density. This resolves the conductance preset's source-table provenance but does not pass ADR-014's broader spike-mechanism scientific acceptance gate. The original NEURON/SciPy optimizer was not rerun in the available environment; the deposited grid outputs were verified instead.


## ADR-017 — Pre-migration JavaScript archive is reference-only

**Status:** Accepted · **Date:** 2026-11-12

The owner supplied a historical `HumanJSProject.zip` for a one-time migration-loss audit. Its SHA-256 is `0deb7789a8df444ea6a4e957dc63520cf6e786c18887286c3a31a319f61eccdf`; the inspected archive contains 422 ZIP entries (375 files; 26,045,082 uncompressed bytes). It includes the former JavaScript/Node.js runtime, 16 files under `src/`, 28 architecture notes, 143 experiment documents, 92 raw simulator-result JSON files, three test files, extensive scientific research notes, and historical requirements/decision/handoff records.

The archive is a historical reference, not a current implementation baseline or dependency. The owner has confirmed that the archive itself is to remain outside the public repository. Do not copy the ZIP, duplicate its source tree, import its Node.js/JavaScript implementation, restore npm packaging, or treat its old simulator outputs as current HumanJS results. These directions are already superseded by the current Rust/WGSL/Python/C/C++ architecture and the main-only GitHub source-of-truth policy.

Useful information is to be recovered selectively, with provenance and scientific limits:
- historical human-evidence citations and anatomy reviews may seed new research only after the primary source and current relevance are rechecked;
- experiment protocols may inform new Rust experiments, but old JavaScript simulator outcomes are software-history evidence only and must be independently reproduced before reuse;
- old requirements/prompts that conflict with current accepted requirements remain historical and do not override them;
- failed, rejected, and incomplete experiments are useful as design warnings, not evidence of biological behavior.

This audit was a structural and documentation triage, not a line-by-line scientific revalidation of all 715-kB research material or all legacy source files. No legacy source, raw result, or unverified citation was imported. The ZIP is not required for future sessions: this decision and the triage findings are recorded in current GitHub documentation. If a specific historical file becomes necessary later, request only that file or relevant source material rather than making the archive a standing dependency.


### ADR-017 follow-up — archived material and current evidence separation

The one-time archive inventory identified 92 raw JSON result files from the discontinued JavaScript simulator and a 715-kB scientific information dossier with a 374-entry reference register. Neither was copied wholesale. The former results are not outputs from the current Rust implementation; the latter contains a mixture of human, animal, model, atlas, tractography, and engineering evidence that must be rechecked source-by-source before reuse. The archive's experiment protocols and rejected/failed findings may be useful as historical leads, but only after independent implementation and preregistered reproduction in the current Rust core. This follow-up does not expand ADR-017's original scope: no line-by-line scientific audit of the full dossier has been completed.


### ADR-014 follow-up — original human sodium voltage-clamp source execution (2026-11-13)

The original pure-human sodium source mechanism and its deposited calling/helper code have now been executed as an end-to-end voltage-clamp software reproduction. The runner verifies the official DataverseNL v3.0 source byte counts/SHA-1 identities for channel_tools.py (file 326242), na_human.mod (file 318629) and fit_na_hh_cma_human.py (file 326238), compiles the unmodified NMODL in NEURON 9.0.2, and creates the source fitting section with diameter 10 µm, NEURON-default length 100 µm, Ra=200, cm=1, ena=141 mV and default gbar=40 pS/µm². Built-in VClamp defaults were read and retained: gain=100000, rstim=1 MΩ, tau1=0.001 ms, tau2=0 and fac=0.

The original Na_IV, Na_IV_inact and Na_recovery routines in channel_tools.py were executed. The Na_IV current-density selection gate passes 19/19 test voltages and 17/19 pass the source composite-fit R²>0.95 criterion. The source output asymmetry (joint-fit tau_m, preliminary decay tau_h) is retained. Na_IV_inact yields 30 conditioning points and a source Boltzmann Vhalf/slope of −68.251977/8.472251 mV while preserving the literal denominator. Na_recovery produces 156 paired-pulse traces and 13 finite source apparent-recovery tau fits. NEURON time-window masks are compared using actual recorded floating timestamps; row-level first/last samples and counts are preserved.

The three CSV records and protocol validators are tracked in the HUMAN-L23-WILBERS-NA-IV-NEURON-REPLAY, HUMAN-L23-WILBERS-NA-IV-INACT-NEURON-REPLAY and HUMAN-L23-WILBERS-NA-RECOVERY-NEURON-REPLAY research records and corresponding experiments validators. GitHub Actions [43440747867](https://github.com/codexclai/HumanJS/actions/runs/43440747867) passed on exact source HEAD 82b361d5359574cb4f02dffdfc63d7cb95e2c1b5: source execution and all three recorded-result checks, along with the full Rust/Python/repository-policy workflow.

These are source/model execution results only. The inspected 65-file Dataverse v3.0 listing contains no raw human NWB voltage-clamp current traces, so empirical raw-current refitting and human-target comparison remain incomplete. This follow-up does not modify original NMODL, add biological parameters, validate the Rust single-compartment spike model, or close the ADR-014 acceptance gate. The exploratory spike-capable implementation remains unaccepted.


### ADR-014 follow-up — original human potassium voltage-clamp source execution and K-fit audit correction (2026-11-13)

The pure human `k_human.mod` mechanism, original Dataverse `channel_tools.py`, and human fitting caller `fit_k_hh_cma_human.py` were size/SHA-1 verified and executed with NEURON 9.0.2. The runner reconstructs the source caller's section and parameter overrides, uses the built-in VClamp defaults, retains 34°C and the deposited time steps, and invokes the source K_IV and K_recovery numerical protocols without modifying the NMODL.

K_IV produced 34 command rows; 32 activation fits and 27 fast-inactivation fits were finite. The source Boltzmann fits returned activation Vhalf/slope −2.666291/14.516246 mV and inactivation Vhalf/slope −50.891061/12.286798 mV. K_recovery produced 50 paired-pulse runs (five recovery voltages × ten delays), with finite fast and slow source double-exponential current-fit outputs for all five voltage conditions. The original per-run current windows and timestamp boundaries are preserved in the result records.

**Correction to the previous audit:** exact DataverseNL v3.0 `channel_tools.py` (file 326242, SHA-1 `615595a270c6170987757cd35743f5d5b5b2af0e`) defines `get_tau_inact_double_fixedtau2` with four free curve-fit parameters (`a1, tau1, a2, ss`) and exactly four initial values in `p0`. Its second time constant `tau2` is a fixed argument, default 450 ms. The earlier statement that a five-element initial vector caused SciPy's parameter-count error and NaN results was incorrect; the actual source helper executes. The lack of a separate final Figure S5 plotting script and the missing empirical K tau CSV/raw K NWB files remain separate evidence gaps.

A repeat CI execution exposed optimizer sensitivity in the K_IV fast-inactivation fit. At −70 mV, the stored run returned 213.819 ms and the latest successful replay returned 183.493 ms, while the waveform current maxima, conductance estimates, normalized steady-state curves and Boltzmann fit outputs matched. The current validator checks fit availability, source acceptance, and the documented parameter bounds rather than claiming exact nonlinear fit-tau reproducibility. This issue remains open for numerical investigation and these estimates must not be treated as stable human experimental targets.

The exact K source-execution results and validators are `HUMAN-L23-WILBERS-K-IV-NEURON-REPLAY.csv`, `HUMAN-L23-WILBERS-K-RECOVERY-NEURON-REPLAY.csv`, and the paired runner/test/validator in `experiments/`. GitHub Actions [43452329852](https://github.com/codexclai/HumanJS/actions/runs/43452329852) passed on exact source HEAD f6c567bc6bae159e21ee6f18fa688e537f9199f4: the full Rust, Python, scientific-data, Na/K NEURON source replay, and repository-policy workflow.

This execution establishes only that the deposited model and analysis code run for the selected source protocols. It does not fit raw human K current traces, resolve pooled human/mouse recovery parameters as human-only values, establish biological validity, or close ADR-014. The HumanJS spike-capable model remains exploratory and unaccepted.


### ADR-014 follow-up — K_IV optimizer initialization and profile diagnosis (2026-11-13)

The repeat-run K_IV sensitivity has now been isolated on the exact same post-peak NEURON waveform. The deposited helper's four-value initial vector is not an arity error, but its argument order and scale are questionable: with model parameter order `(a1, tau1, a2, ss)`, it seeds `tau1` with half a current-density difference and places the default `est1=30` in the `a2` amplitude slot. At −70 mV, this yields an initial `tau1` of 3.14164 × 10⁻⁵ ms and an `a2` amplitude of 30 mA/cm², approximately 59,965 times the observed activation-current peak. The exact source also shifts the input time vector by `x=x-x[0]`; this behavior is retained by the counterfactual runner.

Six same-waveform initializations across 32 attempted voltages produced 192 converged fits. At −70 mV all six pass R² > 0.95, yet \(\tau_1\) ranges from 186.6098 to 213.8193 ms. At −85 mV the largest within-voltage accepted spread is 111.4199 ms. This is direct numerical evidence of initialization-sensitive accepted fits, not a biological effect.

The fixed-`tau1` nonnegative linear least-squares profile finds its best sampled point at the source upper bound (300 ms) when restricted to the original 0.05–300-ms domain. An extended 0.05–1200-ms counterfactual profile places its coarse best sampled point at 338.2372 ms, outside the source bounds. An 801-point local profile over 320–360 ms refines this to 339.411255 ms (R² 0.999999577179; RMSE 1.167677×10⁻⁸ mA/cm²); 326 points lie within 1% of its minimum RMSE, from 331.461 to 347.706 ms. Across that band, r(`a1`,`a2`) = −0.99999896 while `ss` varies by 0.114%. These are descriptive correlations across one deterministic model-current profile, not parameter covariance. The original source-literal fit's RMSE is 3.59× the best local-profile RMSE on the same waveform, but the local minimum remains outside the source's 300-ms limit. The original `channel_tools.py`, caller, and `k_human.mod` remain unchanged.

The source identities, methods, profile results and residual series are in `research/HUMAN-L23-WILBERS-K-IV-FIT-SENSITIVITY.md` and the five `HUMAN-L23-WILBERS-K-IV-FIT-*.csv` tables. The 4,890-sample residual record localises most of the fit discrepancy to the first 10 ms after the peak: its RMSE is 7.80×10⁻⁸ mA/cm² there and 3.29×10⁻⁹ thereafter. The sequence is strongly temporally correlated and is a deterministic model residual, not empirical noise. The original helper and NMODL remain unchanged. GitHub Actions [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed on exact code HEAD `55d469485edb00a9d65c105645f58b9bb1a92a39`, including all Rust/Python tests, original Na/K NEURON source replays, fit-start diagnostics, all three profile grids, residual export and validation, and repository policy.

This closes only the numerical source-fit sensitivity audit. The raw human K trace refit remains blocked by absent NWB recordings and individual K kinetic CSVs; no biological validation is claimed and ADR-014 remains open. The single-compartment spike-capable model remains exploratory and unaccepted.


The first residual-test run [43462098026](https://github.com/codexclai/HumanJS/actions/runs/43462098026) failed on an overstrict synthetic absolute-residual assertion. The test was corrected to compare the recomputed residual RMSE against the corresponding fixed-tau profile objective, and the full subsequent run [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed. No source implementation or numerical acceptance criterion was weakened.


## ADR-018 — Signed K_IV transient correction remains a numerical diagnostic

**Status:** Accepted · **Date:** 2026-11-13

The source-generated −70-mV K_IV post-peak waveform may be described with a non-source third exponential to test the early deterministic residual. The fitted extra coefficient is negative and very small (about 0.064% of peak current), and a nonnegative extra-amplitude control collapses to zero at the signed-model optimum. This is a signed correction to the chosen numerical fit family, not evidence for an additional positive current, channel state, biological inactivation process, or human kinetic time constant.

Keep the deposited helper, fitting caller, and pure-human NMODL unchanged. Do not transfer tau3 into Rust channel parameters, gate state, or the exploratory neuron model. The profile may be used as a numerical diagnostic only. Raw human K voltage-clamp traces and individual K kinetic targets remain unavailable in the inspected public deposit; this result does not close ADR-014 or biologically validate the provisional single-compartment spike mechanism.


## ADR-019 — Adjacent-voltage K_IV short-time correction remains a model-residual diagnostic

**Status:** Accepted · **Date:** 2026-11-13

A signed, non-source short-time exponential may be used to characterize the deterministic residual of the deposited Wilbers K_IV current-fit waveform. The correction has now been independently profiled at three adjacent source-model command voltages (-75, -70 and -65 mV). It is negative at all three commands, remains below 0.11% of peak current, and improves the full-waveform numerical residual. At the signed optimum, constraining its amplitude to be nonnegative collapses the extra coefficient to zero.

The three-voltage result supports only a bounded descriptive model-output trend. It does not identify a positive ionic current, molecular state, biological gate, or human fast-inactivation kinetic parameter. Do not add this correction to Rust channel equations or transfer its fitted tau3 into model parameters. The deposited source fitting helper, source caller and pure-human NMODL stay unchanged. Raw human K voltage-clamp recordings and individual K kinetic targets remain unavailable in the inspected public DataverseNL v3.0 deposit; this analysis does not satisfy ADR-014 or biologically validate the provisional single-compartment spike model.


### ADR-019 follow-up — full finite-positive K_IV source-fit set (2026-11-14)

The adjacent-voltage diagnostic was extended to every K_IV command with a finite positive fast-inactivation fit from the original source routine. Source selection is exhaustive and predeclared from the original K_IV helper: 34 commands were run; the source current threshold passed at 32 (-100 through +55 mV); five attempted fast fits were non-finite (-100, -95, -90, -85 and -80 mV); and the remaining 27 commands (-75 through +55 mV) had finite positive source fast-fit estimates. The two threshold exclusions (-110 and -105 mV) and the five non-finite fit attempts are recorded separately and are not treated as missing-at-random samples.

Across the 27 eligible model-generated waveforms, the signed non-source third-exponential coefficient was negative at all 27 commands; the nonnegative-amplitude control collapsed the extra term to zero at all 27 signed optima. Full-waveform RMSE reduction ranged from 55.467% to 80.386% (median 66.126%); first-10-ms reduction ranged from 75.608% to 94.278% (median 84.935%). After-10-ms RMSE improvement ranged from -41.467% to +27.728% (median +20.814%); the late-window error worsened at +25 through +55 mV (seven commands), despite lower full-waveform error at every command. The extra coefficient magnitude ranged from 0.0391% to 2.0965% of peak current.

The non-source tau3 optimum ranged from 0.6 to 2.0 ms (median 1.384 ms), with 11/27 profiles at one of the declared grid boundaries: 2.0 ms at -50 through -15 mV, and 0.6 ms at +45, +50 and +55 mV. Tau3 is not globally monotonic and these boundary outcomes are not interior estimates. Local tau1 ranged 17.195-393.404 ms; only -75 and -70 mV exceeded the deposited source helper's 300-ms upper bound. These findings describe a chosen numerical correction family on deterministic NEURON/VClamp model output, not human experimental current, a positive ionic component, a microscopic gate, or biological channel kinetics. The inspected DataverseNL v3.0 public inventory still lacks raw human K voltage-clamp NWB traces and individual K tau target CSVs. The deposited helper, caller, pure-human NMODL, and HumanJS runtime parameters were not changed; ADR-014 remains open.

Keep this as a descriptive numerical residual analysis only. Do not add the signed term or tau3 to Rust channel kinetics or the exploratory neuron. The repository's canonical 27-row summary is checked by the main workflow against the exact output regenerated from the pinned NEURON 9.0.2 source replay.


### ADR-019 follow-up — expanded tau3 profile interval (2026-11-14)

All 27 selected tau3 values are now strictly interior to the expanded 0.1–5.0-ms grid: there are **zero tau3 boundary hits**, compared with 11/27 hits on the narrower 0.6–2.0-ms search. The fitted tau3 values span 0.49725–2.9805 ms (median 1.38275 ms) and are **not globally monotonic** with voltage; the largest selected value is 2.9805 ms at -30 mV.

The signed added amplitude remains negative at all 27 commands, and the nonnegative-amplitude control still collapses to zero at all 27 selected optima. Full-waveform RMSE reduction is 59.945–80.386% (median 66.126%); first-10-ms RMSE reduction is 82.625–94.280% (median 89.018%). After-10-ms RMSE reduction ranges from -35.719% to +27.726% (median +20.817%): the late-window error still worsens at +25 through +55 mV (seven commands), even though the full-waveform fit improves at all 27 commands. The absolute added-amplitude magnitude is 0.0391–1.8791% of peak current (median 1.5976%).

The wider grid reduces concern that the prior 11 reported optima were simply clipped by the narrow interval. It does not show that tau3 is a biological kinetic parameter. The full-waveform objective still worsens the after-10-ms fit at seven commands (+25 through +55 mV), despite improving the total waveform objective. Every source-current waveform remains a deterministic NEURON/VClamp output, not a raw human experiment. Do not add the correction to Rust equations or model parameters. The helper, caller and pure-human NMODL remain unchanged; ADR-014 remains open.


### ADR-019 follow-up — full-waveform tau3 objective shape (2026-11-14)

The summary is derived from the same 27 exact post-peak NEURON 9.0.2/VClamp model-current waveforms and the same extended 0.1–5.0-ms tau3 grid (2,801 equally spaced points). At each grid point, all four coefficients are refit against the **full-waveform RSS** while tau1 is fixed at that command's independently profiled local optimum and source tau2 remains 450 ms. For each command, the report records the normalized central second difference of relative RSS at the selected grid minimum, the immediately adjacent left/right relative RSS increases, and the contiguous grid basin around the minimum whose relative RSS increase is no more than 1%, 5%, or 10%.

All 27 selected minima are interior, and **none of the 1%, 5%, or 10% near-minimum basins touches either edge** of the 0.1–5.0-ms grid. The normalized local curvature spans 0.382621–17.942831 ms⁻² (median 3.541781 ms⁻²). The contiguous 1%-RSS-increase basin spans 0.06475–0.45500 ms (median 0.14875 ms); the 5% basin spans 0.14875–1.02550 ms (median 0.33425 ms); and the 10% basin spans 0.21175–1.46125 ms (median 0.47600 ms).

The broadest profile occurs at -30 mV: normalized curvature 0.382621 ms⁻², with 1%, 5%, and 10% basin spans of 0.45500, 1.02550, and 1.46125 ms. The narrowest occurs at +55 mV: curvature 17.942831 ms⁻², with corresponding spans of 0.06475, 0.14875, and 0.21175 ms. Thus, although the expanded grid removed the previous boundary clipping, the local objective width is voltage-dependent and some selected minima are appreciably flatter than others.

These are **descriptive grid-basin spans of a deterministic model-output objective**, not statistical confidence intervals, measurement uncertainty, or biological uncertainty estimates. No noise model was fitted. The widths are conditional on tau1 being held at its selected per-voltage local optimum; they do not account for coupling to tau1 or uncertainty in the source fit. The waveforms are generated by the deposited pure-human K mechanism under NEURON 9.0.2/VClamp, not raw human experimental K-current recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. The deposited fitting helper, caller, pure-human NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or the signed residual correction into Rust channel kinetics. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The reference file `research/HUMAN-L23-WILBERS-K-IV-TAU3-PROFILE-SHAPE.csv` is compared field-by-field in the main workflow. This remains a model-side numerical diagnostic only; it does not provide empirical human current fits or satisfy ADR-014.


### ADR-019 follow-up — conditional tau1–tau3 surface (2026-11-14)

A conditional sensitivity surface was evaluated at the predeclared -30, -60, and +55 mV commands. Nine tau1 values span each already measured local 6% tau1 refinement interval; tau3 is independently profiled over 0.1–10.0 ms on 5,601 points at every tau1 node, with the complete coefficient vector refit against full-waveform RSS and source tau2 fixed at 450 ms. Early and late RMSE remain diagnostics.

| Command | Existing local tau1 (ms) | Existing single-tau1 tau3 (ms) | Tau1 local window (ms) | Conditional tau3 minima over the window (ms) | Best sampled surface tau1 / tau3 (ms) | Full-RSS reduction vs center tau1 slice |
|---:|---:|---:|---:|---:|---:|---:|
| -30 mV | 112.958 | 2.9805 | 106.021–119.556 | 2.057–5.092 | 107.755 / 4.339 | 96.276% |
| -60 mV | 251.949 | 1.56825 | 237.580–267.909 | 1.224–2.140 | 244.764 / 1.802 | 96.955% |
| +55 mV | 17.195 | 0.49725 | 16.134–18.194 | 0.498–10.000 | 17.195 / 0.498 | 0% |

At -30 and -60 mV all nine conditional tau3 minima are interior to the 0.1–10-ms grid. Allowing tau1 to move within its existing local interval materially shifts the sampled full-RSS minimum: the -30-mV minimum is at tau1 107.755 ms/tau3 4.339 ms, while the -60-mV minimum is at 244.764 ms/1.802 ms. Relative to the center tau1 slice, their full-waveform RSS falls by 96.276% and 96.955%, respectively. These are reductions in the objective RSS, not RMSE percentages.

The +55-mV surface behaves differently. Six of its nine tau1 slices select tau3 at the expanded 10-ms upper boundary. Its best sampled surface point remains at the center tau1 (17.195 ms) and tau3 0.49777 ms, so the global full-RSS objective does not improve relative to that center slice. The signed extra amplitude is negative at tau1 indices 0–4 but positive at indices 5–8. Thus, the sign and fitted short component are sensitive to the allowed tau1 change at this depolarized command, and the 10-ms upper limit still fails to localize several conditional minima.

At the center tau1 node, the contiguous 1%/5%/10% objective-basin spans are 0.4561/1.0254/1.4620 ms at -30 mV, 0.1485/0.3359/0.4756 ms at -60 mV, and 0.06541/0.14673/0.21037 ms at +55 mV. These widths are conditional slices through a discrete, deterministic objective surface; they are not statistical uncertainty intervals.

The surface makes clear that the earlier fixed-tau1 basin widths are conditional, not parameter uncertainty. At -30/-60 mV the best sampled full-RSS point shifts within the local tau1 window and substantially reduces the objective. At +55 mV six of nine tau1 slices remain clipped at tau3=10 ms and the signed extra amplitude changes sign across the tau1 grid. The result is a non-source numerical fit to deterministic NEURON/VClamp model output, not raw human data or evidence for a biological gate. Do not transfer any fit term into Rust channel kinetics. The deposited helper, caller, NMODL and HumanJS runtime parameters remain unchanged; ADR-014 remains open.
