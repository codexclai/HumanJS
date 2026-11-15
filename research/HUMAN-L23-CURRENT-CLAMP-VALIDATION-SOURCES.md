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

## Validation utility and limitations

| Candidate use | Howard | Planert |
|---|---|---|
| Raw human current-clamp AP morphology / excitability | Potentially, subject to protocol match, stratification and ABF license review | Not possible from the processed deposit |
| Human L2–3 pyramidal-cell population heterogeneity | Only after layer/cell-type filtering; mixed cortical layers | Strongly relevant: 901 selected L2–3 pyramidal cells |
| Isolated intrinsic Kv activation/inactivation/recovery | Not described in the reviewed intrinsic protocol | Not described |
| Direct AIS channel density or compartment-specific kinetics | No | No |

These sources can inform a future external benchmark of current-clamp AP/excitability outputs. They do not close ADR-014's somatic voltage-clamp evidence gate and cannot identify or tune K-channel gates. The Planert and Mittermaier studies share investigators and institutional context; overlap between their anonymized patient cohorts is unknown, so do not count them as independent subject replication. No Rust equation, gate, conductance density or model parameter is changed by this evidence review.
