# Human neocortical spike-initiation evidence and implementation boundary

**Reviewed:** 2026-11-10  
**Scope:** somatic action-potential generation and axon-initial-segment (AIS) initiation in human neocortical pyramidal cells.  
**Status:** evidence review complete enough to reject an unqualified generic model; exact model-source reconciliation remains open. No spike-generation code is implemented by this review.

## Decision summary

Human data support three distinct evidence layers:

1. **Human somatic current recordings:** Na+ and K+ current kinetics and current densities have been measured in nucleated somatic patches from human L2/L3 pyramidal cells. These data support human-specific somatic channel models, but the excised patch does not contain the AIS.
2. **Human AIS molecular distribution:** immunostaining supports a proximal NaV1.2 and more distal NaV1.6 distribution along pyramidal-cell AISs. It does not measure absolute functional channel density, conductance, gating kinetics, or the complete channel distribution needed for an AIS model.
3. **Human neuron model fits:** detailed six-cell models fit somatic/axonal spike recordings with conductance-based models. The fitted conductance densities are useful constraints, but the authors explicitly assume channel kinetics similar to rodents; these are not measurements of human channel gating.

These sources are complementary, not interchangeable. A single-compartment soma/nucleated-patch equivalent must not be described as an anatomically complete neuron or an AIS-resolved initiation model. An AIS compartment requires additional parameter provenance that is not established by immunostaining alone.

**No intrinsic spike-initiation mechanism is approved for implementation yet.** A bounded somatic-patch-equivalent is a possible first increment after exact human kinetic equations, parameter units, temperature corrections, and fit-source provenance have been verified. An anatomical soma/AIS model is a separate, stricter milestone.

## 1. Eyal et al. (2018): human L2/L3 soma/axon model fits

**Primary source:** Guy Eyal et al., “Human Cortical Pyramidal Neurons: From Spines to Spikes via Models,” *Frontiers in Cellular Neuroscience* 12 (2018), 181.  
DOI: https://doi.org/10.3389/fncel.2018.00181  
Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/  
ModelDB record: https://modeldb.science/238347

The paper integrated anatomical and physiological data for six human layer 2/3 pyramidal cells from temporal cortex. The active somatic/axonal models were constrained by approximately 900 spikes recorded from those six cells. The recordings included repeated depolarizing current-step protocols; the authors also used normalized I–F curves from 25 additional human L2/L3 pyramidal cells. The modeled axon was a short 60 μm extension, introduced by analogy to prior models; this is not a direct measurement of an individual human AIS length.

The model used multi-objective evolutionary fitting. The paper describes 29 free parameters: nine maximal ion-channel conductances, three sodium-channel kinetic parameters, two intracellular-calcium parameters, fitted for soma and axon (14 parameters each), plus a shared leak reversal potential. The optimization began with 1,000 candidate models and ran for 500 generations. These are fitted model parameters, not direct measurements of channel density in the AIS.

Reported fit-derived examples include:

| Quantity | Reported value | Evidence class |
|---|---:|---|
| Axonal Na+ conductance density | 4.9 ± 1.0 S/cm² (n=6) | Conductance density inferred by fitting human spike recordings |
| Somatic Na+ conductance density | 0.33 ± 0.17 S/cm² | Conductance density inferred by fitting human spike recordings |
| Axonal Kv3.1 conductance density | 1.9 ± 0.1 S/cm² | Conductance density inferred by fitting human spike recordings |
| Axonal persistent K+ density | 0.019 ± 0.039 S/cm² | Conductance density inferred by fitting human spike recordings |
| Somatic persistent K+ density | 0.0002 ± 0.0004 S/cm² | Conductance density inferred by fitting human spike recordings |

The recorded spikes used as fit targets had a large peak (38.6 ± 3.2 mV from a voltage base of −83.5 ± 2.9 mV) and a half-width of 1.02 ± 0.15 ms. These data constrain the output waveform and firing pattern, but do not independently identify every channel's molecular density or microscopic kinetics.

**Critical kinetic limitation:** the authors state that channel kinetics were assumed to be similar to those in rodents, citing Ranjan et al. (2011)/Channelpedia. Human recordings constrain the fitting targets and fitted conductance parameters; they do not make those transferred kinetic functions human measurements.

