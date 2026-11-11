# Human neocortical spike-initiation evidence and implementation boundary

**Reviewed:** 2026-11-10  
**Scope:** somatic action-potential generation and axon-initial-segment (AIS) initiation in human neocortical pyramidal cells.  
**Status:** canonical source audit and selected NEURON reproductions completed. Exploratory HumanJS spike-capable code was subsequently added before the evidence gate was closed; it remains unaccepted and is documented as provisional. This review does not establish biological validation.

## Decision summary

Human data support three distinct evidence layers:

1. **Human somatic current recordings:** Na+ and K+ current kinetics and current densities have been measured in nucleated somatic patches from human L2/L3 pyramidal cells. These data support human-specific somatic channel models, but the excised patch does not contain the AIS.
2. **Human AIS molecular distribution:** immunostaining supports a proximal NaV1.2 and more distal NaV1.6 distribution along pyramidal-cell AISs. It does not measure absolute functional channel density, conductance, gating kinetics, or the complete channel distribution needed for an AIS model.
3. **Human neuron model fits:** detailed six-cell models fit somatic/axonal spike recordings with conductance-based models. The fitted conductance densities are useful constraints, but the authors explicitly assume channel kinetics similar to rodents; these are not measurements of human channel gating.

These sources are complementary, not interchangeable. A single-compartment soma/nucleated-patch equivalent must not be described as an anatomically complete neuron or an AIS-resolved initiation model. An AIS compartment requires additional parameter provenance that is not established by immunostaining alone.

**No intrinsic spike-initiation mechanism is yet scientifically accepted.** Exploratory single-compartment Na+/K+ code now exists in the Rust core, but it was added before the evidence gate below was closed. A bounded somatic-patch-equivalent could become an accepted first increment only after exact human kinetic equations, parameter units, temperature corrections, fit-source provenance, and voltage-clamp behavior have been reconciled. An anatomical soma/AIS model is a separate, stricter milestone.

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

### Canonical Eyal supplementary Table S4: fitted parameter manifest

The original Eyal et al. supplementary PDF (bioRxiv version 267898, 11 pages) was retrieved and Table S4 was extracted. The main-text methods state that the somatic/axonal spiking fit uses 29 free parameters: nine maximum channel conductances, three NaTg kinetic parameters, and two intracellular calcium parameters per compartment (14 × 2), plus one shared leak reversal potential. Table S4 directly confirms that bookkeeping:

- **Nine maximum conductance densities per compartment:** NaTg, SK_E2, SKv3_1, Ca_LVAst, Ca, Nap_Et2, K_Pst, K_Tst, Im.
- **Three NaTg kinetic parameters per compartment:** slopem, vshiftm, vshifth.
- **Two intracellular calcium parameters per compartment:** gamma_CaDynamics_E2 and decay_CaDynamics_E2.
- **One shared parameter:** e_pas, the leak reversal potential used across model compartments.

Therefore, the apparent nine-versus-ten discrepancy is resolved at the parameter level: there are nine explicit maximal-conductance entries, and the intracellular CaDynamics_E2 mechanism contributes two additional fitted parameters. The Table S4 caption calls these “ten membrane ion channels and related parameters”; the actual parameter rows, together with the methods text, give the unambiguous 9+3+2 per compartment. This is (2(9+3+2)+1=29).

#### Axonal parameter set

All conductance values are the source-table units S/cm². Gate voltage shifts/slopes are mV. Calcium decay is ms. Model columns are the six original cells named in Table S4.

