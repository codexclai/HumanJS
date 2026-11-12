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

The K+ fitting script also assigns `cell.h12factor_k_human = 10.5` between the inactivation and activation fits. Direct inspection of all three deposited K+ NMODL variants used in this audit (pure `k_human.mod`, hybrid `k_human.mod`, and `k_human_hm12inf.mod`) shows that the only occurrence of `h12factor` is the commented-out line `:h2tau = h1tau * h12factor`. It is not declared in any active `NEURON` or `PARAMETER` block, and `channel_tools.py` does not read the Python attribute. The assignment therefore has no active mechanism path in these deposited variants; it is a stale/unused fit-script assignment, not an unresolved kinetic multiplier.

The pure mechanism inspection also resolves the Table S2 `Rb` omission: both Na+ and K+ NMODL files explicitly assign `Rb = Ra`. The fitting scripts therefore optimize one shared opening/closing prefactor rather than two independent values. The table's single `Ra` row is consistent with the deposited mechanism's equality constraint. The pure Na+ and K+ NMODL `PARAMETER` blocks explicitly annotate `Ra`, `Rb`, `Rd`, and `Rg` as `(/ms)`, matching Table S2. However, the source `trap0` equation is `a * (v - th) / (1 - exp(-(v - th)/q))`: its denominator is dimensionless while its numerator is in mV. For the result to be a transition rate in ms⁻¹, dimensional analysis requires the coefficient to be mV⁻¹·ms⁻¹, not the source-declared ms⁻¹. The `FUNCTION trap0` arguments have no explicit unit declarations, and the source `UNITS` block does not resolve this coefficient mismatch. The unchanged mechanisms compile, but compilation alone does not establish dimensional consistency. HumanJS retains the deposited numeric values without rescaling and gives the internal coefficient the equation-consistent mV⁻¹·ms⁻¹ type; this is an explicit dimensional reinterpretation, not an exact reproduction of the source's unit declaration.

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

The fitted values printed in the script match the corresponding Table S2 human entries for the three optimization stages: `thi1 = -39.2986769 mV`, `thi2 = -77.1667453 mV`, `qi1 = 7.21636387 mV`, `qi2 = 4.74945005 mV`, `Rd = 0.04763919 ms⁻¹`, `Rg = 0.01195166 ms⁻¹`, `tha = -58.5923561 mV`, `qa = 9.21455372 mV`, `Ra = 0.21398493 ms⁻¹`, `th_act_inf = -42.2914567 mV`, and `q_act_inf = 10.2311529 mV`. The script's explicit parameter names resolve the repeated Table S2 row label. The article's 14-parameter description includes two inactivation steady-state values assigned from experimental fits and an independent `Rb`; the deposited mechanism constrains `Rb = Ra`, leaving 11 optimizer variables. The script exposes 13 named Na+ fields only when those two fixed inactivation steady-state assignments are counted.

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

The original pure `na_human.mod` and `k_human.mod` files were retrieved from the CC0 deposit, checksum-verified against the Dataverse metadata, compiled unchanged, and inspected in NEURON 9.0.2. Their complete rate equations, temperature rules, and explicit `Rb = Ra` assignments are recorded below. The K+ script's trailing alternate inactivation/recovery dictionary is a bare literal and is never assigned or applied; the executable script applies the first optimizer result matching Table S2. The article's 14-parameter description versus the deposited 11-variable optimizer sequence is explained by experimentally fixed inactivation steady states and `Rb = Ra`. The printed Table S2 rate-prefactor unit `ms⁻¹` is dimensionally incomplete for `trap0`, whose numerator is voltage-valued; HumanJS therefore interprets the coefficient as mV⁻¹·ms⁻¹ to yield transition rates in ms⁻¹.

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
| Ra, Rb | 0.213984927041 | Opening/closing prefactors; source-declared /ms (equation requires mV⁻¹·ms⁻¹); the file explicitly sets them equal |
| th_inact_inf | −64.48 | Inactivation steady-state half-voltage, mV |
| q_inact_inf | 11.02 | Inactivation steady-state slope, mV |
| thi1 | −39.2986769113 | Inactivation time-constant voltage parameter, mV |
| thi2 | −77.1667453246 | Recovery time-constant voltage parameter, mV |
| qi1, qi2 | 7.21636386593; 4.74945004839 | Inactivation/recovery rate slopes, mV |
| Rd, Rg | 0.0476391878314; 0.0119516550234 | Inactivation/recovery prefactors; source-declared /ms (equation requires mV⁻¹·ms⁻¹) |
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
| Ra, Rb | 0.0184592505854 each | Opening/closing prefactors; source-declared /ms (equation requires mV⁻¹·ms⁻¹); explicitly equal |
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
2. **Preserve exact Wilbers parameter provenance and validate protocol behavior.** The pure human mechanisms have been compiled and their `trap0` edge cases tested in NEURON 9.0.2. The K+ script applies the first optimizer result matching Table S2; its trailing alternate dictionary is not applied. `h12factor_k_human` is not declared in the pure mechanism or consumed by the deposited protocol helper. The article's 14-parameter description maps to an 11-variable deposited optimizer because two inactivation steady-state values are fixed from experiments and `Rb = Ra`. Independently reproduce the voltage-clamp activation, inactivation, and recovery protocols, including the source singularity neighborhoods and dimensional interpretation of `trap0`. Do not silently fix the source's branch logic and call it an exact reproduction.
3. **Reconcile conductance density.** Keep the measured human somatic patch densities separate from the much larger fitted Na+ conductance used in the paper's single-compartment AP simulation. Do not convert one into the other without reproducing and documenting the authors' fitting assumptions.
4. **Keep AIS evidence separate.** Human NaV1.2/NaV1.6 staining supplies spatial subtype evidence, but not absolute conductance or gating. Do not invent AIS channel densities, kinetics, or gradients from immunostaining.
5. **Retain the canonical Eyal source audit.** Table S4 is mapped to the six original HOC soma/axon parameter sets. The nine inserted conductance mechanisms and separate CaDynamics_E2 module are identified; Ca_HVA and NMDA are not inserted by those six spike templates. The Figure 7A reproduction report records the executable test and its limitations. Keep rodent-derived kinetic functions explicitly marked as transferred model assumptions.
6. **Add causal validation targets only after parameter provenance is closed.** Candidate targets include human somatic AP threshold/onset, waveform height and half-width, afterhyperpolarization, repetitive firing/adaptation, and availability/recovery behavior under matched voltage protocols. Passing software tests would still not constitute biological validation.