**Critical anatomical limitation:** active conductances were included in soma and axon only. The authors explain that human dendritic recordings were lacking and that somatic recordings alone could not adequately constrain active dendritic parameters. The paper also identifies back-propagating APs and dendritic Ca2+-spike behavior as requiring further human data. The model is therefore not a fully measured distribution of active conductances across a human neuron.

### Mechanism-source inspection and an unresolved mapping issue

The ModelDB record is the primary model citation and should be the starting point for any later reproduction. A separate public analysis repository, beaherrera/SEF_error-PCs_theta_ERN, contains an EyalEtAl2018 ActiveMechanisms directory with generated C files that embed NMODL source text. Its repository is GPL-3.0 and is not the canonical ModelDB package. It was inspected only to identify source references and mechanism families; no source code is copied into HumanJS, and its licensing/provenance does not establish permission to redistribute those mechanisms here.

The inspected registration list names these current mechanisms: NaTg, Nap_Et2, K_Tst, K_Pst, SKv3_1, SK_E2, Ca, Ca_HVA, Ca_LVAst, and Im, plus CaDynamics_E2 for intracellular calcium dynamics. The paper's methods, however, describe nine fitted ion-channel maximal conductances. The precise mapping between the registered mechanism list, the active mechanisms actually used in the six models, and Table S4 has not yet been reconciled against the original downloadable ModelDB package and supplement. Do not silently choose nine or ten, omit a current, or treat a registered mechanism as proof that it was active in every compartment.

The inspected mechanism comments identify non-human or transferred source literature for several kinetic forms: NaTg references Colbert and Pan (2002); Nap_Et2 refers to Magistretti and Alonso (1999) and describes an approximate activation-time relation; K_Tst and K_Pst cite young-rat neocortical K+ channel work by Korngreen and Sakmann (2000); SKv3_1 cites rat-brain channel work; SK_E2 cites Köhler et al. (1996); Ca_LVAst says its activation time constant was approximated from plots and cites Avery and Johnston (1996)/Randall (1997); and Im cites bullfrog sympathetic-neuron M-current work. Multiple mechanisms include a Q10 correction of 2.3 from 21°C toward a 34°C model temperature. These are source comments from a secondary compiled-code snapshot, not direct human channel measurements. They need verification against the original model files before use.

## 2. Wilbers et al. (2023): direct human somatic Na+/K+ measurements

**Primary source:** “Human voltage-gated Na+ and K+ channel properties underlie sustained fast AP signaling,” *Science Advances* (2023).  
DOI: https://doi.org/10.1126/sciadv.ade3300  
Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10569700/  
Supplementary information (Tables S1–S3): https://pmc.ncbi.nlm.nih.gov/articles/instance/10569700/bin/sciadv.ade3300_sm.pdf

The study examined supragranular human pyramidal cells from surgical association-cortex tissue. It reports 19 human donors aged 21–70 years and whole-cell recordings from 36 human L2/L3 pyramidal cells. Repetitive current-injection protocols examined AP-shape stability across firing frequencies. Na+ and K+ currents were pharmacologically isolated in separate voltage-clamp experiments using nucleated somatic patches.

The voltage-clamp preparation is important: a nucleated somatic patch isolates somatic membrane and does not preserve the AIS. These recordings therefore provide direct human somatic channel evidence, not direct human AIS gating measurements or an intact somato-axonal conductance distribution.

### Direct human measurements

| Measurement | Human value | Sample | Interpretation |
|---|---:|---:|---|
| Na+ activation V1/2 | −32.13 ± 4.86 mV | n=19 recordings | Human somatic patch steady-state activation |
| Na+ inactivation V1/2 | −66.00 ± 7.82 mV | n=18 | Human somatic patch steady-state inactivation |
| Na+ availability at −80 mV | 0.81 ± 0.16 | Reported group result | More channels available at this voltage than in mouse |
| K+ activation V1/2 | −3.03 ± 5.95 mV | n=13 | Human somatic patch steady-state activation |
| K+ inactivation V1/2 | −52.69 ± 5.97 mV | n=11 | Human somatic patch steady-state inactivation |
| K+ availability at −80 mV | 0.94 ± 0.05 | Reported group result | Higher availability than in mouse |
| Na+ conductance density | 5.9 ± 0.8 pS/μm² | n=17; mean ± SEM | Measured in human nucleated somatic patches |
| K+ conductance density | 31.2 ± 4.2 pS/μm² | n=13; mean ± SEM | Measured in human nucleated somatic patches |