| Axonal parameter | Unit | 060303 | 060308 | 060311 | 130303 | 130305 | 130306 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gNaTgbar_NaTg | S/cm² | 4.94 | 5.53 | 6.00 | 5.23 | 3.08 | 4.65 |
| slopem_NaTg | mV | 15.0 | 4.43 | 8.61 | 6.11 | 4.01 | 5.70 |
| vshiftm_NaTg | mV | 8.11 | 13.2 | 8.44 | 15.7 | 10.0 | 9.20 |
| vshifth_NaTg | mV | 0.0102 | 11.9 | 12.0 | 9.87 | 0.0606 | 5.55 |
| gSK_E2bar_SK_E2 | S/cm² | 0.0126 | 0.00640 | 0.000709 | 0.000734 | 0.0684 | 0.0000302 |
| gSKv3_1bar_SKv3_1 | S/cm² | 1.83 | 1.98 | 1.72 | 1.75 | 2.00 | 1.99 |
| gCa_LVAstbar_Ca_LVAst | S/cm² | 0.000999 | 0.0000767 | 0.000295 | 0.000805 | 0.000477 | 0.00000861 |
| gCabar_Ca | S/cm² | 0.000985 | 0.000718 | 0.000784 | 0.000930 | 0.0000709 | 0.000500 |
| gamma_CaDynamics_E2 | — | 0.0429 | 0.0106 | 0.0332 | 0.00876 | 0.000912 | 0.00163 |
| decay_CaDynamics_E2 | ms | 466 | 300 | 587 | 209 | 99.0 | 20.1 |
| gNap_Et2bar_Nap_Et2 | S/cm² | 0.0000671 | 0.000146 | 0.0499 | 0.0413 | 0.0205 | 0.0283 |
| gK_Pstbar_K_Pst | S/cm² | 0.00197 | 0.00711 | 0.000123 | 0.00320 | 0.0991 | 0.00301 |
| gK_Tstbar_K_Tst | S/cm² | 0.000561 | 0.00104 | 0.0953 | 0.0946 | 0.0997 | 0.0248 |
| gImbar_Im | S/cm² | 0.000883 | 0.000805 | 0.0000144 | 0.00000511 | 0.000543 | 0.000855 |

#### Somatic parameter set

| Somatic parameter | Unit | 060303 | 060308 | 060311 | 130303 | 130305 | 130306 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gNaTgbar_NaTg | S/cm² | 0.174 | 0.330 | 0.169 | 0.639 | 0.298 | 0.383 |
| slopem_NaTg | mV | 13.9 | 9.83 | 13.8 | 12.4 | 14.6 | 9.27 |
| vshiftm_NaTg | mV | 8.00 | 7.67 | 16.0 | 16.0 | 16.0 | 8.00 |
| vshifth_NaTg | mV | 11.0 | 11.9 | 11.9 | 0.0214 | 11.6 | 7.02 |
| gSK_E2bar_SK_E2 | S/cm² | 0.0914 | 0.0311 | 0.0999 | 0.0115 | 0.0982 | 0.0966 |
| gSKv3_1bar_SKv3_1 | S/cm² | 0.0929 | 0.132 | 0.0712 | 0.000720 | 0.0519 | 0.0502 |
| gCa_LVAstbar_Ca_LVAst | S/cm² | 0.000997 | 0.000519 | 0.000929 | 0.000995 | 0.000660 | 0.00100 |
| gCabar_Ca | S/cm² | 0.000703 | 0.0000522 | 0.000617 | 0.000000560 | 0.000000474 | 0.0000175 |
| gamma_CaDynamics_E2 | — | 0.000763 | 0.00798 | 0.000528 | 0.0141 | 0.0146 | 0.00599 |
| decay_CaDynamics_E2 | ms | 164 | 197 | 238 | 385 | 431 | 305 |
| gNap_Et2bar_Nap_Et2 | S/cm² | 0.00000214 | 0.0000356 | 0.0000572 | 0.0000676 | 0.0000476 | 0.000226 |
| gK_Pstbar_K_Pst | S/cm² | 0.000000366 | 0.000194 | 0.0000182 | 0.0000742 | 0.00118 | 0.0000837 |
| gK_Tstbar_K_Tst | S/cm² | 0.0480 | 0.0910 | 0.0757 | 0.00159 | 0.0792 | 0.0899 |
| gImbar_Im | S/cm² | 0.000263 | 0.0000110 | 0.000121 | 0.0000307 | 0.000983 | 0.000411 |

#### Shared leak reversal potential

| Parameter | 060303 | 060308 | 060311 | 130303 | 130305 | 130306 |
|---|---:|---:|---:|---:|---:|---:|
| e_pas (mV) | −81.2 | −83.8 | −83.1 | −80.1 | −85.8 | −81.9 |

These values are fitted parameters from multi-objective optimization against the six cells' somatic firing features, not direct measurements of channel protein density or ion-channel abundance. The authors used 1,000 initial candidate models and 500 optimization generations. Active conductances were included in soma and the added 60 μm axonal segment only; they explicitly state that a lack of human dendritic recordings prevented them from constraining active dendritic parameters using soma recordings. Thus Table S4 does not constitute a directly measured human AIS channel map.