A first somatic-patch-equivalent model may become defensible using the direct human channel recordings and the paper's fitted equations, but it must not claim to reproduce a full neuron, dendrites, AIS, or axonal propagation. An AIS-resolved model remains a separate evidence-gated increment.

Exploratory AP-generating code now exists in `crates/humanjs-core/src/ion_channels.rs`; it is not accepted as a scientifically validated human mechanism and must not be described as one. It uses a stable analytic-limit interpretation of `trap0`, K+ values that the deposited script actually applies (matching Table S2), and current-clamp fitted conductance densities optimized against cross-species mean AP features. The article's 14-parameter model description is distinct from the 11 independent optimizer variables in the deposited scripts. The implementation is one lumped compartment, not an anatomical soma/AIS neuron. Its software tests do not replace voltage-clamp protocol reproduction or biological validation. See ADR-016 and the architecture validation gate. The canonical Eyal source audit and selected Figure 7A reproduction remain separate; neither is treated as HumanJS implementation or biological validation.

## Sources and provenance

1. Eyal G. et al. (2018). Human Cortical Pyramidal Neurons: From Spines to Spikes via Models. *Frontiers in Cellular Neuroscience* 12:181. https://doi.org/10.3389/fncel.2018.00181
2. ModelDB model 238347, Eyal et al. 2018. https://modeldb.science/238347
3. Wilbers R. et al. (2023). Human voltage-gated Na+ and K+ channel properties underlie sustained fast AP signaling. *Science Advances*. https://doi.org/10.1126/sciadv.ade3300
4. Tian C. et al. (2014). Molecular identity of axonal sodium channels in human cortical pyramidal cells. *Frontiers in Cellular Neuroscience*. https://doi.org/10.3389/fncel.2014.00297
5. Zulaica M. et al. (2026). A Detailed Model for Understanding the Human Neocortex. Preprint. https://doi.org/10.64898/2026.01.29.702592
6. Secondary code-inspection lead only (not a HumanJS implementation dependency): https://github.com/beaherrera/SEF_error-PCs_theta_ERN — public GPL-3.0 repository containing generated EyalEtAl2018 mechanism C files with embedded NMODL text. No code from this repository is copied into HumanJS; exact original source/redistribution terms must be checked at the canonical ModelDB record before any later port.


### Deposited K+ voltage-clamp fitting protocol and objective audit (2026-11-11)