The reported human Na+ currents activated and inactivated more slowly than mouse currents but recovered more quickly from inactivation. Human K+ activation was faster at lower membrane potentials; the K+ steady-state activation and inactivation curves were shifted to more depolarized potentials. K+ inactivation and recovery time constants were not convincingly different between species in the study, although availability and recovery amplitude differed.

The study used different recording temperatures for different measurements and included a Q10 correction of 2.3 in its model parameterization. The Na+ activation measurements were made at 25°C; other current recordings were performed at approximately 34°C. Temperature and recording-protocol provenance must remain attached to any parameter reused from the paper.

### Model boundary and fitted parameter caveat

The authors built a single-compartment HH-style model of 10 μm diameter to approximate a nucleated somatic patch. It is not an anatomical neuron and does not include an AIS. Its reported fitted parameters include approximately 114.5 pS/μm² maximal Na+ conductance and 29.05 pS/μm² maximal K+ conductance, with ENa=53 mV, EK=−101 mV, and a 1 pS/μm² passive leak. The fitted Na+ conductance is much larger than the directly measured human nucleated-patch mean of 5.9 ± 0.8 pS/μm²; the authors explicitly note this difference. The fitted model value must not be relabeled as a directly measured human somatic channel density.

The sodium model used separate Boltzmann steady-state functions for activation and inactivation, with voltage-dependent transition/time-constant functions fitted to current recordings. The article describes 14 free parameters for sodium: two steady-state parameters per gate, four activation-kinetic parameters, and six inactivation-kinetic parameters. The potassium model used three fractions with different inactivation behavior:

- gK1 = gmax · m² · h1 · frac_inact · (1 − frac_h2)
- gK2 = gmax · m² · h2 · frac_inact · frac_h2
- gK3 = gmax · m² · (1 − frac_inact)

The slow-inactivation time constants were fixed to common human/mouse values because the source measurements did not justify distinct fits; the fractions frac_inact=0.85 and frac_h2=0.4 were fixed from the experimental behavior. This is a specific fitted decomposition, not a complete K-channel molecular Markov model.

The original supplementary PDF was retrieved and Table S2 was inspected. Its fitted **human** single-compartment parameter values are listed below. These are fitted model parameters, not direct measurements of conductance density or molecular gating constants in an intact human AIS.

| Parameter family | Table S2 human value | Table's description / provenance |
|---|---:|---|
| Compartment diameter | 10 μm | Single compartment; described as roughly representing a nucleated patch |
| Specific membrane capacitance | 1 μF/cm² | Explicitly confirmed in the article's Methods |
| Axial resistivity | 200 Ω·cm | Single-compartment model |
| Specific membrane resistance | 10,000 Ω·cm² | Table S2; source formatting should be retained when transcribing |
| Passive conductance density | 0.0001 S/cm² (= 1 pS/μm²) | Leak conductance |
| Passive reversal | −85 mV | Leak reversal |
| Maximum Na+ conductance | 114.5 pS/μm² | Fitted AP-model value, not measured patch mean |
| Na+ reversal | 53 mV | Calculated for current-clamp ionic conditions |
| Maximum K+ conductance | 29.05 pS/μm² | Fitted AP-model value, not a molecular subtype density |
| K+ reversal | −101 mV | Calculated for current-clamp ionic conditions |

**Human Na+ gate parameters in Table S2**