The main article states that the gating kinetics were assumed similar to rodent channel kinetics, citing Channelpedia/Ranjan et al. (2011). The human fit therefore combines human AP targets and fitted soma/axon conductance/NaTg-shift parameters with transferred kinetic function forms. Keep those evidence classes separate.

The Table S4 mechanism rows confirm nine fitted maximum-conductance variables. A separate secondary compiled-code registration snapshot lists Ca_HVA as a mechanism registration in addition to the Table S4 mechanisms, but Table S4 has no gCa_HVAbar parameter. Registration in that secondary code snapshot is not proof that Ca_HVA was an optimized active conductance in the six Table S4 models; its role in other model figures or helper simulations remains unresolved.

#### Canonical ModelDB source package and HOC mapping

The official ModelDB archive for model 238347 was retrieved from https://modeldb.science/download/238347. The archive `238347-full.zip` was 139,316,573 bytes, passed `unzip -t`, and had SHA-256 `12dfd8b8fb38b28136d6904da69aaf5e200fa5fb64cd03d845a96d972057354b`. It is not copied into HumanJS. The official archive contains the original `ActiveModels/`, `ActiveMechanisms/`, `Morphs/`, and Figure 7A data.

The six original fitted templates are `cell0603_03_model_476`, `cell0603_08_model_602`, `cell0603_11_model_937`, `cell1303_03_model_448`, `cell1303_05_model_643`, and `cell1303_06_model_263`. Their HOC `insertChannel()` functions insert exactly nine conductance mechanisms in soma and axon: `NaTg`, `Nap_Et2`, `K_Tst`, `K_Pst`, `SKv3_1`, `Ca`, `Ca_LVAst`, `SK_E2`, and `Im`. They also insert `CaDynamics_E2` for intracellular calcium state. `Ca_HVA.mod` exists in the archive but is not inserted or assigned by these six Figure 7A spike-model templates. `NMDA.mod` is a separate synaptic mechanism and is not an active conductance fitted in these six spike models.

Direct comparison of the canonical HOC `biophys()` assignments with the original Table S4 confirms that the six parameter sets map to the six named model templates. Each compartment has nine maximal conductance densities, three NaTg kinetic values (`slopem`, `vshiftm`, `vshifth`), and two calcium-dynamics values (`gamma_CaDynamics_E2`, `decay_CaDynamics_E2`), plus one shared `e_pas`: `2 × (9 + 3 + 2) + 1 = 29`. Table S4 therefore reconciles with the original HOC assignments at the parameter and compartment level. The values are fitted model parameters, not direct channel-density measurements.

The HOC templates set `celsius=37`, `CM=0.488 μF/cm²`, `RM=21,406 Ω·cm²`, and `RA=281.78 Ω·cm`. Apical and basal capacitance and passive leak are scaled by 1.9 beyond 60 μm. Figure 7A replaces the morphology's original axon with two 30 μm stub sections. Active conductances are inserted into soma and this replacement axon; dendrites remain passive. This reduced axon must not be equated with direct human AIS geometry or a fully active dendritic neuron.

The canonical `ActiveMechanisms/README` attributes its channel models to the Blue Brain Project mechanism library. Eyal et al. explicitly describe the kinetic functions as similar to rodent channel kinetics. The resulting models therefore combine human AP recordings and fitted soma/axon conductance parameters with transferred kinetic forms. They are not fully human-measured channel models.

#### Canonical Eyal Figure 7A reproduction

The ten mechanisms actually inserted by the six HOC templates were compiled unchanged, serially, with `nrnivmodl` in NEURON 9.0.2. Compilation succeeded. A Python 3 reproduction then followed the original Figure7A construction, morphology, stub-axon, channel-insertion, temperature, time-step, initial-voltage, and current-clamp stimulus sequence for all six fitted cells. It compared first-spike metrics with the released repeated human traces, applying the same −16 mV junction-potential correction as Figure7A.py.

The reproducible runner and results are recorded in `experiments/HUMAN-L23-SPIKE-MODEL-REPRODUCTION.md` and `experiments/reproduce_eyal_figure7a.py`. The first 0 mV crossing is only an alignment marker, not a claim of biological spike threshold. The comparison showed good correspondence for some cell features and visible timing/width/peak differences in several others. It is a selected-stimulus code/source reproduction, not an independent optimization, exact trace match, or biological validation.


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

