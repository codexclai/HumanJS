# Human L2–3 current-clamp evidence for future spike-model validation

**Reviewed:** 2026-11-15  
**Status:** human current-clamp comparator sources located; one provides raw ABF/NWB data, the other processed per-cell feature tables. Neither is a source of isolated intrinsic Kv channel kinetics.

## Why these sources matter

Mittermaier et al. (2024) adds preprocessed axonal Kv1 voltage-clamp summaries, but not the somatic current-clamp action-potential waveforms needed to validate the exploratory single-compartment spike model. Two further datasets are relevant for later current-clamp comparisons:

1. Howard et al. (2022): whole-cell human cortical recordings with public ABF and NWB files.
2. Planert et al. (2025 online; 2026 issue): a large L2–3 pyramidal-cell study with public processed, per-cell intrinsic electrophysiology features and e-type labels.

Neither article describes intrinsic voltage-step protocols for Kv activation, inactivation, recovery, or toxin-isolated K-current kinetics. Neither should be used to back-solve individual K-channel gates from aggregate action-potential features.

## Howard et al. (2022): raw current-clamp recordings

**Article:** D. Howard et al., “An in vitro whole-cell electrophysiology dataset of human cortical neurons,” *GigaScience* 11 (2022), giac108, DOI [10.1093/gigascience/giac108](https://doi.org/10.1093/gigascience/giac108).  
**Data:** GigaDB DOI [10.5524/102317](https://doi.org/10.5524/102317); human DANDI accession [000293, version 0.220708.1652](https://dandiarchive.org/dandiset/000293/0.220708.1652). The associated mouse data are DANDI 000292 and must remain separate.

The dataset describes 118 human neurons from 35 participants. It includes L2/3, deep L3c and L5 neurons; it is not a layer-pure L2–3 pyramidal-cell cohort. GigaDB contains original ABF recordings, including recordings that failed quality-control or conversion to NWB, alongside the DANDI NWB-converted data. The GigaDB page did not clearly expose a redistribution license in the reviewed metadata; do not copy or redistribute ABF files into HumanJS until their terms are resolved.

The reviewed intrinsic-excitability protocols use current-clamp hyperpolarizing/depolarizing current injections (the article describes long-square steps, including 600–1000 ms protocols). A representative human NWB asset inspected directly contained 16 acquisition series typed as `CurrentClampSeries`, with 20 kHz sampling and a paired stimulus description of `I_clampsec`. In this file, the stimulus container used NWB type `VoltageClampStimulusSeries`; that container type alone must not be mistaken for an intrinsic voltage-clamp measurement because the stimulus description and acquisition series identify injected current. This was one representative asset, not an exhaustive review of every recording.

The reviewed paper describes current-clamp excitability and synaptic recordings, not intrinsic voltage-step isolation of Kv activation/inactivation/recovery or blocker-sensitive K-current kinetics. This dataset could support future raw action-potential waveform, rheobase and repetitive-firing comparisons after a protocol-matched audit and layer/cell-type stratification. It is not a K-gate parameter source.

## Planert et al. (2025/2026): processed human L2–3 pyramidal-cell features

**Article:** H. Planert et al., “Electrophysiological classification of human layer 2–3 pyramidal neurons reveals subtype-specific synaptic interactions,” *Nature Neuroscience* 29(2), 455–466, published online 2025-12-10, DOI [10.1038/s41593-025-02134-7](https://doi.org/10.1038/s41593-025-02134-7). Full article: [PMC12880919](https://pmc.ncbi.nlm.nih.gov/articles/PMC12880919/).  
**Processed code/data:** Figshare DOI [10.6084/m9.figshare.28184126](https://doi.org/10.6084/m9.figshare.28184126), public `humandata.zip` (1,956,326 bytes), declared GPL 3.0+. The archive was inspected but not copied into HumanJS; its SHA-256 at review was `6b0d7244dec5c665a88d0d1828ae842d084bb737a6df9f86561d53d8564c4bfd`.

The study uses human middle temporal gyrus from anterior temporal resections for pharmaco-resistant epilepsy, acute 300–400 μm slices, supragranular L2–3 down to about 1,200 μm from the pia, and 34 °C recording conditions. The patient age range is 21–55 years (median 34), with a cohort of 23 individuals. The paper reports 1,479 pyramidal neurons recorded and 1,214 passing quality control. The public processed cell table contains 1,560 total rows, including non-pyramidal cells and excluded/incomplete entries. The figure-analysis script selects `saved == 0` and `etype != "IntN"`; this reproduces **901 pyramidal neurons across 22 anonymized patient IDs** for the core intrinsic-feature comparison.

The processed `tcell_all_psdn.csv` includes per-cell resting potential (`V_m`), input resistance (`R_in`), membrane time constant (`tau`), AP threshold amplitude (`AP_tamp`), AP amplitude (`AP_amp`), half-width (`AP_hw`), upstroke/downstroke (`AP_up`, `AP_down`), AHP (`AP_ahp`), ADP slope (`AP_adp`), ISI adaptation (`isi_adapt`), frequency at 700 pA (`freq_700`), sag ratio (`sag`), rheobase (`rheo`), and F–I slope (`f_i_slope`). These are processed feature summaries, not raw voltage/current time series.

The authors' MATLAB definitions and article methods provide the following feature semantics:

- Resting potential: average of four 150 ms trace segments preceding the −50, +50, +100, and +150 pA current injections.
- Input resistance: steady-state voltage response relative to resting potential for −100, −50, +50, and +100 pA current steps; the four step-derived estimates are averaged (MΩ).
- Membrane time constant: mono-exponential fit to initial segments after −50 and −100 pA current steps; the two estimates are averaged (ms).
- Rheobase: first positive current injection that elicits at least one AP (pA).
- F–I slope: linear fit of firing frequency versus positive current amplitude, requiring at least three APs for each included stimulus and using stimuli up to 900 pA (Hz/pA).
- AP waveform: spline smoothing and reverse filtering using access resistance and an estimated 4.5 pF pipette capacitance; threshold is the first slope above 60 mV/ms; AP amplitude is threshold-to-peak; half-width is measured at half amplitude; up/downstroke are maximal/minimal derivatives; AHP is the post-spike minimum relative to threshold.
- ISI adaptation: mean of the second-to-first interspike-interval ratio across the first five positive-current steps (or fewer available) that elicit at least three APs.
- Sag ratio: fitted minimum and steady-state voltages relative to resting potential from the −100 pA hyperpolarizing current response.

For the exact `saved == 0` and `etype != "IntN"` subset of the public processed table, the calculated all-cell medians are:

| Feature | Median | Unit / definition |
|---|---:|---|
| Resting potential | −73.33 | mV |
| Input resistance | 71.92 | MΩ |
| Membrane time constant | 19.30 | ms |
| AP threshold amplitude | −37.19 | mV |
| AP amplitude | 84.38 | mV, threshold-to-peak |
| AP half-width | 0.870 | ms |
| AP upstroke | 354.82 | mV/ms |
| AP downstroke | 82.70 | mV/ms, magnitude |
| AHP | 14.28 | mV below threshold |
| ADP slope | 0.284 | mV/ms |
| ISI adaptation | 2.092 | mean ratio |
| Firing frequency at 700 pA | 22 | Hz |
| Sag ratio | 1.083 | ratio |
| Rheobase | 250 | pA |
| F–I slope | 0.0404 | Hz/pA |

The 901-cell core subset has four deposited labels: SlowAP (445), LowRin (293), FastAP (136), and DoubSpk (27). These are descriptive subtype counts in a processed table, not a new independent electrophysiological sample.

### Subtype-generation provenance

The public `humandata.zip` includes the 2025 figure-analysis R Markdown that plots and statistically compares the pre-existing `etype` labels; it does not itself regenerate those labels. The archive also contains an earlier full clustering R Markdown workflow. That earlier workflow standardizes 15 intrinsic features, first separates interneuron-like from pyramidal-like cells by Euclidean Ward.D2 hierarchical clustering, then applies Kimes `sigclust2` significance testing to the pyramidal-cell hierarchy (`n_min=300`, `alpha=0.05`, `n_sim=100`) and maps the resulting significant branches to the SlowAP/FastAP/DoubSpk/LowRin labels. `NbClust` and silhouette checks explore cluster counts; the archived 3- and 5-type R Markdown files are sensitivity analyses. This supplies a published method/label mapping, but the exact final 2025 label-generation state should not be treated as a fully bit-for-bit reproducible pipeline without reconciling historical pipeline versions, final data curation and preassigned labels in the 2025 table.

The paper states that original human-participant data are not openly shared due to EU/German data-protection requirements. The Figshare archive contains processed tables and analysis/visualization code, not raw human electrophysiology traces. No raw sweep refit or independent trace-level uncertainty analysis can be performed from this deposit. The Figshare archive declares GPL 3.0+; no source archive/code or per-cell data table is copied into HumanJS.

## Kushner et al. (2025): pediatric L2/3 current-clamp and broad 4-AP perturbation

**Article:** J. K. Kushner et al., “Characterizing the Diversity of Layer 2/3 Human Neocortical Neurons in Pediatric Epilepsy,” *eNeuro* 12(5), ENEURO.0247-24.2025, published 2025-04-17, DOI [10.1523/ENEURO.0247-24.2025](https://doi.org/10.1523/ENEURO.0247-24.2025); full text [PMC12061357](https://pmc.ncbi.nlm.nih.gov/articles/PMC12061357/). The article is CC BY 4.0.

The study analysed 108 human L2/3 pyramidal neurons from 33 pediatric patients (age 1–21 years; mean 9.9 years): 37 from malformations of cortical development (MCD), 45 from other epilepsy etiologies, and 26 tumour-associated controls. Samples came from temporal (15 patients), frontal (13), parietal (4) and occipital (1) neocortex. Acute 400 μm coronal slices were prepared in cold NMDG ACSF, incubated at about 35 °C for 12 min, then held in HEPES ACSF at about 23 °C; recordings were in a heated chamber at about 33 °C. The recording mode was whole-cell **current clamp** from rest, with (I_{hold}=0) pA. No intrinsic voltage-clamp protocol for isolating K or Na channel currents is reported.

The intrinsic protocol used a 0.5 s baseline, a 2 s current ramp from 0 to 1000 pA, and a 2.5 s recovery period, plus 600 ms square-current injections from −100 to +100 pA in 10 pA increments and −250 to +1000 pA in 50 pA increments. The internal solution was potassium based (135 mM potassium gluconate, 20 mM KCl, 10 mM HEPES, 0.1 mM EGTA, 2 mM Mg-ATP and 0.3 mM Na₂-GTP; pH 7.3–7.4). These long-square/ramp current-clamp measurements are useful context for firing and AP phenotypes, but not voltage-clamp channel kinetics.

### 100 μM 4-aminopyridine wash-on

A subset of 17 neurons from 8 patients underwent 100 μM 4-AP wash-on. Published Table 5 reports the following paired group summaries:

| Measure | Before 4-AP | 100 μM 4-AP | Statistical comparison |
|---|---:|---:|---|
| Input resistance | 146.00 ± 67.25 MΩ | 111.40 ± 53.23 MΩ | paired t, p = 0.0002 |
| Voltage sag | 6.43 ± 3.58% | 6.68 ± 3.48% | Wilcoxon, p = 0.3060 |
| Membrane decay | 28.15 ± 7.90 ms | 33.38 ± 17.54 ms | Wilcoxon, p = 0.3303 |
| AP threshold | −38.14 ± 4.28 mV | −40.59 ± 4.93 mV | paired t, p = 0.0433 |
| AP amplitude | 86.80 ± 7.62 mV | 87.40 ± 4.62 mV | paired t, p = 0.7729 |
| AP half-width | 1.28 ± 0.32 ms | 1.61 ± 0.39 ms | paired comparison, p = 0.0091 |
| AHP magnitude | −16.85 ± 2.76 mV | −14.13 ± 3.26 mV | Wilcoxon, p = 0.0021 |
| AHP latency | 8.59 ± 3.79 ms | 15.53 ± 5.19 ms | paired t, p = 0.0002 |
| Maximum firing rate | 26.08 ± 8.70 Hz | 25.29 ± 7.17 Hz | paired t, p = 0.3543 |

The table also reports higher accommodation ratios after 4-AP at the 400, 500, 600, 750, 800 and 850 pA steps (p = 0.0273, 0.0342, 0.0143, 0.0105, 0.0034 and 0.0068, respectively). There were no significant changes in voltage sag, membrane decay, AP amplitude, ΔAHP or maximum firing rate. The authors suggest the AP/AHP changes are consistent with perisomatic/AIS Kv1 and Kv4 contributions, but this is an interpretation of a broad pharmacological intervention, not a subtype-selective channel assay.

**Model relevance and limits:** this is a useful pediatric human *functional perturbation* reference for the direction and scale of some current-clamp outcomes under broad K-channel block. It is not a direct Kv current measurement, does not isolate Kv1 versus Kv4, and cannot identify gate time constants, activation/inactivation curves, recovery kinetics or compartment-specific conductance density. The seizure-affected pediatric cohort is not interchangeable with adult human L2/3 tissue; these paired means must not be used to tune HumanJS channel gates.

The article page and its linked supplementary files expose figure images and summary tables, including Table 5, but the reviewed article and figures/data page did not provide a formal data-availability statement or a linked repository of the raw voltage traces. No claim is made that the original traces do not exist elsewhere; only that a public raw-trace deposit was not located during this review. The published article and Table 5 values can be cited as processed paired summaries, not independently re-fit waveforms.

## Validation utility and limitations

| Candidate use | Howard | Planert | Kushner |
|---|---|---|---|
| Raw human current-clamp AP morphology / excitability | Potentially, subject to protocol match, stratification and ABF license review | Not possible from the processed deposit | Summary/representative AP figures and current-clamp effects; no public raw trace repository located |
| Human L2–3 pyramidal-cell population heterogeneity | Only after layer/cell-type filtering; mixed cortical layers | Strongly relevant: 901 selected L2–3 pyramidal cells | 108 pediatric L2/3 PNs from 33 patients, three clinical groups |
| Broad pharmacological K-blocker current-clamp perturbation | Not established in the reviewed records | Not described | 100 μM 4-AP pre/post current-clamp comparison (17 neurons, 8 patients) |
| Isolated intrinsic Kv activation/inactivation/recovery | Not described in the reviewed intrinsic protocol | Not described | Not described; no voltage-clamp K-current isolation |
| Direct AIS channel density or compartment-specific kinetics | No | No | No |

These sources can inform a future external benchmark of current-clamp AP/excitability outputs. They do not close ADR-014's somatic voltage-clamp evidence gate and cannot identify or tune K-channel gates. The Planert and Mittermaier studies share investigators and institutional context; overlap between their anonymized patient cohorts is unknown, so do not count them as independent subject replication. No Rust equation, gate, conductance density or model parameter is changed by this evidence review.


## Follow-up human Kv voltage-clamp literature audit — direct A-type current evidence (2026-11-17)

The 2026-11-15 screen above correctly excluded the Chameh/Rich \(I_h\) experiments, Planert's synaptic voltage-clamp workflow, Howard's reviewed current-clamp records and Kushner et al. (2025) 4-AP current-clamp perturbation. However, its broader wording about an absence of direct human somatic Kv evidence was incomplete. A subsequent primary-literature search located direct human temporal-neocortical A-type current kinetics in Rüschenschmidt et al. (2004), and direct human hippocampal \(I_K\)/\(I_A\) measurements in Beck et al. (1997). A 2026 Kushner study adds human L2/3 KCNQ2–5 network pharmacology. These studies and their distinct scopes are documented in the dedicated companion note, research/HUMAN-K-CURRENT-VOLTAGE-CLAMP-EVIDENCE.md.

The direct Rüschenschmidt neocortical A-current study reports activation, steady-state inactivation and recovery summaries from five cells, but no public raw sweep/per-cell data deposit was identified. Beck et al. provide an open full-text human dentate-granule-cell voltage-clamp study (34 cells from 11 TLE patients), with \(I_A\) present in 6/15 investigated AHS neurons; it is hippocampal evidence, not cortical pyramidal-cell evidence. Kushner et al. (2026) find retigabine-mediated KCNQ2–5 activation suppresses human L2/3 network oscillations, but their experiments are current-clamp/network pharmacology, not isolated Kv7 voltage clamp.

Accordingly, the corrected conclusion is: **published direct human neocortical A-type current kinetics exist, but publicly accessible raw human cortical K-current traces and per-cell data suitable for independent trace refitting were not located in this targeted search.** These findings narrow the evidence gap but do not establish molecular subunit identity, L2/3 pyramidal-cell specificity, AIS/somatic channel density, or a validated HumanJS gate. Do not transfer the summary parameters into Rust. ADR-014 remains open; no Rust equation or model parameter was changed. The search was targeted rather than systematic, and no authors or researchers were contacted.

The expanded direct human K-current evidence review is maintained in research/HUMAN-K-CURRENT-VOLTAGE-CLAMP-EVIDENCE.md. Use that note as the canonical protocol, quantitative-summary and limitation record; this document remains focused on current-clamp comparators and the distinction between them and voltage-clamp evidence.