| Parameter | Value | Table description |
|---|---:|---|
| `th_act_inf` | −42.291457 mV | Activation steady-state half-voltage |
| `q_act_inf` | 10.2311529 mV | Activation steady-state slope |
| `tha` | −58.592356 mV | Activation/deactivation time-constant half-voltage |
| `qa` | 9.21455372 mV | Activation/deactivation time-constant slope |
| `Ra` | 0.21398493 ms⁻¹ (table unit) | Open/close rate parameter as named in Table S2 |
| `th_act_inf` (label repeated) | −64.48 mV | Description says inactivation steady-state half-voltage |
| `q_inact_inf` | 11.02 mV | Inactivation steady-state slope |
| `thi1` | −39.298677 mV | Inactivation time-constant half-voltage |
| `thi2` | −77.166745 mV | Recovery-from-inactivation time-constant half-voltage |
| `qi1` | 7.21636387 mV | Inactivation time-constant slope |
| `qi2` | 4.74945005 mV | Recovery time-constant slope |
| `Rd` | 0.04763919 ms⁻¹ (table unit) | Inactivation rate parameter |
| `Rg` | 0.01195166 ms⁻¹ (table unit) | Recovery rate parameter |
| `q10` | 2.3 | Temperature sensitivity factor |

**Human K+ gate parameters in Table S2**

| Parameter | Value | Table description |
|---|---:|---|
| `th_act_inf` | −18.406164 mV | Activation steady-state half-voltage |
| `q_act_inf` | 19.1995503 mV | Activation steady-state slope |
| `tha` | −29.961798 mV | Activation/deactivation time-constant half-voltage |
| `qa` | 6.59040569 mV | Activation/deactivation time-constant slope |
| `Ra` | 0.01845925 ms⁻¹ (table unit) | Open/close rate parameter as named in Table S2 |
| `th_act_inf` (label repeated) | −52.61 mV | Description says inactivation steady-state half-voltage |
| `q_inact_inf` | 13.09 mV | Inactivation steady-state slope |
| `thi1` | 40.5659149 mV | Inactivation time-constant half-voltage |
| `thi2` | −75.938227 mV | Recovery-from-inactivation time-constant half-voltage |
| `qi1` | 26.7739292 mV | Inactivation time-constant slope |
| `qi2` | 0.40183383 mV | Recovery time-constant slope |
| `Rd` | 0.00169014 ms⁻¹ (table unit) | Inactivation rate parameter |
| `Rg` | 0.00049688 ms⁻¹ (table unit) | Recovery rate parameter |
| `h2tau_inact` | 450 ms | Slow-inactivation time constant |
| `h2tau_inact_rec` | 2789.79294 ms | Slow-inactivation recovery time constant |
| `prop_inact` | 0.85 | Fraction of conductance that inactivates |
| `prop_h2` | 0.4 | Fraction of the inactivating conductance assigned to slow inactivation |
| `q10` | 2.3 | Temperature sensitivity factor |

The PDF table prints `th_act_inf` a second time for the inactivation steady-state row. This label problem is partly resolved by the author-deposited fitting code: `fit_na_hh_cma_human.py` sets the parameter under the explicit name `th_inact_inf_na_human`, and `fit_k_hh_cma_human.py` uses `th_inact_inf_k_human`. The intended row semantics are therefore inactivation steady-state half-voltage, even though the Table S2 printed label is repeated.

The paper reports 14 free parameters for each channel model. However, the author-deposited fitting scripts expose 13 human Na parameter names across their fit stages (6 inactivation/recovery + 3 activation-kinetic + 2 activation steady-state + 2 inactivation steady-state values) and 11 explicit human K fit parameters (6 inactivation/recovery + 3 activation-kinetic + 2 activation steady-state), with other K quantities assigned from measured or fixed values. The deposited K script also contains a final-fit dictionary whose inactivation/recovery values differ from the earlier optimizer result that matches Table S2. This means the methods-level parameter count, Table S2, and script snapshots have not yet been reconciled into one definitive parameter manifest. Do not choose one silently.

Table S2 has no separate `Rb` row, while the referenced Mainen-style activation-rate template has both `Ra` and `Rb`. The fitting script's activation fit list includes `tha`, `qa`, and `Ra`, but not `Rb`; `Rb` may be fixed in the corresponding NEURON mechanism, but its value in the Wilbers source mechanism has not been verified. The rate-prefactor rows are reported in ms⁻¹. The specific-resistance unit in the PDF table should still be checked against the original NEURON mechanism before encoding.

### Author-deposited fitting code and protocol cross-check

The researchers' public data deposit is DataverseNL DOI [10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD), version 3.0, released 2022-12-13 under CC0-1.0. It includes the fitting scripts, protocol/analysis helpers, and the original NEURON mechanism files. The relevant deposited text-code files were inspected:

| File | Dataverse file ID | What it establishes |
|---|---:|---|
| `fit_na_hh_cma_human.py` | 326238 | Sequential human Na+ fitting stages and named fitted values |
| `fit_k_hh_cma_human.py` | 326237 | Sequential human K+ fitting stages, fixed values, and one internal result inconsistency |
| `channel_tools.py` | 326242 | Voltage-clamp analysis functions, command protocols, and recording temperature |
| `cc_tools.py` | 318557 | Single-compartment AP model initialization, current-clamp temperature, liquid-junction-potential handling, and fitted conductance density |
| `na_human.mod` | 318629 | Original NEURON Na+ mechanism file metadata; 3.5 KB, SHA1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970` |
| `k_human.mod` | 318647 | Original NEURON K+ mechanism file metadata; 4.1 KB, SHA1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5` |

The two `.mod` files are listed by Dataverse as public `audio/mod` files. Their metadata and checksums were verified, but the available document extraction interfaces reject that MIME type, so their source text has not been inspected in this review. The corresponding older-current-clamp directory also lists `na_human.mod` (file 318563; SHA1 `ef158980e4bb427c97cfb8f379cd63006130b3b2`) and `k_human.mod` (file 318566; SHA1 `622f7c9867e727a3dc7dea1f9ba2efbfb94cfd3a`). Do not assume those duplicate-location files are byte-identical without comparing their content hashes.

#### Human Na+ fitting sequence recorded in the deposited script

The author script runs separate fits:
1. Six inactivation/recovery values: `thi1`, `thi2`, `qi1`, `qi2`, `Rd`, and `Rg`.
2. Three activation-kinetic values: `tha`, `qa`, and `Ra`.
3. Two activation steady-state values: `th_act_inf` and `q_act_inf`.
4. It also assigns the inactivation steady-state values as `th_inact_inf_na_human = -64.48 mV` and `q_inact_inf_na_human = 11.02 mV`.

The fit script initializes a 10 μm NEURON section with `Ra = 200 Ω·cm`, `Cm = 1 μF/cm²`, and `ENa = 141 mV` for its voltage-clamp current calculations.

The fitted values printed in the script match the corresponding Table S2 human entries for the three optimization stages: `thi1 = -39.2986769 mV`, `thi2 = -77.1667453 mV`, `qi1 = 7.21636387 mV`, `qi2 = 4.74945005 mV`, `Rd = 0.04763919 ms⁻¹`, `Rg = 0.01195166 ms⁻¹`, `tha = -58.5923561 mV`, `qa = 9.21455372 mV`, `Ra = 0.21398493 ms⁻¹`, `th_act_inf = -42.2914567 mV`, and `q_act_inf = 10.2311529 mV`. The script's explicit parameter names resolve the repeated Table S2 row label, but the discrepancy between the paper's stated 14 free parameters and the 13 parameter names visible across those fitting/assignment stages remains open.

#### Human K+ fitting sequence recorded in the deposited script

The K+ script:
- Assigns `th_inact_inf_k_human = -52.6 mV` and `q_inact_inf_k_human = 13.09 mV` from the human experimental steady-state inactivation fit (the paper/table report approximately −52.61 mV).
- Fits six inactivation/recovery parameters (`thi1`, `thi2`, `qi1`, `qi2`, `Rd`, `Rg`), three activation-kinetic parameters (`tha`, `qa`, `Ra`), and two activation steady-state parameters (`th_act_inf`, `q_act_inf`).
- Explicitly assigns `h12factor_k_human = 10.5` before the activation fit.

Its first inactivation optimizer result matches the Table S2 values `thi1 = 40.5659149 mV`, `thi2 = -75.9382266 mV`, `qi1 = 26.7739292 mV`, `qi2 = 0.40183383 mV`, `Rd = 0.00169014 ms⁻¹`, and `Rg = 0.00049688 ms⁻¹`. However, the same script's final printed “best fit” dictionary contains different values for these six entries (`thi1 = 20.3866205 mV`, `thi2 = -84.1648768 mV`, `qi1 = 25.7483108 mV`, `qi2 = 6.80912645 mV`, `Rd = 0.000996811 ms⁻¹`, `Rg = 0.000438888 ms⁻¹`). This result snapshot does not agree with Table S2 or the earlier optimizer result. The script's displayed sequence does not establish which parameter set was finally used to produce the published simulation. Resolve this from the `k_human.mod` contents and original run artifacts before porting.