The article's Methods describe 14 parameters per channel model: 2 steady-state parameters for each gate (4 total), 4 activation-kinetic parameters, and 6 inactivation-kinetic parameters. The deposited implementation constrains this parameterization further: both pure NMODL files explicitly set the activation prefactors `Ra` and `Rb` equal, and the fitting scripts optimize only `Ra`; the two inactivation steady-state Boltzmann values are assigned from experimental fits rather than passed to the optimizer. Consequently, the scripts expose 13 named Na+ parameter fields when the two fixed inactivation steady-state values are counted, but only 11 optimizer variables (6 inactivation/recovery + 3 activation-kinetic + 2 activation steady-state). The K+ script likewise optimizes 11 variables and assigns the two inactivation steady-state values from experimental fits. This explains the article's 14-parameter description versus the more constrained deposited fit workflow; it does not establish that all 14 were independently optimized in the archived scripts.

The potassium fit-script's apparent final-dictionary conflict is also clarified by execution order. The script applies the first inactivation optimizer result with `mod_cell(cell, inact_fit['params'])`, explicitly reapplies those same six values, then fits activation kinetics and activation steady state. Its trailing “final best fit” dictionary is a bare dictionary literal: it is not assigned, returned, or passed to `mod_cell`. Therefore that literal is not evidence that the alternate six inactivation values were used by the executed fitting sequence. The operative K+ inactivation values in the deposited script are the first optimizer result, which matches Table S2 and the pure `k_human.mod` source.

The K+ fitting script also assigns `cell.h12factor_k_human = 10.5` between the inactivation and activation fits. However, the pure `k_human.mod` mechanism declares `inact_rate_factor` (value 1) and does not declare `h12factor_k_human`; the deposited `channel_tools.py` K+ protocol helper does not read that Python attribute. There is therefore no evidence in the deposited pure-mechanism fitting path that this assignment changes the NMODL kinetics. Treat it as an unconsumed/legacy assignment unless a different mechanism variant or runtime contract is demonstrated. The distinct hybrid current-clamp mechanism remains a separate source variant and must not be conflated with the pure voltage-clamp mechanism.

The pure mechanism inspection also resolves the Table S2 `Rb` omission: both Na+ and K+ NMODL files explicitly assign `Rb = Ra`. The fitting scripts therefore optimize one shared opening/closing prefactor rather than two independent values. The table's single `Ra` row is consistent with the deposited mechanism's equality constraint.

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

The two pure voltage-clamp mechanism files were retrieved from the CC0 Dataverse deposit and decoded as text. Their checksums match the deposit metadata:
- `na_human.mod`, file 318629, 3,602 bytes, SHA1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970`.
- `k_human.mod`, file 318647, 4,220 bytes, SHA1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`.

The alternative current-clamp/hybrid copies are different model variants, not byte-identical duplicates:
- `na_human.mod`, file 318563, 3,711 bytes, SHA1 `ef158980e4bb427c97cfb8f379cd63006130b3b2`; adds a global human-channel fraction na_human_ratio and scales current-clamp conductance by that fraction.
- `k_human.mod`, file 318566, 4,326 bytes, SHA1 `622f7c9867e727a3dc7dea1f9ba2efbfb94cfd3a`; adds a global human-channel fraction k_human_ratio and scales K+ conductance by that fraction.

The pure voltage-clamp files, not the hybrid copies, are the primary source for the human gate equations summarized below. The current-clamp variants must be considered separately when reproducing the AP simulations.

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
- Optimizes six inactivation/recovery parameters (`thi1`, `thi2`, `qi1`, `qi2`, `Rd`, `Rg`), three activation-kinetic parameters (`tha`, `qa`, `Ra`), and two activation steady-state parameters (`th_act_inf`, `q_act_inf`).
- Assigns `h12factor_k_human = 10.5` after the inactivation fit and before activation fitting. The pure mechanism/helper do not show that this attribute affects the model; see the qualification above.

The first inactivation optimizer result matches the Table S2 values `thi1 = 40.5659149 mV`, `thi2 = -75.9382266 mV`, `qi1 = 26.7739292 mV`, `qi2 = 0.40183383 mV`, `Rd = 0.00169014 ms⁻¹`, and `Rg = 0.00049688 ms⁻¹`. The script applies these values to the section before activation fitting. Although a different six-value set appears in the final trailing “best fit” dictionary, that dictionary is a standalone literal and is never assigned or applied. Thus the executable fitting sequence selects the Table S2-matching inactivation result; the alternate literal is a provenance artifact, not an applied final parameter set.