The original public DataverseNL dataset (DOI: https://doi.org/10.34894/L5J0SD, version 3.0, CC0-1.0) was re-enumerated from its live 65-file public inventory. The relevant deposited source files are `fit_k_hh_cma_human.py` (file 326237), `channel_tools.py` (326242), `channel_kinetics.py` (326241), and the pure `k_human.mod` (318647). The pure mechanism and fitting helper were retrieved directly from the Dataverse access API and inspected as source text.

#### Model-side clamp waveforms in `channel_tools.py`

All K+ clamp protocols set `h.celsius = 34` °C. The source helper uses:

- **Activation and inactivation family (`K_IV`):** 20 ms at −140 mV, 500 ms at each test voltage (−110 to +55 mV in 5-mV increments), 50 ms at +60 mV, then 100 ms at −140 mV. The activation conductance is estimated from the peak current during the variable-voltage step. The +60-mV test step after each conditioning voltage estimates steady-state inactivation. The fit helper's coarser `K_IV_ss` version uses 10-mV increments from −110 to +50 mV.
- **Recovery from inactivation (`K_recovery`):** 2 ms at −120 mV, 5,000 ms at +40 mV to inactivate the channels, a variable recovery step at −90, −85, −80, −75, or −70 mV, then a 5-ms +40-mV test pulse. Recovery delays are `linspace(2, 92, 10)^2`: 4, 144, 484, 1,024, 1,764, 2,704, 3,844, 5,184, 6,724, and 8,464 ms. The helper fits a double exponential to the recovered test-pulse amplitudes.
- **Deactivation (`K_deact`):** the helper defines 2 ms at −120 mV, 5 ms at +60 mV, then 200 ms at test voltages −90 to −35 mV. This plotting helper is commented out in `K_IV` and is not one of the three criteria used by the human K+ optimizer.

The `K_IV` simulation uses 0.1-ms time steps; recovery uses 0.5-ms steps. These are the deposited model-evaluation settings, not a claim that the original recording acquisition used those time steps.

#### What the human K+ optimizer actually fits

`fit_k_hh_cma_human.py` runs the following sequence:

1. Fit six inactivation/recovery parameters: `thi1`, `thi2`, `qi1`, `qi2`, `Rd`, and `Rg`, against fast inactivation, slow inactivation, and fast recovery criteria (50 generations).
2. Apply that result to the cell.
3. Assign `h12factor_k_human = 10.5`; this remains unused by the inspected pure/hybrid mechanisms.
4. Fit activation-rate parameters `tha`, `qa`, and `Ra`.
5. Fit the activation steady-state parameters `th_act_inf` and `q_act_inf`.

The inactivation/recovery fit reports component scores of 0.0721 (fast inactivation), 2.4386 (slow inactivation), and 0.00235 (fast recovery). The helper's score is the mean squared deviation normalized by the experimental standard deviation. The fit weights are −1, −0.05, and −1 respectively, so the slow-inactivation component has one-twentieth the weight of fast inactivation and fast recovery. This is a source-reported optimizer score, not a new independent fit.

Two important provenance limitations are now explicit:

- The fast-recovery objective uses a hard-coded target of 236.824345 ms, commented in the source as the **mean of human and mouse values**, even when `species='H'` is passed for the human fit. Thus this objective is pooled across species rather than a human-only recovery target.
- The mechanism fixes `h2tau_inact = 450 ms` and `h2tau_inact_rec = 2789.7929 ms`; these are not among the six inactivation optimizer variables. The slow recovery time constant is therefore a fixed mechanism setting, not an independently optimized human parameter in this fitting script.

The `K_IV_ss` function's default criterion list contains an adjacent-string concatenation typo between `'tau_inact_slow'` and `'tau_inact_rec_fast'`. The actual human fitting script passes its own explicit `crits` list, so this default-list defect does not alter the recorded human optimizer call.

#### Public-data availability boundary

The current version-3 Dataverse inventory contains 65 public files, but it does **not** contain the `Experimental means/k_tau_act.csv`, `k_tau_inact_fast.csv`, `k_tau_inact_slow.csv`, or other `Experimental means` files read by `channel_tools.py`. The K plotting script `plots_fig4.py` references `data_fig5.xlsx`, which is also absent from the public inventory. The available `K_data_fig2.xlsx` is an AP-clamp amplitude workbook (human/mouse current amplitudes over repeated AP waveforms), not the missing voltage-step kinetic dataset. No raw NWB K+ voltage-clamp current traces were present in the inspected 65-file listing. The publisher's article PDF states that all data, model files, and scripts are publicly available in DataverseNL (DOI `10.34894/L5J0SD`) and that the data needed to evaluate the paper's conclusions are in the article and/or Supplementary Materials. This statement is consistent with the deposited summary data and code; it does not imply that the missing per-cell K kinetic CSVs or raw voltage-clamp traces are among the 65 files in version 3.0. The distinction here is between public summary/model reproducibility and raw-trace refitting, not a claim that the authors withheld data.

Consequently, the model-side clamp waveforms and optimizer logic are source-audited, but numerical replay against the original per-voltage K+ current traces or exact experimental-mean CSV targets is not possible from the public version examined. A Rust-side replay of the deposited `K_IV_ss` protocol now compares the model's full steady-state voltage series with the paper's group-level human summaries. Using transparent half-range interpolation (not the source's nonlinear least-squares fit), the model gives an activation midpoint of −3.25 mV, an inactivation midpoint of −51.48 mV, and availability at −80 mV of 0.936. These fall within the published human group mean ± SD (−3.03 ± 5.95 mV, n=13; −52.69 ± 5.97 mV, n=11; and 0.94 ± 0.05, respectively). The test also checks the source activation, inactivation, and recovery command sequences using exact first-order gate updates and independent reference conductance fractions. This is a coarse group-summary consistency check and a software protocol/equation regression, not a refit to raw traces or validation of fast/slow kinetic time constants. The recovery regression now covers the complete deposited 5 × 10 grid: all five recovery voltages (−90, −85, −80, −75, and −70 mV) at all ten recovery delays (4–8,464 ms). Each of the 50 normalized test-pulse peak conductances is checked against independently calculated first-order gate reference values, and recovery is required to increase monotonically with delay at each voltage. This closes a software protocol-coverage gap; the reference values are model-side calculations, not experimental observations. The current HumanJS K+ implementation must therefore remain exploratory and unaccepted.





#### Publisher supplementary Figure S5: verified series mapping, digitization, and source-protocol reproduction

The publisher supplement was retrieved from the **new PMC Article Datasets AWS distribution**, rather than the retired PMC FTP/legacy-cloud endpoints. PMC article `PMC10569700.1` is CC BY. The official supplement object is [sciadv.ade3300_sm.pdf](https://pmc-oa-opendata.s3.amazonaws.com/PMC10569700.1/sciadv.ade3300_sm.pdf), 1,468,232 bytes, 13 pages; SHA-256 `dfa1daaf4dd0e3979bac84b9cb8b1874c4514d40588969a21d7766a7f12f2a1d` (JATS-reported MD5 `f12cab61e8f8206001a29cd90a24651b`). The original Figure S5 graphic is on PDF page 7.

The page was rendered locally from the downloaded PDF. The figure legend and caption visually establish the series identities:
- Red continuous line: human model; blue continuous line: mouse model.
- Red open-circle markers: human experimental group means.
- Blue cross markers: mouse experimental group means.
- The caption states that markers represent means of human (o) and mouse (x) experimental data. It repeats panel label “(I)” for fast inactivation; the actual plotted panel is visibly labelled **J**, between activation panel I and slow-inactivation panel K.

**Experimental marker evidence record:** 50 experimental marker values are now recorded across panels I, J, K, M, and N. Panels I/J/K contain 46 manually digitized marker centers; panels M/N contain four exact experimental means transcribed from the deposited plotting source, not pixel-digitized. All CSVs preserve the PDF hash and species/marker mapping:
- `research/HUMAN-L23-WILBERS-FIG-S5-I-ACTIVATION.csv`: seven voltages per species (−10 to +50 mV). Approximate human means decrease from 3.36 ms at −10 mV to 0.58 ms at +50 mV; mouse means decrease from 7.76 to 0.93 ms.
- `research/HUMAN-L23-WILBERS-FIG-S5-J-FAST-INACTIVATION.csv`: six voltages per species (0 to +50 mV). Human and mouse markers are retained separately; do not infer significance from the plotted means alone.
- `research/HUMAN-L23-WILBERS-FIG-S5-K-SLOW-INACTIVATION.csv`: ten voltages per species (−30 to +60 mV). The experimental points vary broadly with voltage and species; the model's slow-inactivation time constant is fixed at 450 ms.
- `research/HUMAN-L23-WILBERS-FIG-S5-M-FAST-RECOVERY.csv`: exact experimental means hard-coded in `channel_tools.py`, function `K_IV`: human 228.52749381071555 ms and mouse 245.12119700268607 ms at −80 mV.
- `research/HUMAN-L23-WILBERS-FIG-S5-N-SLOW-RECOVERY.csv`: exact `K_IV` means: human 1999.7294967866596 ms and mouse 3579.8563888349777 ms at −80 mV. Their arithmetic mean is exactly 2789.7929428108187 ms, the shared model slow-recovery constant.
- The arithmetic mean of the two fast-recovery means is 236.82434540670081 ms, matching the optimizer's pooled human/mouse fast-recovery target (236.824345 ms). These exact identities confirm the provenance of both pooled recovery constants. They are not human-only targets.

For panels I/J/K, uncertainties are conservative plot-reading/calibration estimates (I ±1 mV/±0.25 ms; J ±1 mV/±2 ms; K ±2.5 mV/±25 ms). They are **not biological SD or SEM**. The M/N CSVs transcribe exact source-script constants; their zero transcription uncertainty means only that the code values were copied exactly, not that the experimental means have zero biological uncertainty. The group means are not raw cell-level observations or the absent Dataverse source CSV values.

**Critical protocol distinction resolved:** panel I is not a direct plot of the activation gate's (m)-gate `mtau`. The deposited `channel_tools.py` (Dataverse file 326242) `K_IV` routine simulates the K current with a voltage clamp (34°C, `dt=0.1 ms`, command durations [20, 500, 50, 100] ms, holding/test/recovery commands [−140, test voltage, +60, −140] mV). It fits the rising **current** before its peak using `get_tau_act`, which fits (a e^{-t/\tau}+ss) and accepts `R² > 0.95`. Comparing the plotted current-fit `tau_act` to the direct gate `mtau` is invalid. A previous gate-`mtau` comparison and its inferred voltage-shift sensitivity are withdrawn.

The K voltage-clamp scripts create cells with `ek=-101 mV`; the MOD default `vshift=0 mV` is used by `K_IV`. The separate current-clamp helper's −10-mV shift is not the Figure S5 voltage-clamp setting. The Rust voltage-clamp regression replays the current waveform and the source exponential-fit procedure, rather than treating gate `mtau` as the plotted quantity. It also accumulates the 0.1-ms clock as NEURON does: the strict source mask `t>20.4` includes the nominal 20.4-ms sample because the cumulative floating-point time is slightly above 20.4. Independent SciPy references for the human current-fit curve at −10, 0, 10, 20, 30, 40, and 50 mV are approximately 3.284746, 2.298530, 1.700319, 1.330597, 1.082613, 0.902015, and 0.771108 ms. The Rust test reproduces these values within 0.01 ms; their RMSE against the digitized human experimental markers is about 0.145 ms. This is a source-equation/protocol regression, not independent biological validation; NEURON itself has not been executed in this environment.

**Model-curve provenance issue, now strongly supported:** the Dataverse contains no dedicated Figure S5 plotting script. The available `fit_k_hh_cma_human.py` (file 326237) and `fit_k_hh_cma_mouse.py` (file 326240) each call `K_IV(cell)` exactly once before the activation optimizer. Human `k_human.mod` defaults match the later fit. Mouse `k_mouse.mod` default activation `Ra=0.0167/ms` differs from the later optimizer result `Ra=0.020746083599133762/ms`. The blue model line was sampled at six unmarked intermediate voltages (−5, +5, +15, +25, +35, +45 mV) from the page-7 raster and compared with current-fit simulations using both parameter snapshots. Pixel RMSE is 5.35 px for the pre-fit default and 36.06 px for the post-fit optimizer value; the comparison is recorded in `research/HUMAN-L23-WILBERS-FIG-S5-I-MOUSE-MODEL-PREFIT-CHECK.csv` and `research/HUMAN-L23-WILBERS-FIG-S5-MN-RECOVERY-MODEL-REPLAY.csv` and checked by the research validator. This strongly supports that the published blue activation curve is the pre-optimizer default, not the final optimized mouse activation model. The raster line-center uncertainty is estimated at ±5 px, and no separate final-figure generator is deposited, so retain this as a strongly supported source-provenance finding rather than an absolute claim about undocumented plotting steps. Do not treat the Figure S5 mouse model curve as a final optimized fit.

The deposited current-fit procedure has now also been reproduced for panel J. `K_IV` takes the post-peak current and fits `a1*exp(-t/tau1) + a2*exp(-t/450 ms) + offset`, with `tau1` constrained to 0–300 ms and all three linear coefficients nonnegative. A Rust test uses the same full current trace and fixed-`tau2` fit; a one-dimensional search over `tau1` with a nonnegative linear least-squares solve for amplitudes/offset matches independent SciPy references at 0, 10, 20, 30, 40, and 50 mV within 0.1 ms. The model `tau1` values are approximately 52.28, 41.56, 33.46, 27.26, 22.47, and 18.75 ms. RMSE against the digitized human panel-J group means is ≈5.91 ms; this is a source-model/data comparison, not biological validation.

Panel K's model `tau2` is fixed at 450 ms by the source fit routine, rather than estimated from the current trace. Against the digitized experimental means, this fixed value has RMSE ≈149 ms for human and ≈166 ms for mouse. The wide voltage dependence in the plotted means and these discrepancies are consistent with the paper's explicit caveat that its HH models did not accurately reproduce K+ inactivation.

The source recovery protocol in `K_recovery` is also now reproduced in Rust: 2 ms at −120 mV, 5,000 ms conditioning at +40 mV, recovery at each of five voltages (−90, −85, −80, −75, −70 mV) for the ten source delays (4–8,464 ms), then a 5-ms +40-mV test pulse sampled at 0.5-ms steps. All 50 test-pulse peak currents are generated and fitted to the source's two-component recovery equation, with `tau1` constrained to 0–1,000 ms, `tau2` to 1,000–5,000 ms, nonpositive component amplitudes, and the source offset bound. The Rust fit uses a deterministic two-dimensional grid plus coordinate refinement and nonnegative/negative-constrained linear least squares for the amplitudes; it matches independent human SciPy `curve_fit` references within 3 ms for `tau1` and 15 ms for `tau2`. A separate SciPy replay of the deposited mouse parameters (pre-fit default `Ra=0.0167/ms`) gives nearly overlapping recovery curves; both species' five-voltage references are preserved in `research/HUMAN-L23-WILBERS-FIG-S5-MN-RECOVERY-MODEL-REPLAY.csv` and checked by CI. This is a current-based recovery fit, not direct reading of the two gate time constants.

At −80 mV, the independent reference fit is approximately `tau1=235.15 ms` and `tau2=2803.29 ms`. The exact source-script experimental means at the same voltage are 228.5275 ms human and 245.1212 ms mouse for fast recovery, and 1999.7295 ms human and 3579.8564 ms mouse for slow recovery. The pooled means are 236.8243 ms and 2789.7929 ms, respectively. Thus the model's current-fit components are close to the pooled species means (≈1.67 ms and ≈13.5 ms differences), not to a human-only slow-recovery target. Across recovery voltage, the SciPy reference pairs (`tau1/tau2`, ms) are approximately −90 mV: 115.73/2791.30; −85 mV: 155.67/2794.58; −80 mV: 235.15/2803.29; −75 mV: 376.91/2816.55; −70 mV: 332.22/2814.89. Only one experimental marker per species is supplied at −80 mV, so the remaining model voltage dependence is not experimentally validated. A second high-resolution raster inspection shows the panel-M model curves rising from roughly 120–160 ms at −90 to a peak near 370 ms at −75 and falling near 330 ms at −70, while panel N is nearly horizontal around 2.8 s. This is qualitatively consistent with the source-equation current-fit references above; no quantitative panel-M/N pixel RMSE is claimed, and exact model-line digitization remains open.

**Human-only parameterization warning:** the deposited model's slow recovery parameter `h2tau_inact_rec=2789.7929428108187 ms` is exactly the arithmetic mean of the human and mouse group means, not a human-specific measurement. The human-only mean is 1999.7295 ms; the pooled source parameter is about 39.5% higher. The fast-recovery pooled mean is 236.8243 ms versus 228.5275 ms human-only (about 3.6% higher). The model current-fit at −80 mV is close to the pooled means, as intended by the source fitting workflow. For HumanJS, retain these values only when reproducing the deposited source model; do not silently treat pooled human/mouse constants as human biological parameters. A human-only reparameterization needs the exact per-cell human data or an explicitly uncertainty-qualified group-mean decision. The missing K tau CSVs and raw traces prevent that decision here.

A stdlib-only validator, `experiments/validate_wilbers_fig_s5_digitization.py`, checks the seven research CSVs' PDF hash, species/marker identity, point counts, voltage grids, axis calibration, declared uncertainties, exact K_IV recovery constants, the mouse pre-fit model-line comparison, the five-voltage K_recovery model references, and quantitative model-versus-group-mean discrepancies in panels J/K. The CI workflow executes this validator. It verifies transcription/protocol reproducibility and arithmetic, not biological correctness.

**Published human/mouse K+ summary results (main Fig. 4 and Table S1):**
- Activation midpoint: human −3.0 ± 5.9 mV (`n=13`), mouse −7.9 ± 6.0 mV (`n=29`), unpaired t test `P=0.02`.
- Steady-state inactivation midpoint: human −52.7 ± 6.0 mV (`n=11`), mouse −65.0 ± 5.3 mV (`n=26`), unpaired t test `P<10^-6`.
- K+ availability at resting potential: human 0.94 ± 0.05, mouse 0.86 ± 0.06.
- Human K+ currents activate faster than mouse currents at lower membrane potentials. Fast- and slow-inactivation components were described as similar between species. Recovery time constants were described as similar, while human currents recovered to a larger proportion of their initial amplitude.
- The authors explicitly state that their HH conductance models did not accurately reproduce all K+ properties, particularly K+ inactivation, likely contributing to relatively poor fits to K+ currents and AP falling speeds.

**Quantitative panel J/K model-to-marker comparison (2026-11-11):** The six human source-protocol fast-inactivation current-fit outputs (52.2804, 41.5635, 33.4636, 27.2646, 22.4693, 18.7451 ms at 0–50 mV) have RMSE 5.9142 ms against the six digitized human panel-J group means; three of six residuals are within the ±2-ms plot-reading estimate. The model values are the independent SciPy references already checked by the Rust post-peak current-fit regression, not a fit to these digitized markers. For panel K, the source's fixed 450-ms slow component has RMSE 148.9672 ms against human and 166.3848 ms against mouse digitized means; only 2/10 human and 3/10 mouse residuals are within the ±25-ms plot-reading estimate. These discrepancies quantitatively support the authors' warning that K+ inactivation was poorly reproduced. The new validator recomputes and asserts these values in CI. Plot-reading estimates are not biological SD/SEM, and these are comparisons to group means, not inferential statistics or raw-trace validation.

**Remaining evidence boundary:** the exact Dataverse `Experimental means/k_tau_*.csv` files and raw per-cell K+ voltage-clamp traces remain absent. The J/K comparisons above are model-output-versus-experimental-marker residuals; they are not pixel-level digitizations of the red/blue model curves. Independently digitize model-line pixels in J/K/M/N, trace the exact figure-generation path and pre-/post-fit parameter snapshots, and reproduce panels M/N against their plotted curves. Do not fit/promote the exploratory Rust model on approximate group means alone; no raw-trace reproduction or biological validation is claimed.
#### Current-clamp conductance-density fitting audit

The full optimizer source, outcome-extraction definitions, AP1 feature targets, and deposited 20×20 fitted-density matrices have now been retrieved and checksum-verified. The exact all-human-kinetics grid corner maps to the HumanJS 114.48/29.05 pS/μm² preset after rounding. The complete audit, including the feature windows, optimizer objective, protocol, source hashes, exact target values, and limitations, is in Section 3 below. The optimizer targets cross-species median AP features even at the all-human kinetic setting; this is not a human-only fit or a direct channel-density measurement.

#### NEURON 9.0.2 unit-checker diagnostic

The original pure `k_human.mod` and `na_human.mod` were checked with NEURON 9.0.2's own `modlunit`, separately from compilation. Both mechanisms compile unchanged with `nrnivmodl`; compilation emits a warning that assignment to the GLOBAL variable `tadj` is not thread-safe. Compilation does **not** establish dimensional consistency.

On the unmodified files, `modlunit` stops before the rate equations: K+ fails at line 82 and Na+ at line 80 on `trates(v+vshift)`. The procedure signature `PROCEDURE trates(v)` has no voltage unit annotation, so the checker treats the passed millivolt expression as nonconformable with the untyped argument. The source also leaves `rates(vm)` and `trap0(v,th,a,q)` arguments/return units unannotated. A fresh follow-up run on 2026-11-11 independently repeated the K+ failure on both deposited species files: `k_human.mod` and `k_mouse.mod` each stop at line 82 with the same nonconformable-unit diagnostic. Both files had already compiled unchanged with `nrnivmodl`; this additional check confirms the initial untyped-signature failure is shared by the human and mouse K implementations, rather than specific to the human parameter set.

Temporary diagnostic copies were then used to expose the masked errors; no Dataverse source file was modified:

1. With explicit `trates(v (mV))`, `rates(vm (mV))`, and `trap0(v (mV), th (mV), a (/ms), q (mV)) (1/ms)` signatures, `modlunit` flags the active `trap0 = a * (v - th) / (1 - exp(-(v - th)/q))` expression (K line 141; Na line 138). The `/ms` prefactor multiplied by the voltage numerator produces `mV/ms`, not the declared `ms^-1` return. This independently confirms that the equation requires the prefactors `mV^-1 ms^-1`.
2. With the equation-required prefactor units `(/mV-ms)`, the checker proceeds only after adding the omitted units to `th_act_inf` and `q_act_inf` (both mV) and making the Q10 denominator a temperature interval, `10 (degC)`. The original `(celsius - temp)/10` exponent is otherwise dimensionful.
3. The checker then flags the active singularity fallback `trap0 = q*(1--(v-th)/q/2)` (K line 144; Na line 141): it has voltage units, not rate units, and omits the prefactor. Replacing this temporary probe's fallback with the source's commented-out `trap0 = a*q` makes `modlunit` pass for both K+ and Na+ diagnostic copies.

The branch predicate is a separate mathematical defect that dimensional checking cannot detect: it tests `fabs((v + th)/q)`, while the active denominator is singular at `v - th = 0`. Thus the fallback is selected around `v = -th`, not around the actual singularity `v = th`. HumanJS's `trap0` intentionally uses the equation's true singularity, the analytic `a*q` limit, and a stable local series; it does not reproduce this defective NMODL branch.

The diagnostic therefore establishes several independent source issues: untyped procedure/function signatures prevent the original unit check from reaching the equations; rate-prefactor declarations omit inverse millivolts; the fallback has the wrong dimensions and omits its prefactor; the fallback predicate uses the wrong sign; the Q10 exponent omits the temperature unit; and activation midpoint/slope parameters lack explicit voltage units. It also records the NEURON thread-safety warning for GLOBAL `tadj`. These findings strengthen the decision to keep HumanJS's typed Rust implementation independent of the deposited NMODL runtime. They do not establish that the deposited authors intended the equation-derived unit reinterpretation; that interpretation is required by the displayed equation and is explicitly a HumanJS engineering/scientific correction.

The unit-checking contract and command are documented by the [NEURON 9.0.2 NMODL reference](https://www.neuronsimulator.org/en/9.0.2/nmodl/language/nmodl.html) and [NEURON units guide](https://nrn.readthedocs.io/en/8.2.2/guide/units.html). `modlunit` is a separate check from `nrnivmodl` compilation.

**Evidence classification:** direct human somatic nucleated-patch recordings in the paper; model-side protocol and parameter fitting in the deposited Python/NMODL source; fixed/pooled fit settings as identified above; no independent reproduction of the missing raw voltage-clamp traces. The patch excludes the AIS, and these findings do not establish AIS channel kinetics or an anatomical soma/AIS model.

The intermediate 2026-11-11 source-grid and missing-extractor notes above were based on incomplete file extraction and are superseded by the complete checksum-verified 2026-11-12 audit in Section 3. The CSVs are present and their exact values are preserved in the repository; the helper exists in the retrieved source. No independent NEURON/SciPy rerun or biological validation is claimed.



## 3. Complete current-clamp conductance-fit provenance (2026-11-12 correction)

**Canonical dataset:** Wilbers et al. (2023), DataverseNL DOI [10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD), version 3.0. The current-clamp source files and three calibration CSVs are unrestricted (Dataverse metadata `restricted=false`). They were retrieved from the documented Dataverse access API through its signed SURF object-store redirect. Downloaded byte counts and SHA-1 digests match the independent Dataverse file metadata:

| File | Dataverse ID | Bytes | SHA-1 (Dataverse) | SHA-256 (retrieved bytes) |
|---|---:|---:|---|---|
| `AP1comparison.csv` | 318555 | 846 | `85fea00fea374ed0595d032180a798371d96aa4d` | `2833ee551241917767e912db569833629009bf5cda157824747847be89432d97` |
| `gbar_na.csv` | 318551 | 8,224 | `ac2f1b3ae108e8f256e53b0d85c4e0b353eb173a` | `b488e45ad87b03cc876f287e7a598d218899f63a85d9de6d8a108b01b05b9991` |
| `gbar_k.csv` | 318552 | 8,037 | `6867798db8a5a2a77a66bb72b7cae77590ff0247` | `6682854d3c2e72a5a29c5115a193d5db00adf1eda177bae24204c04e3d3531d0` |
| `cc_tools.py` | 318557 | 10,448 | `f64162577fa5dd86892b46570d597e58e083a02b` | `3215473c16162dc81f73cb60da161014f370f3acc052b7cae3c1c416d321f241` |
| `currentclamp.py` | 318553 | 3,070 | `fffbe589889ae552c29b96dd2eb1dafd90e1c69e` | `56a83d012040bb8dd8114edbe658ea347c7cb3a7451f7b711c9be7b496b73321` |
| `fit_gbar_na_k.py` | 318556 | 1,472 | `708babaafe09090828978b366e4c6193fe982421` | `a9549e210294a5016bb3d3e0ba51f4ba158e7f853f22150b75c728fc533b68d3` |

The three CSV files are preserved verbatim in HumanJS under `research/WILBERS-CURRENT-CLAMP-*.csv` (CC0 source data). The stdlib-only validator `experiments/validate_wilbers_current_clamp_grid.py` checks their byte counts, SHA-1 values, target medians, grid shape/orientation, optimizer bounds, and both endpoint values; CI runs it on every main push.

### The outcome extractor is present in the complete helper

The full 10,448-byte `cc_tools.py` was retrieved and checksum-verified. Contrary to the earlier incomplete extraction, the file **does define** both `get_outcomes(t, v)` and `get_outcomes_full(t, v)` at its end (the latter begins at source line 283). The prior “missing helper” conclusion was an extraction/search error and is superseded.

The exact `get_outcomes_full` definitions used by `fit_densities` are now known:

1. Detect AP peaks with `scipy.signal.find_peaks(v, prominence=50)`; the returned peak voltages are called `amp`. This is absolute peak voltage, not peak-to-threshold amplitude.
2. For each peak, take samples in the open interval from 1 ms before to 3 ms after that peak and calculate discrete `dvdt = diff(v)/diff(t)`.
3. Define threshold as the voltage sample immediately after the last pre-maximum-slope derivative sample below 40 mV/ms. The source comment notes this criterion was changed from 23.
4. Define AP amplitude for fractional windows as peak voltage minus this threshold. Upstroke is the mean `dvdt` between the 30% and 70% levels on the rising phase. Downstroke is the mean `dvdt` between the 70% and 30% levels on the falling phase.
5. Also calculate AHP as the minimum voltage between this peak and the next detected peak, or within 25 ms after the final peak. AHP and threshold are returned but are not optimizer targets in `fit_densities`.

The separate `get_outcomes` helper detects peaks with the same 50-mV prominence and returns the maximum and minimum derivative within the same −1/+3-ms windows. It is used by accommodation analysis, not by the three-feature density objective.

### Exact optimizer target and current-clamp protocol

`fit_densities` reads `AP1comparison.csv` and selects median rows in this order: `[5, 0, 1]`, corresponding to peak voltage (`amplitude`), upstroke, and downstroke. It forms each target as the arithmetic mean of the human and mouse medians:

| Feature | Human median | Mouse median | Optimizer target |
|---|---:|---:|---:|
| AP peak voltage (mV) | 46.1861495972 | 50.5402011871 | 48.3631753922 |
| Upstroke (mV/ms) | 378.1895103072 | 461.7445706513 | 419.9670404793 |
| Downstroke (mV/ms) | −76.0721557507 | −70.1367784282 | −73.1044670895 |

The objective is the equally weighted sum of the three squared relative residuals, `((model - target) / target)^2`. It is optimized with SciPy `minimize(method="Powell")`, initial conductances [95, 65], and independent bounds [20, 150] pS/μm². If the simulation does not contain exactly one detected AP, the objective is multiplied by four. Any exception in feature extraction is caught and converted to NaN. The code runs the objective again at the selected optimizer result and prints the extracted features.

The current-clamp cell uses one 10 μm-long, 10 μm-diameter section at 34°C; axial resistance 200 Ω·cm; specific capacitance 1 μF/cm²; passive membrane resistance 10,000 Ω·cm²; (E_K=-86) mV, (E_{Na}=+68) mV, and (E_{leak}=-70) mV. The human and mouse Na/K mechanisms are inserted together. All four mechanism voltage shifts are −10 mV. The one-AP runner finds rheobase using a 3-ms pulse, an APCount threshold of −20 mV, and coarse-to-fine current increments 0.1, 0.01, and 0.001 nA; it then applies 1.5× rheobase for 3 ms after a 1-ms delay, records for 29 ms, and uses (dt=0.02) ms.

### Exact source mapping of the HumanJS conductance preset

`fit_gbar_na_k.py` evaluates 20 Na kinetic ratios and 20 K kinetic ratios, each from 0 to 1 inclusive, for 400 calls to `fit_densities`. The outer loop is Na ratio and the inner loop is K ratio. The exported matrices reverse the Na rows for plotting: CSV row labels descend from 1 to 0, while K columns ascend from 0 to 1. The downstream interpolation explicitly reverses the rows again and treats K ratio as x and Na ratio as y.

The all-human kinetic condition is therefore the top-right cell (Na ratio=1, K ratio=1). Its exact deposited fitted conductance values are:

- Na: **114.47654963753565 pS/μm²**
- K: **29.045736151752504 pS/μm²**

Rounded to two decimals, these are **114.48 and 29.05 pS/μm²**, exactly the values in `HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit()`. This resolves the previously open provenance question: the HumanJS preset maps to the all-human-kinetics corner of the published 20×20 fitted-density grid, rather than an unidentified table entry.

The all-mouse (0,0) bottom-left corner is 148.61916853685673 pS/μm² Na and 64.99989629764137 pS/μm² K. The source `currentclamp.py` independently calls `fit_densities` at all-human ratios (1,1), all-mouse ratios (0,0), and mixed ratios (0.5,0.5), confirming the grid endpoints' intended interpretation.

**Important interpretation:** “all-human” describes the channel kinetic ratios used in the model, not the experimental target population. The optimizer still fits the all-human kinetic model against the 50:50 human/mouse median AP feature targets shown above. The preset is not a human-only AP fit and its conductances are not direct measurements of human channel density. It remains a fitted single-compartment model parameterization, not biological validation.

### Verification of human/mouse kinetic mixing semantics

The pure human and mouse NMODL mechanisms confirm that the ratio axes genuinely partition a shared fitted conductance density between complementary kinetic mechanisms; they are not merely labels on independently active channels:

- Human Na (na_human.mod, file 318563) uses tadj * gbar * na_human_ratio * m^3 * h; mouse Na (na_mouse.mod, file 318561) uses tadj * gbar_na_human * (1 - na_human_ratio_na_human) * m^3 * h.
- Human K (k_human.mod, file 318566) multiplies its three-component gating expression by gbar * k_human_ratio; mouse K (k_mouse.mod, file 318560) multiplies its corresponding mouse gating expression by gbar_k_human * (1 - k_human_ratio_k_human).

The unrestricted mouse mechanism files have Dataverse SHA-1 values: na_mouse.mod (3,726 bytes, file 318561) 84cc161f3c38fc71d399cc998d91f0c60cbd2df1; k_mouse.mod (4,303 bytes, file 318560) 8b1761352a44cc57c29f3345242a4060186d84eb. Therefore ratio 1 means the shared conductance is assigned entirely to the human kinetic mechanism, ratio 0 entirely to the mouse mechanism, and 0.5 splits it equally. This independently confirms the interpretation of the 20×20 grid's all-human and all-mouse endpoints. The Na mechanism's tadj also multiplies maximal conductance as well as gating rates; the K mechanism uses tadj for gate time constants but not for its conductance expression. The Rust implementation follows this species-specific source placement: sodium conductance includes the sodium temperature factor, while potassium conductance does not.

### Reproduction boundary

This session verified all six downloaded files against the Dataverse SHA-1 metadata and parsed the complete source helper and calibration tables. The original NEURON/SciPy optimization was **not rerun**: the available execution environment does not have NEURON, SciPy, or NumPy installed. The source grid is a deposited result, not a fresh independent optimization. The HumanJS 114.48/29.05 mapping is nevertheless directly verified by the exact grid corner and its matching source checksums. Do not claim an independently rerun optimizer, raw-trace reproduction, or biological validation.