#### Recorded voltage-clamp and current-clamp settings

The deposited `channel_tools.py` defines:
- Na+ channel I–V/kinetic analysis at 25°C, `dt = 0.01 ms`. The activation protocol uses a −120 mV holding level followed by 10 ms test steps from −80 mV to +10 mV in 5 mV increments. The inactivation protocol uses a 1 ms −70 mV holding segment, a 50 ms conditioning segment stepped from −105 mV to −47 mV in 2 mV increments, and a 10 ms test at −10 mV. Recovery uses 2 ms at −120 mV, 10 ms at 0 mV, a variable recovery segment (square-spaced delays), and a 2 ms test pulse. These Na+ voltage-clamp protocols all execute with `h.celsius=25`.
- K+ channel I–V/kinetic analysis at 34°C, `dt = 0.1 ms`, using a 20 ms holding segment, a 500 ms conditioning segment, a 50 ms test segment, and a 100 ms final segment; test voltages span −110 mV to +55 mV in 5 mV increments. The helper uses a double-exponential inactivation analysis and separately represents fast and slow inactivation/recovery. The K+ fitting script initializes `EK = -101 mV` for these voltage-clamp protocols.

The current-clamp helper `cc_tools.py` initializes a single 10 μm compartment with `Ra = 200 Ω·cm`, `Cm = 1 μF/cm²`, `Rm = 10,000 Ω·cm²` and `g_pas = 1/Rm`, `h.celsius = 34`, and reversals offset from the nominal current-clamp values to account for the liquid-junction potential. It sets channel voltage shifts to −10 mV when moving between the voltage-clamp and current-clamp internal solutions; it adds +15 mV to the nominal `ENa = 53 mV`, `EK = -101 mV`, and `Epas = -85 mV` in that initialization path. The voltage-clamp `Na_IV` and `K_IV` helpers themselves do not apply a voltage shift.

The separate conductance-density fitting helper adjusts human and mouse channel fractions and minimizes current-clamp AP waveform differences in amplitude, rise speed, and fall speed. The article describes fits to cross-species mean AP features (48.4 mV, 420 mV/ms, and 73.1 mV/ms), followed by a grid of channel-fraction combinations. The resulting AP-model conductance densities are therefore outputs of a particular optimization target; they are not direct patch measurements.

These deposited scripts materially improve parameter provenance and resolve the intended name of the repeated inactivation steady-state label. They do **not** expose the underlying `na_human.mod` and `k_human.mod` equations through the text extraction path used here. Exact gate-rate equations, any fixed `Rb`, the table-versus-script K+ result discrepancy, and the 14-parameter bookkeeping remain open.

### Published fitted equations and inherited rate-form source

The article defines separate steady-state Boltzmann functions for the sodium activation and inactivation gates:

`m∞ = 1 / (1 + exp((Vhalf,act − Vm) / qact))`

`h∞ = 1 / (1 + exp((Vm − Vhalf,inact) / qinact))`

The activation and inactivation time constants are fitted independently to the measured current traces. The article states that the Na+ gate model has 14 free parameters: two steady-state parameters for each gate, four activation-kinetic parameters, and six inactivation-kinetic parameters. The fit first estimates `m∞`, `h∞`, `mτ`, and `hτ`, then applies the same voltage-clamp command protocols in NEURON and minimizes the sum of squared normalized differences to experimental means with CMA-ES/DEAP (50–500 generations). Human and mouse channel models are fit independently.

The article states that its Na+ model is similar in HH style to the Mainen et al. ModelDB 8210 mechanism. The original `na3h5.mod` source exposes the following inherited rate template, which is a separate source from the fitted human parameters:

- `αm = trap0(Vm, tha, Ra, qa)`
- `βm = trap0(−Vm, −tha, Rb, qa)`
- `τm = 1 / (αm + βm)`
- `αh = trap0(Vm, thi1, Rd, qi)`
- `βh = trap0(−Vm, −thi2, Rg, qi)`
- `τh = 1 / (αh + βh)`
- `trap0(v, th, a, q) = a (v − th) / (1 − exp(−(v − th)/q))`, with the limiting value `a q` when `v = th`.