#### Recorded voltage-clamp and current-clamp settings

The deposited `channel_tools.py` defines:
- Na+ channel I–V/kinetic analysis at 25°C, `dt = 0.01 ms`. The activation protocol uses a −120 mV holding level followed by 10 ms test steps from −80 mV to +10 mV in 5 mV increments. The inactivation protocol uses a 1 ms −70 mV holding segment, a 50 ms conditioning segment stepped from −105 mV to −47 mV in 2 mV increments, and a 10 ms test at −10 mV. Recovery uses 2 ms at −120 mV, 10 ms at 0 mV, a variable recovery segment (square-spaced delays), and a 2 ms test pulse. These Na+ voltage-clamp protocols all execute with `h.celsius=25`.
- K+ channel I–V/kinetic analysis at 34°C, `dt = 0.1 ms`, using a 20 ms holding segment, a 500 ms conditioning segment, a 50 ms test segment, and a 100 ms final segment; test voltages span −110 mV to +55 mV in 5 mV increments. The helper uses a double-exponential inactivation analysis and separately represents fast and slow inactivation/recovery. The K+ fitting script initializes `EK = -101 mV` for these voltage-clamp protocols.

The current-clamp helper `cc_tools.py` initializes a single 10 μm compartment with `Ra = 200 Ω·cm`, `Cm = 1 μF/cm²`, `Rm = 10,000 Ω·cm²` and `g_pas = 1/Rm`, `h.celsius = 34`, and reversals offset from the nominal current-clamp values to account for the liquid-junction potential. It sets channel voltage shifts to −10 mV when moving between the voltage-clamp and current-clamp internal solutions; it adds +15 mV to the nominal `ENa = 53 mV`, `EK = -101 mV`, and `Epas = -85 mV` in that initialization path. The voltage-clamp `Na_IV` and `K_IV` helpers themselves do not apply a voltage shift.

The separate conductance-density fitting helper adjusts human and mouse channel fractions and minimizes current-clamp AP waveform differences in amplitude, rise speed, and fall speed. The article describes fits to cross-species mean AP features (48.4 mV, 420 mV/ms, and 73.1 mV/ms), followed by a grid of channel-fraction combinations. The resulting AP-model conductance densities are therefore outputs of a particular optimization target; they are not direct patch measurements.

The original pure `na_human.mod` and `k_human.mod` files were retrieved from the CC0 deposit, checksum-verified against the Dataverse metadata, compiled unchanged, and inspected in NEURON 9.0.2. Their complete rate equations, units, temperature rules, and explicit `Rb = Ra` assignments are recorded below. The K+ script's later final printed inactivation/recovery dictionary still differs from the pure K+ file and Table S2. The paper's 14-parameter methods count also remains unreconciled with the source fit stages; neither discrepancy is silently resolved here.

### Original human channel mechanisms: equations and parameter values

The deposited pure voltage-clamp files are the authoritative equation sources inspected for this review. They are based on Mainen/Kole Hodgkin–Huxley rate forms, but use separately fitted human steady-state Boltzmann functions. The equations below are transcribed from Dataverse file 318629 (na_human.mod) and file 318647 (k_human.mod), not inferred from a secondary code snapshot.

#### Human sodium mechanism (na_human.mod)

gbar = 40 pS/μm² in the file's parameter declaration; this is a mechanism starting/default value, not the Table S2 spike-model fitted density and not a universal human default.

| Parameter | File value | Meaning |
|---|---:|---|
| th_act_inf | −42.2914566895 | Activation steady-state half-voltage, mV |
| q_act_inf | 10.2311528961 | Activation steady-state slope, mV |
| tha | −58.5923560662 | Activation rate-function voltage parameter, mV |
| qa | 9.21455371864 | Activation rate-function slope, mV |
| Ra, Rb | 0.213984927041 | Opening/closing rate prefactors, ms⁻¹; the file explicitly sets them equal |
| th_inact_inf | −64.48 | Inactivation steady-state half-voltage, mV |
| q_inact_inf | 11.02 | Inactivation steady-state slope, mV |
| thi1 | −39.2986769113 | Inactivation time-constant voltage parameter, mV |
| thi2 | −77.1667453246 | Recovery time-constant voltage parameter, mV |
| qi1, qi2 | 7.21636386593; 4.74945004839 | Inactivation/recovery rate slopes, mV |
| Rd, Rg | 0.0476391878314; 0.0119516550234 | Inactivation/recovery rate prefactors, ms⁻¹ |
| temp, q10 | 25°C; 2.3 | Reference temperature and temperature coefficient |
| vShift_inact | 0 mV | Additional shift applied only to the inactivation gate |

