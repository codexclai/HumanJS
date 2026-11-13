# HumanJS — decision record

**Decision authority:** project owner.  
**Updated:** 2026-11-10.

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