For the Wilbers fit, `m∞` and `h∞` are the separate Boltzmann functions above rather than the original template's `a/(a+b)` steady states. The source template contains `Rb = 0.124` as a fixed parameter and a Q10 adjustment of `2.3^((celsius − temp)/10)`; the exact value of `Rb` and the runtime/reference temperature used in the Wilbers simulations must be checked against their original implementation before translating the rate functions. Do not assume that every line of the older ModelDB 8210 mechanism was retained unchanged.

For the K+ current, the article uses three components with different inactivation behavior:

- `gk1 = gmax · m² · h1 · frac_inact · (1 − frac_h2)`
- `gk2 = gmax · m² · h2 · frac_inact · frac_h2`
- `gk3 = gmax · m² · (1 − frac_inact)`
- `gk = gk1 + gk2 + gk3`

The slow-inactivation kinetics are shared between human and mouse because recorded time constants did not justify species-specific fit models. `frac_h2=0.4` and `frac_inact=0.85` are fixed, not fitted. The paper notes that this simplified HH K+ model did not accurately reproduce all K+ inactivation behavior.

**Direct measurement versus model fit:** Table S1 contains measured steady-state Boltzmann fit values; Table S2 contains the authors' single-compartment AP-model parameterization; Table S3 contains measured patch area and conductance. The main text reports human nucleated-patch conductance densities of Na+ 5.9 ± 0.8 pS/μm² (n=17) and K+ 31.2 ± 4.2 pS/μm² (n=13), mean ± SEM. Table S3 separately gives mean ± SD: Na+ density 5.85 ± 3.38 pS/μm² (n=17) and K+ density 31.22 ± 14.71 pS/μm² (n=13). The larger Table S2 fitted Na+ density (114.5 pS/μm²) is not a measured patch density. The authors explicitly note that the Na+ density required by their single-compartment AP model exceeds the density recorded in somatic nucleated patches. The model is therefore an optimized input-output representation, not a direct reproduction of measured somatic channel abundance.

The article's Methods specify the single compartment as 10 μm diameter, specific capacitance 1 μF/cm², axial resistivity 200 Ω·cm, and reversal potentials 53 mV for Na+ and −101 mV for K+. It describes the conductance model as a nucleated-patch approximation, not an AIS-resolved neuron model. Its AP waveform fitting used model simulations optimized against experimental AP amplitude, rise speed, and fall speed; it does not identify the anatomical location or density gradient of Na+ channels in an intact human AIS.

Most importantly, the authors state that the characteristics of the human AIS membrane and its contribution to AP initiation remain to be determined. The nucleated patch omits the AIS and cannot supply its channel density, geometry, or gating kinetics.

## 3. Tian et al. (2014): human AIS sodium-channel localization

**Primary source:** “Molecular identity of axonal sodium channels in human cortical pyramidal cells,” *Frontiers in Cellular Neuroscience* (2014).  
DOI: https://doi.org/10.3389/fncel.2014.00297  
Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC4172021/

This study used immunohistochemistry on human surgical cortical tissue from 15 patients with mixed clinical indications, including temporal and frontal lobe epilepsy, tumors, and cerebrovascular disease. It examined the molecular identity and spatial distribution of voltage-gated sodium-channel subtypes along cortical pyramidal-cell AISs.

The reported pattern was a proximal enrichment of NaV1.2 and a more distal enrichment of NaV1.6: NaV1.2 signal peaked approximately 9–14 μm from the soma, whereas NaV1.6 signal peaked around 25–29 μm. The study used an AIS-length criterion exceeding 40 μm for its analyses. NaV1.1 was not detected at pyramidal-cell AISs in the reported staining, although it was found in interneurons.

This is human molecular-localization evidence, not electrophysiology. Immunostaining does not yield an absolute count of functional channels, current density, maximal conductance, activation/inactivation kinetics, or the effective membrane area of each channel subtype. The authors discuss methodological limits on absolute channel-density quantification. The tissue is also a clinical surgical sample rather than a population-representative sample of healthy human cortex.