The temperature adjustment is T_adj = q10 ^ ((T - T_ref) / 10).

The activation rates are a_m = trap0(V, tha, Ra, qa) and b_m = trap0(-V, -tha, Rb, qa). The activation time constant is tau_m = 1 / (T_adj * (a_m + b_m)), while its steady state is the separately fitted m_inf = 1 / (1 + exp((th_act_inf - V) / q_act_inf)).

For inactivation, V_s = V - vShift_inact, a_h = trap0(V_s, thi1, Rd, qi1), and b_h = trap0(-V_s, -thi2, Rg, qi2). Its time constant is tau_h = 1 / (T_adj * (a_h + b_h)), and its steady state is h_inf = 1 / (1 + exp((V_s - th_inact_inf) / q_inact_inf)).

The gate states follow first-order relaxation: m' = (m_inf - m) / tau_m and h' = (h_inf - h) / tau_h. The file initializes both gates at their steady-state values. Its conductance/current expression is g_Na = T_adj * gbar_Na * m^3 * h and I_Na = 1e-4 * g_Na * (V - E_Na), using the file's density/current conversion conventions.

#### Human potassium mechanism (k_human.mod)

gbar = 40 pS/μm² in the file's parameter declaration. The K+ channel is modeled as one activation gate and two inactivation gates representing fast and slow inactivating fractions plus a non-inactivating fraction.

| Parameter | File value | Meaning |
|---|---:|---|
| th_act_inf | −18.4061635398 | Activation steady-state half-voltage, mV |
| q_act_inf | 19.1995502734 | Activation steady-state slope, mV |
| tha, thb | −29.9617980169 each | Activation/deactivation rate voltage parameters, mV |
| qa, qb | 6.59040568888 each | Activation/deactivation slopes, mV |
| Ra, Rb | 0.0184592505854 each | Opening/closing rate prefactors, ms⁻¹; explicitly equal |
| th_inact_inf | −52.61 | Inactivation steady-state half-voltage, mV |
| q_inact_inf | 13.09 | Inactivation steady-state slope, mV |
| thi1, thi2 | 40.5659148938; −75.9382265931 | Inactivation/recovery time-constant voltage parameters, mV |
| qi1, qi2 | 26.7739292447; 0.401833827494 | Inactivation/recovery slopes, mV |
| Rd, Rg | 0.00169014356593; 0.000496879131264 | Inactivation/recovery rate prefactors, ms⁻¹ |
| h2tau_inact | 450 | Slow-inactivation time constant, ms |
| h2tau_inact_rec | 2789.79294281 | Slow-inactivation recovery time constant, ms |
| prop_inact, prop_h2 | 0.85; 0.4 | Fraction inactivating; fraction of that assigned to slow inactivation |
| inact_rate_factor | 1 | Scaling factor for inactivation during the inactivation branch |
| temp, q10 | 34°C; 2.3 | Reference temperature and temperature coefficient |

The activation time constant is tau_m = 1 / (T_adj * (a_m + b_m)), and m_inf is the separate Boltzmann activation function. Inactivation uses a_h = trap0(V, thi1, Rd, qi1) and b_h = trap0(-V, -thi2, Rg, qi2), with tau_h1 = 1 / (T_adj * (a_h + b_h)) and the separate inactivation Boltzmann h_inf. The slow gate time constant is set to 450 ms while inactivating and 2789.79294281 ms while recovering; this file does not fit a separate voltage-dependent slow-gate kinetic function.

The total K+ conductance is exactly decomposed as:

    g_K = gbar_K * m^2 * [
        h1 * prop_inact * (1 - prop_h2)
      + h2 * prop_inact * prop_h2
      + (1 - prop_inact)
    ]
    I_K = 1e-4 * g_K * (V - E_K)

Unlike the Na+ mechanism, the K+ source does not multiply gbar_K by T_adj; the Q10 factor appears in the K+ gate time constants.

