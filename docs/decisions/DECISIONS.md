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

## ADR-015 — Published-model reproduction is evidence, not HumanJS implementation

**Status:** Accepted · **Date:** 2026-11-11

The canonical Eyal et al. 2018 ModelDB archive may be used in a separately documented experiment to verify original source availability, parameter mapping, compilation and selected model behavior. Such an experiment must identify archive integrity, execution environment, model configuration, stimulus, comparison metric, released data, deviations and limitations. External model execution does not implement an AP mechanism in the HumanJS Rust core, does not validate HumanJS biologically, and does not establish whole-brain functionality. Do not copy the external model wholesale into HumanJS or silently describe transferred rodent kinetics as human measurements.


## ADR-016 — Exploratory human L2/L3 single-compartment spike code remains unaccepted

**Status:** Accepted classification and corrective action · **Date:** 2026-11-11

The Rust core now contains `HumanL23SingleCompartmentModel` in `crates/humanjs-core/src/ion_channels.rs`. It is capable of generating an action potential in a specified current-clamp software fixture. This code was added before the evidence gate in ADR-014 had been closed. Its existence must be documented accurately, but its presence does not waive or retroactively satisfy that gate.

Classify the implementation as **exploratory and not scientifically accepted** until the remaining source and validation questions are resolved. It uses human Na+ gate parameters from the pure Wilbers source, K+ parameters matching the pure mechanism and Table S2 / first optimizer result, and current-clamp fitted conductance densities and setup. The latter are fitted against cross-species mean AP features, not direct human channel-density measurements. The Rust `trap0` uses the analytic mathematical limit rather than reproducing the source's defective branch behavior. The selected K+ inactivation set matches the parameters actually applied by the deposited script. A Rust model-side K_IV_ss replay now covers the deposited steady-state voltage grid and its activation/inactivation half-range crossings and −80-mV availability fall within the published human group mean ± SD. This remains a coarse summary check: the exact K+ kinetic CSV targets and raw voltage-clamp traces are absent, so fast/slow time-constant reproduction remains outstanding. The article's 14-parameter description versus the deposited 11-variable optimizer sequence is now explained by fixed experimental inactivation steady states and `Rb = Ra`, though independent protocol reproduction remains outstanding. The article Discussion also acknowledges that its HH models do not accurately reproduce all potassium-channel properties, especially K+ inactivation, and that this likely contributes to poor fits of K+ currents and AP falling speeds (Wilbers et al., 2023, https://doi.org/10.1126/sciadv.ade3300).

Do not remove or extend this exploratory mechanism merely to make the documentation appear consistent. First complete the evidence audit, unit/temperature review, voltage-clamp comparisons, current-clamp setup review, and independent regression tests recorded in the architecture and research documents. Keep all claims limited to software-level behavior until evidence-based validation is complete. The model is one lumped compartment and is not an anatomical soma/AIS neuron, full pyramidal neuron, or biological validation result.