It is reasonable to preserve the NaV1.2-proximal/NaV1.6-distal pattern as an anatomical hypothesis for a later AIS model, with its sampling and measurement limitations. It is not reasonable to turn the staining intensity or peak locations into numerical conductance densities or gating parameters.

## 4. State-of-field cross-check: Zulaica et al. (2026) preprint

**Preprint:** “A Detailed Model for Understanding the Human Neocortex,” posted 2026-01-29.  
DOI: https://doi.org/10.64898/2026.01.29.702592

This preprint is useful as a state-of-field check, not as a direct source of human channel parameters. Its human-neocortex microcircuit model substitutes rat ion-channel and receptor mechanisms rather than claiming a comprehensive human-specific kinetic dataset. The authors discuss the difficulty of constructing and validating human channel mechanisms from the available measurements. The model therefore reinforces the evidence gap; it does not fill it.

## 5. Implementation gate and current conclusion

Before writing an intrinsic spike model in HumanJS, close these specific questions:

1. **Choose the represented preparation explicitly.** Decide whether the first increment is a somatic nucleated-patch equivalent or an intact soma/AIS model. State its anatomical and electrophysiological boundary in type names, documentation, and tests.
2. **Verify exact human somatic gate equations.** Retrieve and cross-check the original Wilbers supplement and model implementation, including the m∞, h∞, activation-time, inactivation-time, and recovery functions; fit parameters; units; voltage sign conventions; and temperature corrections. Resolve ambiguous extracted table labels against the original source.
3. **Reconcile conductance density.** Keep the measured human somatic patch densities separate from the much larger fitted Na+ conductance used in the paper's single-compartment AP simulation. Do not convert one into the other without reproducing and documenting the authors' fitting assumptions.
4. **Keep AIS evidence separate.** Human NaV1.2/NaV1.6 staining supplies spatial subtype evidence, but not absolute conductance or gating. Do not invent AIS channel densities, kinetics, or gradients from immunostaining.
5. **Audit the Eyal model package.** Map every Table S4 parameter to the original ModelDB mechanisms and compartment assignments. Reconcile the paper's nine fitted channel conductances with the mechanism names in the available secondary code snapshot. Keep rodent-derived kinetic functions explicitly marked as transferred model assumptions.
6. **Add causal validation targets only after parameter provenance is closed.** Candidate targets include human somatic AP threshold/onset, waveform height and half-width, afterhyperpolarization, repetitive firing/adaptation, and availability/recovery behavior under matched voltage protocols. Passing software tests would still not constitute biological validation.

A first somatic-patch-equivalent model may become defensible using the direct human channel recordings and the paper's fitted equations, but it must not claim to reproduce a full neuron, dendrites, AIS, or axonal propagation. An AIS-resolved model remains a separate evidence-gated increment.

No AP-generating code, threshold-only spike event, or generic rodent HH parameter set has been added to HumanJS by this review.

## Sources and provenance

1. Eyal G. et al. (2018). Human Cortical Pyramidal Neurons: From Spines to Spikes via Models. *Frontiers in Cellular Neuroscience* 12:181. https://doi.org/10.3389/fncel.2018.00181
2. ModelDB model 238347, Eyal et al. 2018. https://modeldb.science/238347
3. Wilbers R. et al. (2023). Human voltage-gated Na+ and K+ channel properties underlie sustained fast AP signaling. *Science Advances*. https://doi.org/10.1126/sciadv.ade3300
4. Tian C. et al. (2014). Molecular identity of axonal sodium channels in human cortical pyramidal cells. *Frontiers in Cellular Neuroscience*. https://doi.org/10.3389/fncel.2014.00297
5. Zulaica M. et al. (2026). A Detailed Model for Understanding the Human Neocortex. Preprint. https://doi.org/10.64898/2026.01.29.702592
6. Secondary code-inspection lead only (not a HumanJS implementation dependency): https://github.com/beaherrera/SEF_error-PCs_theta_ERN — public GPL-3.0 repository containing generated EyalEtAl2018 mechanism C files with embedded NMODL text. No code from this repository is copied into HumanJS; exact original source/redistribution terms must be checked at the canonical ModelDB record before any later port.