**Published-model limitation:** the article's Discussion explicitly states that the fitted HH channel models captured many measured properties but did not accurately reproduce all of them, specifically identifying potassium-channel inactivation mechanisms. The authors connect this limitation to the relatively poor fit of simulated K+ currents and AP falling speeds. This is direct evidence that the deposited K+ HH mechanism is an imperfect approximation of the measured human K+ behavior, not a definitive or fully validated kinetic description. The HumanJS exploratory implementation must retain this limitation even if its own software tests pass. Source: Wilbers et al. (2023), *Science Advances*, DOI https://doi.org/10.1126/sciadv.ade3300.

#### Unresolved numerical issue in both original trap0 functions

Both original human mechanism files contain this piecewise function (spacing normalized):

    trap0(v, th, a, q):
        if abs((v + th) / q) > 1e-6:
            return a * (v - th) / (1 - exp(-(v - th) / q))
        else:
            return q * (1 + (v - th) / (2*q))

The source comments out an earlier intended fallback a*q, but the active fallback omits the prefactor a. Its branch test uses v + th, whereas the main expression's removable singularity is at v = th. The analytic limit of the main expression at v = th is a*q. Thus the branch condition and active fallback are not an evident implementation of that limit. The comment says the earlier version trapped near zero voltage; that explanation does not establish that the replacement is mathematically or numerically correct.

The original pure files were compiled unchanged with `nrnivmodl` and probed in NEURON 9.0.2. Direct calls to the compiled `trap0` function at each stored singular voltage returned non-finite values. With `usetable_na_human=0`, direct Na+ rate evaluation at its three singular voltages also returned non-finite time constants. The Na+ source enables a lookup table from −120 to +100 mV with 199 subdivisions (200 nodes); scanning every compiled table node produced finite activation and inactivation time constants. The three Na+ singularities are off-grid; the nearest grid node to the `thi1` singularity is approximately 0.0022 mV away. The K+ table block is commented out, so its rates are evaluated directly; exact K+ gate singularities return non-finite time constants. At the opposite-sign branch triggers, the compiled K+ runtime produced negative `h1tau` values of approximately −0.728 ms and −0.133 ms for the inactivation and recovery cases. This identifies a real source/runtime edge case, but does not establish that all published model simulations fail: the Na+ default table avoids non-finite values at its grid nodes, while K+ evaluations need more careful voltage/protocol coverage. No correction was applied to the source files, and HumanJS must not silently patch them and claim exact source reproduction.

#### What the deposited per-cell workbooks establish

The public deposit includes per-cell summary workbooks:
- data_fig3.xlsx, file 318666: 34 records overall, including 19 human Na+ recordings. All 19 have activation steady-state fits; the paper reports Vhalf_act = −32.13 ± 4.86 mV, n=19. The workbook contains 19 inactivation fit rows, but one record (H20.29.188.11.42.07.nwb) has inactivation fit quality 0.8600. Excluding that row yields mean −66.0018 mV and SD 7.8217 mV across 18 records, matching the paper's reported inactivation result (−66.00 ± 7.82 mV, n=18). The workbook does not itself state the exclusion rule; the match is a reconstruction from its per-record values and fit-quality column.
- data_fig4.xlsx, file 318667: 43 records overall, including 13 human K+ recordings. The 13 human activation fits give Vhalf_act = −3.0315 ± 5.9490 mV and slope 13.8708 ± 1.3453 mV. Eleven human records contain inactivation fits, giving Vhalf_inact = −52.6861 ± 5.9748 mV and slope 12.8032 ± 1.8705 mV. These reproduce the corresponding published sample counts and closely match the reported summary values.

The per-cell workbook summaries are not the raw whole-cell/nucleated-patch current traces. Their filename columns identify the source NWB recordings, but those original NWB trace files were not present among the 65 public files in the version-3.0 file listing examined here. Consequently, the original optimizer has not been independently rerun from raw trace data.

The pure Wilbers mechanisms were compiled in the cloud VM using NEURON 9.0.2 and their direct rate-function and lookup-grid behavior was exercised. The full Wilbers voltage-clamp analysis workflow and current-clamp hybrid AP fit were not rerun; the public per-cell workbooks are summary fits, not raw current traces, and the original NWB traces were not present in the 65-file Dataverse v3.0 listing inspected. The NEURON runtime audit is therefore a compiled-source edge-case test, not a reproduction of the paper's channel-fitting experiments.

The current-clamp helper uses a separate single-compartment model with 10 μm length/diameter, 200 Ω·cm axial resistivity, 1 μF/cm² capacitance, Rm=10,000 Ω·cm², g_pas=1/Rm, h.celsius=34, and E_K=-101+15 mV, E_Na=53+15 mV, E_pas=-85+15 mV. It applies −10 mV voltage shifts to the channels to account for the 15 mV current-clamp liquid-junction potential versus 5 mV during voltage clamp. The current-clamp helper fits conductance densities to AP features averaged 50/50 between human and mouse data; those resulting densities are model-fit quantities, not direct human channel-density measurements. The pure channel defaults gbar=40 pS/μm² must therefore not be substituted for final AP-fit conductance densities.

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
2. **Resolve Wilbers source/runtime discrepancies before porting.** The pure human mechanisms have been compiled and their `trap0` edge cases tested in NEURON 9.0.2. Reconcile the K+ script's final dictionary and unused `h12factor_k_human` assignment with the source file and paper; reconcile the paper's 14-parameter methods count with the staged fit variables. Do not silently fix the source's branch logic and call it an exact reproduction.
3. **Reconcile conductance density.** Keep the measured human somatic patch densities separate from the much larger fitted Na+ conductance used in the paper's single-compartment AP simulation. Do not convert one into the other without reproducing and documenting the authors' fitting assumptions.
4. **Keep AIS evidence separate.** Human NaV1.2/NaV1.6 staining supplies spatial subtype evidence, but not absolute conductance or gating. Do not invent AIS channel densities, kinetics, or gradients from immunostaining.
5. **Retain the canonical Eyal source audit.** Table S4 is mapped to the six original HOC soma/axon parameter sets. The nine inserted conductance mechanisms and separate CaDynamics_E2 module are identified; Ca_HVA and NMDA are not inserted by those six spike templates. The Figure 7A reproduction report records the executable test and its limitations. Keep rodent-derived kinetic functions explicitly marked as transferred model assumptions.
6. **Add causal validation targets only after parameter provenance is closed.** Candidate targets include human somatic AP threshold/onset, waveform height and half-width, afterhyperpolarization, repetitive firing/adaptation, and availability/recovery behavior under matched voltage protocols. Passing software tests would still not constitute biological validation.

A first somatic-patch-equivalent model may become defensible using the direct human channel recordings and the paper's fitted equations, but it must not claim to reproduce a full neuron, dendrites, AIS, or axonal propagation. An AIS-resolved model remains a separate evidence-gated increment.

Exploratory AP-generating code now exists in `crates/humanjs-core/src/ion_channels.rs`; it is not accepted as a scientifically validated human mechanism and must not be described as one. It uses a stable analytic-limit interpretation of `trap0`, Table S2 / first-optimizer K+ values despite the later fit-dictionary discrepancy, and current-clamp fitted conductance densities that were optimized against cross-species mean AP features. The implementation is one lumped compartment, not an anatomical soma/AIS neuron. Its software tests do not replace voltage-clamp protocol reproduction or biological validation. See ADR-016 and the architecture validation gate. The canonical Eyal source audit and selected Figure 7A reproduction remain separate; neither is treated as HumanJS implementation or biological validation.

## Sources and provenance

1. Eyal G. et al. (2018). Human Cortical Pyramidal Neurons: From Spines to Spikes via Models. *Frontiers in Cellular Neuroscience* 12:181. https://doi.org/10.3389/fncel.2018.00181
2. ModelDB model 238347, Eyal et al. 2018. https://modeldb.science/238347
3. Wilbers R. et al. (2023). Human voltage-gated Na+ and K+ channel properties underlie sustained fast AP signaling. *Science Advances*. https://doi.org/10.1126/sciadv.ade3300
4. Tian C. et al. (2014). Molecular identity of axonal sodium channels in human cortical pyramidal cells. *Frontiers in Cellular Neuroscience*. https://doi.org/10.3389/fncel.2014.00297
5. Zulaica M. et al. (2026). A Detailed Model for Understanding the Human Neocortex. Preprint. https://doi.org/10.64898/2026.01.29.702592
6. Secondary code-inspection lead only (not a HumanJS implementation dependency): https://github.com/beaherrera/SEF_error-PCs_theta_ERN — public GPL-3.0 repository containing generated EyalEtAl2018 mechanism C files with embedded NMODL text. No code from this repository is copied into HumanJS; exact original source/redistribution terms must be checked at the canonical ModelDB record before any later port.
