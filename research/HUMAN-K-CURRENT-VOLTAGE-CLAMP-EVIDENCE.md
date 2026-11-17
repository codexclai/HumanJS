# Human neuronal potassium-current voltage-clamp evidence: neocortical A-type and hippocampal currents

**Reviewed:** 2026-11-18  
**Scope:** Published human neuronal voltage-clamp current summaries, the public per-recording Wilbers K-current fit workbook, and related human network-level KCNQ evidence.  
**Status:** Direct human neocortical A-type and somatic mixed K-current measurements are documented below. Wilbers et al. provide a public per-recording fit workbook, but the original raw K-current NWB sweeps and several separate fitting-target CSVs are absent from the inspected DataverseNL v3.0 inventory. No raw-trace refit was performed. This note does not authorize parameter transfer into HumanJS.

## Executive finding

The previous literature screen was incomplete in two different ways. Direct human neocortical A-type and hippocampal K-current studies had been missed; a subsequent file-level audit also establishes that the public Wilbers Dataverse release contains per-recording processed K-current fits, although the raw K-current sweeps are absent. The main direct voltage-clamp sources are:

1. Rüschenschmidt et al. (2004) characterize a fast transient A-type current in acutely dissociated human temporal neocortical neurons from epilepsy surgery tissue. The PubMed abstract reports activation, steady-state inactivation and recovery summaries from five cells.
2. Beck et al. (1997) characterize voltage- and calcium-dependent K currents in acutely isolated human hippocampal dentate granule cells. Their open full-text article reports a delayed outward current in all 34 recorded neurons and an A-type current in six neurons from three patients with Ammon's horn sclerosis.
3. Wilbers et al. (2023) measure pharmacologically isolated aggregate voltage-gated K currents in nucleated somatic patches from adult human L2/L3 pyramidal neurons. The unrestricted Dataverse data_fig4.xlsx workbook contains per-recording steady-state and voltage-dependent kinetic fit summaries for 13 human recordings, with activation fits in 13 and inactivation fits in 11.

These sources establish complementary human K-current evidence but are not interchangeable. Rüschenschmidt provides an A-type current summary from five cells without a resolved cortical layer or molecular channel identity. Beck provides pathology-dependent hippocampal dentate-granule-cell currents, not cortical pyramidal-cell evidence. Wilbers provides adult human L2/L3 somatic mixed-K-current voltage-clamp measurements plus processed per-recording fit arrays; however, the workbook is not a raw-sweep archive. No original human K-current NWB traces were found in the 65-file DataverseNL v3.0 inventory, and a raw-trace refit is therefore still unavailable. Neither a mixed K-current fit nor a pharmacological A-current phenotype identifies an individual Kv molecular subtype.

A further 2026 human L2/3 study shows that KCNQ2–5 activation can suppress 4-AP-induced network oscillations, but it uses current clamp and pharmacology, not isolated Kv7 voltage-clamp protocols.

**The evidence gap is therefore narrower than previously documented, but ADR-014 remains open.** Do not equate the published A-current summaries with a fully validated L2/3 pyramidal-cell gate, infer Kv4 molecular identity from the A-current phenotype, or tune HumanJS parameters from summary numbers alone.

## 1. Rüschenschmidt et al. (2004): direct human neocortical A-type current

**Citation:** C. Rüschenschmidt et al., “Characterization of a fast transient outward current in neocortical neurons from epilepsy patients,” *Journal of Neuroscience Research* 75 (2004), 807–816. DOI [10.1002/jnr.20055](https://doi.org/10.1002/jnr.20055); PMID [14994341](https://pubmed.ncbi.nlm.nih.gov/14994341/). The publisher abstract is available from [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/jnr.20055).

### Preparation and measurement

The abstract describes acutely dissociated human temporal-lobe neocortical neurons from patients undergoing epilepsy surgery, studied with whole-cell voltage clamp. The A-type current was isolated using a subtraction protocol; delayed potassium currents were reduced pharmacologically with 10 mM tetraethylammonium chloride (TEA).

The accessible abstract does not disclose the full voltage-step sequence, detailed internal/external solutions, exact total patient/cell count, or a layer- and cell-type-resolved sampling scheme. Those details are therefore not inferred here.

### Published kinetic summaries

| Quantity | Reported result | Reported sample |
|---|---:|---:|
| Activation threshold | Approximately −70 mV | Study-level description |
| Half-maximal activation, \(V_{1/2,\mathrm{act}}\) | −14.8 ± 1.8 mV | n = 5 |
| Activation Boltzmann slope factor | 17.0 ± 0.5 mV | n = 5 |
| Half-maximal steady-state inactivation, \(V_{1/2,\mathrm{inact}}\) | −98.9 ± 8.3 mV | n = 5 |
| Inactivation Boltzmann slope factor | −6.6 ± 1.9 mV | n = 5 |
| Recovery from inactivation | Monoexponential \(\tau=18.2 \pm 7.5\) ms | n = 5 |

At +30 mV, the abstract reports a 35% reduction in current amplitude with 5 mM 4-aminopyridine (4-AP), a 22% reduction with 100 μM flecainide, and a 31% reduction with 500 μM cadmium. Flecainide also markedly accelerated inactivation. Reported drug effects were reversible.

### Interpretation and limits

This is direct human **neocortical** voltage-clamp evidence for an A-type current phenotype with quantitative group kinetic summaries. It is materially more relevant to cortical K-current physiology than hippocampal dentate-granule-cell or animal-only studies.

However:

- The fitted voltage-dependence and recovery values are based on n=5; they are not a large population distribution.
- The accessible abstract describes temporal neocortical neurons but does not resolve cortical layer, excitatory/inhibitory identity, or a specific pyramidal-cell subtype.
- An A-type current phenotype and pharmacological sensitivity do not establish a specific molecular composition such as Kv4.2/Kv4.3, Kv1.4, or a particular auxiliary-subunit complex.
- The accessible PubMed and publisher records provide summary values, not raw sweeps or an identified public per-cell dataset. No open raw-trace deposit was located in this targeted search.

These published summary values are a candidate for careful protocol/provenance review, not a direct parameter-transfer instruction.

## 2. Rüschenschmidt et al. (2004): modulation of human neocortical A-type current by calcium-channel blockers

**Citation:** “Reduction of human neocortical and guinea pig CA1-neuron A-type currents by organic calcium channel blockers,” *Neuroscience Letters* 368 (2004), 57–62. DOI [10.1016/j.neulet.2004.06.058](https://doi.org/10.1016/j.neulet.2004.06.058); PMID [15342134](https://pubmed.ncbi.nlm.nih.gov/15342134/). [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/15342134/).

The study used whole-cell voltage clamp in acutely isolated human temporal neocortical neurons and, separately, guinea pig CA1 neurons. The following results are the **human** observations only:

- 40 μM nifedipine reduced A-current amplitude by 28% at a command potential of −6 mV. It accelerated inactivation and produced a biexponential fit with time constants 8.4 ± 1.1 ms (n=6) and 62.9 ± 6.4 ms (n=5); the reported control time constant was 50.1 ± 8.5 ms (n=6).
- 40 μM verapamil did not change amplitude but accelerated monoexponential inactivation from 40.2 ± 7.1 ms to 13.3 ± 0.8 ms (n=9).

The guinea pig CA1 result (42.3 ± 5.9 ms to 15.0 ± 1.3 ms, n=11) is animal evidence and is not included in the human values above.

This paper provides additional pharmacological evidence about the human neocortical A-current phenotype, but these calcium-channel blocker effects are not a molecular channel fingerprint and do not add an independent, complete activation/inactivation/recovery dataset. Cohort independence from the other Rüschenschmidt report was not established in this review.

## 3. Beck et al. (1997): voltage- and calcium-dependent K currents in human dentate granule cells

**Citation:** H. Beck et al., “Potassium currents in acutely isolated human hippocampal dentate granule cells,” *Journal of Physiology* 498 (1997), 73–85. DOI [10.1113/jphysiol.1997.sp021842](https://doi.org/10.1113/jphysiol.1997.sp021842); PMID [9023769](https://pubmed.ncbi.nlm.nih.gov/9023769/); PMCID [PMC1159235](https://pmc.ncbi.nlm.nih.gov/articles/PMC1159235/). The full article is openly available through [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC1159235/pdf/jphysiol00286-0069.pdf).

### Cohort, preparation and recording

The study examined 34 acutely isolated dentate granule cells from 11 patients undergoing hippocampal resection for pharmacoresistant temporal-lobe epilepsy. Neuropathology classified five patients as having Ammon's horn sclerosis (AHS); six had a temporal-lobe lesion without AHS. The authors state that four of the 11 patients had also appeared in their 1996 report, but the neurons were different. These related publications must not be counted as fully independent patient replication.

Human hippocampal slices (400 μm) were enzymatically treated with pronase, the dentate gyrus was dissected and triturated, and only granule-cell-like neurons were included. Whole-cell voltage-clamp recordings were obtained 5–90 minutes after isolation. The recording solution included 1 μM tetrodotoxin. Pipette resistance was 3–5 MΩ; access resistance averaged 7.2 ± 3.6 MΩ, with 40% series-resistance compensation. The authors estimated a maximum residual voltage error of 5.4 mV.

The principal voltage-dependent K-current experiments used 11.5 mM intracellular EGTA with 1 mM Ca²⁺ to strongly buffer intracellular calcium. A separate configuration used 1 mM BAPTA with 0.1 mM Ca²⁺ internally and 5 mM extracellular Ca²⁺ to examine calcium-dependent components.

### Delayed outward \(I_K\)

A slowly activating outward current with biexponential time-dependent decay was observed in all 34 neurons and had an activation threshold around −30 mV. The Figure 1 activation/inactivation protocol is explicitly described as recordings from patients with lesion-associated epilepsy.

| Quantity | Reported result |
|---|---:|
| Half-maximal activation, \(V_{1/2,\mathrm{act}}\) | −2.9 ± 1.8 mV |
| Activation slope factor | 12.0 ± 1.4 mV |
| Half-maximal inactivation, \(V_{1/2,\mathrm{inact}}\) | −48.7 ± 1.1 mV |
| Inactivation slope factor | −5.98 ± 1.2 mV |
| Removal of inactivation | Monoexponential \(\tau=116.7 \pm 27.7\) ms, n=5 |
| Current decay at +50 mV | Biexponential time constants 253 ± 118 ms and 1319 ± 399 ms |
| Current decay at +10 mV | Biexponential time constants 323 ± 151 ms and 2259 ± 1011 ms |

The authors also measured a tail-current reversal potential of −81.2 ± 8.0 mV, close to their estimated potassium equilibrium potential of −81 mV.

These \(I_K\) values describe the delayed outward component under a strongly calcium-buffered protocol; they are not the A-type-current kinetics below and should not be pooled with them.

### Transient A-type \(I_A\)

A classical A-type current was observed in six neurons from three AHS patients. It was not observed in patients with lesion-associated epilepsy in this study. The A-current was isolated kinetically by inserting a 50 ms delay at −50 mV between the conditioning prepulse and command pulse, allowing the rapidly inactivating component to disappear; subtracting the delayed trace from the corresponding undelayed trace yielded the transient current.

The isolated \(I_A\):

- activated rapidly and inactivated with a monoexponential time course;
- was virtually completely blocked by 5 mM 4-AP;
- was not affected by low extracellular calcium;
- was insensitive to 10 mM TEA in two of five neurons tested in the TEA comparison.

The subtraction-derived decay estimates were:

| Command potential | \(I_A\) decay time constant |
|---:|---:|
| +20 mV | 15.9 ± 6.3 ms |
| 0 mV | 20.3 ± 9.4 ms |
| −20 mV | 38.1 ± 20.1 ms |

These time-constant fits were reported for n=4. A separate figure-specific analysis of a TEA-resistant transient current in two neurons from one 9-year-old patient gave \(V_{1/2,\mathrm{act}}=-11.2\) mV (slope 4.2 mV), \(V_{1/2,\mathrm{inact}}=-58.0\) mV (slope 5.7 mV), and decay values of 19.8, 22.5 and 45.5 ms at +20, 0 and −20 mV, respectively. This is a very small subanalysis, not a robust population estimate.

### Calcium-dependent outward components

Using the separate BAPTA/low-internal-calcium configuration, the authors identified pharmacologically distinct calcium-dependent outward components. Low extracellular calcium reduced peak outward current by approximately 43%; 5 mM extracellular Ba²⁺ reduced it by approximately 78%; 100 μM Cd²⁺ reduced it by approximately 25%. A component sensitive to 500 μM TEA and 10 nM charybdotoxin was not additively blocked by the two agents, while 50 nM apamin reduced a smaller component. The authors interpreted these findings as evidence for BK- and SK-like components. These are pharmacological classifications, not molecularly definitive subunit identifications.

### Interpretation and limits

Beck et al. provide valuable direct human voltage-clamp evidence, but it is **hippocampal dentate granule-cell** evidence rather than neocortical pyramidal-cell evidence. The A-type current was heterogeneous and associated with AHS in this cohort; it was not found in the lesion-associated epilepsy subgroup. The authors deliberately used acute dissociation to mitigate space-clamp problems, but the sampled cells no longer retain intact dendritic/axonal compartments. Series-resistance voltage error was estimated up to 5.4 mV. The paper provides published group summaries and plotted traces, but no publicly downloadable raw sweep/per-cell trace archive was identified in this review.

**Related earlier study:** Beck et al. (1996), “Properties of a delayed rectifier potassium current in dentate granule cells isolated from the hippocampus of patients with chronic temporal lobe epilepsy,” *Epilepsia* 37, 892–901, DOI [10.1111/j.1528-1157.1996.tb00043.x](https://doi.org/10.1111/j.1528-1157.1996.tb00043.x), PMID [8814103](https://pubmed.ncbi.nlm.nih.gov/8814103/). It reports pathology-associated differences in \(I_K\) steady-state inactivation: −67.7 ± 0.6 mV in AHS versus −47.7 ± 2.6 mV in lesion-associated epilepsy (p=0.0017). Because the 1997 paper explicitly reports patient overlap with the earlier work, this is related evidence, not an independent replication cohort.

## 4. Kushner et al. (2026): KCNQ2–5 modulation of human L2/3 network activity

**Citation:** J. K. Kushner et al., “4-Aminopyridine induced hyperpolarizing oscillations in pediatric human epileptic tissue are network-driven potassium currents that are abolished by activation of KCNQ2–5 (Kv7.2–Kv7.5) channels,” *Neurobiology of Disease* 218 (2026), 107252. DOI [10.1016/j.nbd.2025.107252](https://doi.org/10.1016/j.nbd.2025.107252); PMID [41456614](https://pubmed.ncbi.nlm.nih.gov/41456614/); PMCID [PMC12906913](https://pmc.ncbi.nlm.nih.gov/articles/PMC12906913/).

This study obtained tissue from 46 pediatric patients (40 epilepsy, 6 controls; ages 1–21 years) and recorded from human neocortical L2/3 pyramidal neurons in acute slices. Whole-cell recordings were performed at approximately 33 °C and 10 kHz. The intrinsic and drug-response recordings were in **current clamp**, not voltage clamp. Cells were held near −55 mV while 100 μM 4-AP induced slow hyperpolarizing oscillations (HypOs) and network bursting.

Retigabine (50 μM), a KCNQ2–5 opener, eliminated HypOs in the reported five-cell experiment. XE991 (20 μM), a KCNQ blocker, produced only a modest reduction in HypO amplitude and frequency (n=4), comparable to time-dependent rundown. The authors interpret the results as KCNQ2–5 activation stabilizing network activity and potassium fluctuations. They do not report isolated human Kv7 current-voltage curves, activation/inactivation kinetics, recovery time constants, or single-cell KCNQ conductance density.

The data-availability statement is “Data will be made available on request.” The study therefore adds useful human L2/3 **network-level pharmacological** evidence, not direct Kv7 gating data or a public raw voltage-clamp dataset.

## 5. Cross-study comparison and HumanJS relevance

| Evidence source | Human preparation | Direct isolated K current? | Quantitative kinetics | Public raw traces/per-cell data located? | Main constraint |
|---|---|---:|---:|---:|---|
| Rüschenschmidt et al. (2004), J Neurosci Res | Acutely dissociated temporal neocortical neurons from epilepsy patients | Yes, A-type current | Activation, inactivation and recovery, n=5 | No | Small fit sample; abstract-level protocol detail; no layer/subtype or molecular subunit identification |
| Rüschenschmidt et al. (2004), Neurosci Lett | Acutely dissociated human temporal neocortical neurons | Yes, A-type current modulation | Drug-dependent inactivation, human n=5–9 depending comparison | No | Pharmacological modulation, not molecular identification; guinea pig results are separate |
| Beck et al. (1997), J Physiol | Acutely isolated human hippocampal dentate granule cells | Yes, delayed \(I_K\), \(I_A\), and calcium-dependent currents | Multiple voltage-dependence and time-constant summaries | No raw trace archive located | TLE tissue; \(I_A\) found only in a subset with AHS; not cortical pyramidal neurons |
| Kushner et al. (2026), Neurobiol Dis | Pediatric human neocortical L2/3 pyramidal neurons in acute slices | No isolated Kv current; network-level K-related oscillations | No Kv gate kinetics | No; available on request | Current clamp and network pharmacology, not voltage clamp |
| Mittermaier et al. (2024) | Human axonal whole-bleb Kv1 | Yes, axonal Kv1 | Processed activation/inactivation/recovery summaries | Raw human traces are not public | Axonal, processed/pseudonymized observations; not somatic L2/3 |
| Wilbers et al. (2023) | Adult human L2/L3 pyramidal-cell nucleated somatic patches | Yes, pharmacologically isolated aggregate voltage-gated K current | Activation/inactivation V1/2 and slopes; per-recording activation, fast/slow inactivation and recovery fit summaries | Public per-recording workbook data_fig4.xlsx; raw human K NWB sweeps not found | Mixed somatic K-current population without Kv subtype-selective isolation; excised soma is not AIS |

The Rüschenschmidt neocortical A-current study remains the most directly targeted human cortical transient-current summary, but its n=5 phenotype must not be equated with the broader K-current population measured by Wilbers in adult L2/L3 somatic patches. Wilbers' processed per-recording workbook is the strongest openly accessible quantitative human somatic K dataset found in this audit; it supports distribution-level comparisons to the published fit outputs, but does not allow independent refitting of the underlying currents. Beck's hippocampal data and Kushner's human L2/3 network-level KCNQ pharmacology remain distinct evidence classes.

The Rüschenschmidt A-current inactivation \(V_{1/2}\) (−98.9 ± 8.3 mV) and the small Beck figure-specific TEA-resistant transient-current estimate (−58.0 mV) differ substantially. They come from different preparations, sampling and protocols, and must not be averaged or treated as a single common parameter. The Beck A-current summary also depends on AHS pathology, and its tiny two-cell figure-specific parameter fit is not interchangeable with the Rüschenschmidt n=5 group summary.


## 6. Wilbers et al. (2023): adult human L2/L3 somatic K-current measurements and per-recording fit workbook

**Citation:** “Human voltage-gated Na+ and K+ channel properties underlie sustained fast AP signaling,” Science Advances 9 (2023), eade3300. DOI [10.1126/sciadv.ade3300](https://doi.org/10.1126/sciadv.ade3300); PMCID [PMC10569700](https://pmc.ncbi.nlm.nih.gov/articles/PMC10569700/). Public data/model/code deposit: [DataverseNL DOI 10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD), version 3.0, CC0-1.0.

### Human preparation and voltage-clamp method

The paper reports 19 adult human donors aged 21–70 years. Cortex was surgically removed to access a deeper lesion (medial temporal sclerosis or tumour); source regions were temporal (10 donors), frontal (5) and parietal (4). Human L2/L3 pyramidal neurons were identified morphologically and confirmed post hoc. The whole-cell current-clamp/AP cohort included 36 human L2/L3 cells; the K-current results below came from separate nucleated somatic patch recordings and have smaller recording counts.

For nucleated-patch K-current recordings, the Methods specify KCl internal solution, 1 μM TTX and 1 μM CdCl2 in the external recording solution, 34 °C, access resistance typically 3–5 MΩ and 60–85% series-resistance compensation. K-current traces were low-pass filtered at 2 kHz for analysis. This preparation samples excised somatic membrane; it does not include the AIS, dendrites or their spatial channel distributions. The pharmacological protocol blocks Na+ and Ca2+ currents but does not selectively isolate a named Kv subfamily, so the measured outward current should be treated as an aggregate somatic voltage-gated K-current phenotype.

The authors' public channel_tools.py source (Dataverse file 326242) implements K_IV with a 20-ms −140-mV starting segment, a 500-ms test step, a 50-ms +60-mV segment and a 100-ms final −140-mV segment; test commands in that helper run from −110 to +55 mV in 5-mV increments at 34 °C with a 0.1-ms integration step. This documents the deposited analysis/model protocol, not a recovery of the original acquisition files. The separate recovery helper uses a 2-ms −120-mV segment, a 5-s +40-mV conditioning period, variable recovery intervals and a 5-ms +40-mV test.

### What the public data_fig4.xlsx contains

The DataverseNL v3.0 inventory contains unrestricted Figure4/data_fig4.xlsx (file ID 318667; 108,029 bytes; SHA-1 30ba48520d8d27a7f4db8aaa6abc7ae0f80ba7d3). The workbook is publicly downloadable at [the Dataverse file-access endpoint](https://dataverse.nl/api/access/datafile/318667). Its tabular preview contains 43 recording rows (13 Human, 30 Mouse) and 241 fields. Human rows include the source NWB filename, steady-state activation/inactivation fits, goodness-of-fit fields, normalized conductance-versus-voltage arrays, per-voltage activation/inactivation time-constant arrays, fast/slow inactivation fractions and time constants, and paired-pulse recovery amplitudes and fitted recovery constants.

The 13 human rows are per-recording fitted summaries, not 13 confirmed independent donors. Their filenames reference original NWB files, but those original human K-current voltage-clamp NWB sweeps are not included in the inspected 65-file v3.0 deposit. The workbook therefore supports analysis of the released fit distributions but cannot reproduce the filtering, fitting or quality control from the raw acquisition traces.

### Human-only per-recording steady-state fits

The following statistics were recalculated from the 13 Human rows only, excluding blank cells and using sample standard deviation:

| Quantity | Per-recording mean ± SD | n |
|---|---:|---:|
| Activation V1/2 | −3.03 ± 5.95 mV | 13 |
| Activation Boltzmann slope | 13.87 ± 1.35 mV | 13 |
| Inactivation V1/2 | −52.69 ± 5.97 mV | 11 |
| Inactivation Boltzmann slope | 12.80 ± 1.87 mV | 11 |

These independently aggregated workbook entries reproduce the published human sample counts and closely match the group summaries in the paper (activation n=13; inactivation n=11). They are the mean and SD of per-recording nonlinear fit outputs; do not conflate them with a fit to the mean current/conductance curve or with the separate parameter values hard-coded as optimization targets in the deposited fitting script.

### Per-recording voltage-dependent kinetic summaries

The workbook also contains voltage-indexed fit arrays. The values below are recalculated as mean ± sample SD across available human recording rows; n varies where a fit is blank.

| Current-fit quantity | Command voltage | Mean ± SD | n |
|---|---:|---:|---:|
| Activation tau | +10 mV | 1.69 ± 0.71 ms | 13 |
| Activation tau | +20 mV | 1.36 ± 0.49 ms | 13 |
| Activation tau | +30 mV | 1.08 ± 0.33 ms | 13 |
| Activation tau | +40 mV | 0.96 ± 0.24 ms | 13 |
| Activation tau | +50 mV | 0.88 ± 0.21 ms | 13 |
| Fast inactivation tau | +20 mV | 43.16 ± 24.62 ms | 13 |
| Fast inactivation tau | +30 mV | 21.84 ± 7.07 ms | 13 |
| Fast inactivation tau | +40 mV | 23.54 ± 6.47 ms | 13 |
| Fast inactivation tau | +50 mV | 19.28 ± 4.69 ms | 13 |
| Fast inactivation tau | +60 mV | 26.16 ± 15.50 ms | 13 |
| Slow inactivation tau | +30 mV | 332.68 ± 205.01 ms | 13 |
| Slow inactivation tau | +40 mV | 308.22 ± 174.90 ms | 13 |
| Slow inactivation tau | +50 mV | 197.39 ± 55.45 ms | 13 |
| Slow inactivation tau | +60 mV | 290.00 ± 205.75 ms | 12 |

The slow component has wide between-recording variability, and at +60 mV one recording has no stored slow-fit value. The workbook includes lower-voltage fit entries as well, but their availability is more limited and some individual estimates are conspicuously large; the values above are a selected, transparent subset, not a new fit or a population-wide kinetic law.

The recovery fields contain per-recording biexponential summaries. Across available human rows, rec_tau1 is 254.54 ± 144.56 ms (n=12) and rec_tau2 is 2483.91 ± 1843.47 ms (n=11). These fits are descriptive workbook outputs; they should not be relabelled as a clean human-only recovery target without checking each recording's protocol and fit quality and the exact semantics of the helper.

### HumanJS activation-current fit consistency check (2026-11-18)

A new regression test in crates/humanjs-core/src/ion_channels.rs, named human_k_activation_current_fit_taus_fall_within_dataverse_per_recording_summary_spread, compares the Rust reproduction of the Wilbers K_IV activation current waveform with Human-only processed per-recording activation-fit summaries. It selects +10 through +50 mV, where all 13 workbook records have activation-fit \(R^2>0.95\) at each command voltage. The Rust replay uses the 34 °C Human K-channel model and the rising-phase exponential current-fit helper; it is not comparing microscopic channel-gate \(\tau_m\) values directly.

| Command | Human workbook mean ± SD (ms), n=13 | Minimum per-record fit \(R^2\) | Rust source-equivalent current-fit (ms) | Difference from workbook mean (ms) |
|---:|---:|---:|---:|---:|
| +10 mV | 1.6879 ± 0.7073 | 0.95530 | 1.70032 | +0.01245 |
| +20 mV | 1.3564 ± 0.4897 | 0.98092 | 1.33060 | −0.02580 |
| +30 mV | 1.0814 ± 0.3316 | 0.98484 | 1.08261 | +0.00125 |
| +40 mV | 0.9639 ± 0.2422 | 0.98420 | 0.90202 | −0.06193 |
| +50 mV | 0.8836 ± 0.2128 | 0.98741 | 0.77111 | −0.11250 |

The five-point RMSE of these rounded Rust fit references against the workbook means is 0.05885 ms. Every model output lies within one sample SD of the corresponding 13-recording Human distribution. This is a limited distribution-level consistency check, not an external validation: the model and workbook arise from the same Wilbers study, the recorded raw K-current NWB sweeps are unavailable, and the script that exported the per-recording workbook arrays was not found in the 65-file deposit. The regression test therefore checks that the already implemented source-equivalent activation replay remains in a plausible region of the released Human fit distribution; it does not independently reproduce the experimental current filtering/export algorithm.

#### Why the published Figure S5 activation markers are a separate comparator

The repository's existing HUMAN-L23-WILBERS-FIG-S5-I-ACTIVATION.csv is a manual digitization of human red markers from Supplementary Figure S5 panel I, not an arithmetic aggregation of the data_fig4.xlsx rows. Its approximate plotted human means are 3.36, 2.41, 1.68, 1.25, 0.88, 0.69 and 0.58 ms at −10, 0, +10, +20, +30, +40 and +50 mV, respectively, with conservative plot-reading uncertainty ±0.25 ms and ±1 mV (not biological SD). The workbook's first three means are close to the plotted markers, while its +40 and +50 mV means (0.9639 and 0.8836 ms) are higher than the digitized markers (0.69 and 0.58 ms) by approximately 0.274 and 0.304 ms. These differences modestly exceed the stated marker-reading uncertainty. The missing Experimental means/k_tau_act.csv, data_fig5.xlsx and workbook-export script prevent resolution of the aggregation/provenance difference. Neither data source should silently overwrite the other.

For context, the separate manual digitizations for Supplementary Figure S5 panels J and K broadly agree with the corresponding workbook means over their overlapping positive commands: the panel J human fast-inactivation markers are approximately 60.9, 43.4, 43.4, 21.7, 23.8 and 19.6 ms at 0 through +50 mV, while the workbook means are approximately 60.48, 43.24, 43.16, 21.84, 23.54 and 19.28 ms. The panel K slow-inactivation markers at +30/+40/+50/+60 mV are approximately 332.7/308.3/197.0/290.2 ms, versus workbook means 332.68/308.22/197.39/290.00 ms. Those plots are themselves manual group-mean digitizations with stated pixel-reading uncertainty, not raw observations or independent fits.

#### Scope deliberately not compared

No regression comparison is added for fast/slow inactivation or recovery. The deposited source-model K_IV helper fixes the slow inactivation component to 450 ms during its four-free-parameter fit, whereas the workbook stores per-recording fast and slow fit arrays whose export implementation is unavailable; the slow workbook means also vary widely with voltage. The workbook recovery protocol identifier and delay schedule likewise cannot be demonstrated to match the source helper's 5-s +40-mV conditioning sequence and recovery/test timing. These are useful evidence summaries, but a matched fit/protocol contract has not been established. No per-recording fast/slow or recovery summary is used as a HumanJS gate target.

## Historical Wilbers Dataverse v1.0 Figure 4 fields removed from v2/v3

A comparison of all three released Dataverse manifests found an additional, previously overlooked historical K-current summary layer in version 1.0.

| Release | Release time (UTC) | Manifest files | Figure 4 workbook |
|---|---|---:|---|
| v1.0 | 2022-11-10 10:59:42 | 126 | file 318537, 115,221 bytes, SHA-1 9a35cd30552efff3b5bf548d7313f71238a3a886 |
| v2.0 | 2022-11-10 14:34:35 | 65 | file 318667, 108,029 bytes in the later v3 release |
| v3.0 | 2022-12-13 12:12:16 | 65 | file 318667, 108,029 bytes, SHA-1 30ba48520d8d27a7f4db8aaa6abc7ae0f80ba7d3 |

The v1.0 workbook has 43 recordings (13 Human and 30 Mouse) and 272 fields. The v2/v3 workbook has the same 43 rows and 241 fields. A field-by-field comparison of all 241 shared columns across all 43 rows found **zero value differences**. Thus, the historical v1.0 workbook is an additive extension, not a different set of values for the shared activation, inactivation and recovery summaries.

The 31 fields present only in v1.0 consist of nine deactivation command-voltage labels, nine deactivation time-constant values, nine corresponding goodness-of-fit values, and four legacy scalar fields: reversal, amp1to200, tau_rec and ss_rec. All 13 Human rows are preserved, including missing values, in the CC0-derived subset at research/HUMAN-L23-WILBERS-FIG4-V1-HISTORICAL-EXTRA-K-FITS.csv. The file deliberately retains the legacy scalar field names rather than assigning unverified units or physiological meanings. The row index denotes workbook order after filtering Species=Human, not donor identity.

### Human v1.0 deactivation fit summaries

The v1.0 deactivation voltage grid is -120, -110, -100, -90, -80, -70, -60, -50 and -40 mV. The table below includes every nonblank Human tau_deact entry; no post hoc quality filtering is applied. Values are mean ± sample SD in milliseconds.

| Command voltage | Mean ± SD (ms) | n | Minimum stored gof_deact |
|---:|---:|---:|---:|
| -120 mV | 23.33 ± 7.75 | 4 | 0.81131 |
| -110 mV | 25.96 ± 10.86 | 5 | 0.83212 |
| -100 mV | 29.77 ± 11.71 | 2 | 0.80619 |
| -90 mV | 42.07 ± 34.28 | 4 | 0.87312 |
| -80 mV | 43.76 ± 23.81 | 4 | 0.83193 |
| -70 mV | 30.15 ± 15.40 | 3 | 0.82367 |
| -60 mV | 31.51 ± 15.22 | 8 | 0.86517 |
| -50 mV | 53.48 ± 22.64 | 10 | 0.91328 |
| -40 mV | 77.74 ± 33.09 | 10 | 0.88109 |

The corresponding stored gof_deact values vary considerably; the minimum at six of the nine command voltages is below 0.9. The source deactivation helper described below accepts a fit only for R-squared greater than 0.9, so it cannot simply be assumed that every stored v1.0 row was produced by that helper. The legacy scalar-field completeness is reversal 13/13, amp1to200 12/13, tau_rec 12/13 and ss_rec 12/13. One reversal entry is literally zero and is retained unchanged. The semantics and units of these scalar fields are not established by the released workbook and inspected analysis scripts; do not reinterpret tau_rec as the later double-exponential recovery tau pair.

### What the deposited deactivation helper does—and does not establish

The v1.0 and v3.0 channel_tools.py sources both contain a K_deact helper. It uses 34 °C, a 0.2-ms step, a 2-ms -120-mV segment, a 5-ms +60-mV segment and a 200-ms variable return-voltage segment. Its return-voltage array spans -90 to -35 mV in 5-mV increments. It fits a single exponential plus offset over 7.2 < t < 207 ms and returns tau only when R-squared exceeds 0.9. However:

- The K_deact call inside K_IV is commented out.
- The helper voltage grid (-90 to -35 mV by 5 mV) differs from the historical workbook grid (-120 to -40 mV by 10 mV).
- The workbook retains nonblank deactivation fits with gof_deact below 0.9.

Consequently, the historical workbook deactivation values cannot be attributed to this helper without further source provenance. Do not present the table above as an independent replay of K_deact or as a matched experimental gate-kinetic target.

The deposited plots_fig4.py and stats_fig4.py are downstream consumers of Data/data_fig5.xlsx; both scripts read that file rather than creating the v1.0 data_fig4 workbook. data_fig5.xlsx is absent from all three released manifests. The specific exporter that created data_fig4.xlsx and the precise processing path behind its v1-only fields therefore remain unidentified.

The full v1.0, v2.0 and v3.0 manifests were checked. None contains files with NWB, ABF, IBW or SMR acquisition extensions, data_fig5.xlsx, or the separate K tau Experimental means CSV filenames. This reinforces the distinction between the public processed workbook summaries and the still-unavailable original human K-current acquisition sweeps. The historical data expands the processed evidence catalogue; it does not provide raw-sweep refitting, a matched recording protocol, a named Kv subtype or grounds to change a HumanJS parameter.

### Remaining repository gaps and comparability

Neither the v1.0, v2.0 nor v3.0 inventory contains the separate Experimental means/k_tau_act.csv, k_tau_inact_fast.csv or k_tau_inact_slow.csv files read by the original fitting helper, data_fig5.xlsx referenced by the plotting/statistics scripts, or the original human K-current NWB acquisition sweeps. Version 1.0 additionally contains 31 processed deactivation/legacy scalar fields, now preserved in the historical subset above; those fields do not supply raw sweeps. The paper and repository provide the aggregate fit workbook and code, but not the complete raw-data chain needed for an independent trace-level refit and a bitwise reproduction of every plotted curve.

Do not combine these Wilbers aggregate somatic K-current fits with the Rüschenschmidt A-current n=5 values. The Rüschenschmidt abstract does not resolve its cortical layer/subtype, full voltage protocol, temperature or internal/external solution in the accessible text retrieved here. Its A-current was isolated by subtraction in acutely dissociated temporal neocortical tissue with TEA to reduce delayed K currents, whereas Wilbers measured a pharmacologically isolated aggregate somatic K-current in nucleated patches at 34 °C. Their steady-state inactivation midpoints (−98.9±8.3 versus −52.7±6.0 mV) describe different evidence definitions and should not be averaged or treated as a direct biological discrepancy between matched channel populations.

### Decision for HumanJS

- Correct the earlier repository-audit wording: a public per-recording Wilbers K-current fit workbook does exist; what is absent from the inspected v3.0 deposit is the original raw human K-current NWB sweeps and the separate Experimental means/k_tau_*.csv files.
- Use data_fig4.xlsx only as processed per-recording evidence, retaining each recording's fit quality and missing-value pattern. It is sufficient for a new transparent comparison against model-predicted steady-state and tau distributions, but not for independent raw-trace refitting.
- Do not identify the aggregate K-current as Kv1, Kv4 or Kv7, or infer subcellular AIS/dendritic densities from the nucleated-soma recording.
- Do not transfer the current workbook means directly into Rust. First compare equivalent command voltages, 34 °C kinetics, recorded fit definitions, series-resistance conditions and the distribution—not just one grand mean—of HumanJS gate outputs.
- ADR-014 remains open; no HumanJS Rust equation, gate, conductance density or spike-model parameter was changed by this source audit. The single-compartment mechanism remains exploratory and scientifically unaccepted.

This was a targeted source-repository audit, not a complete reanalysis of all 13 human recordings. The workbook summary values were parsed and aggregated from the public Dataverse tabular preview; the raw NWB sweeps and source Experimental means CSV inputs were not obtained.

## Additional human neocortical K conductances and developmental evidence (2026-11-17)

The following sources broaden the human K-conductance inventory, but they are not interchangeable with adult neocortical Kv activation/inactivation/recovery measurements.

### Jiang and Haddad (1997): temporal-neocortical KATP and BK-like single-channel conductances

**Citation:** C. Jiang and G. G. Haddad, “Modulation of K+ channels by intracellular ATP in human neocortical neurons,” Journal of Neurophysiology 77(1) (1997), 93–102. DOI [10.1152/jn.1997.77.1.93](https://doi.org/10.1152/jn.1997.77.1.93); PMID [9120601](https://pubmed.ncbi.nlm.nih.gov/9120601/). The publisher's full PDF is available [here](https://journals.physiology.org/doi/pdf/10.1152/jn.1997.77.1.93).

**Tissue and recording.** The authors obtained anterior temporal neocortical tissue, mostly from middle temporal gyrus, from epilepsy-surgery patients. The tissue was removed to gain access to the hippocampus and was judged to have normal excitability from intracranial and/or intraoperative recordings. They prepared 300-µm slices, enzymatically incubated them, and dissociated grey matter presumed to include layers III–V. Cells were selected for a pyramidal-shaped soma with one thick proximal dendrite and no visible injury; laminar and molecular subtype identity were not established.

Experiments were performed at approximately 24 °C. Whole-cell currents used perforated-patch voltage clamp; single-channel currents used excised inside-out patches. The main single-channel protocol used symmetric 150-mM K+ solutions. The article examined human and rat neurons, but the results below are human-only unless explicitly stated otherwise.

**Conductances and pharmacology.**

- **Small-conductance ATP-sensitive K+ channel (S-KATP):** observed in nine patches from approximately 80 human neocortical neurons studied (one patch per cell). Single-channel conductance was 47 ± 3 pS (n=9), with strong inward rectification. ATP inhibited channel activity concentration-dependently (IC50 approximately 130 µM); ADP, AMP-PNP and glibenclamide also inhibited it. The article shows rapid reduction in open probability after ATP application and recovery after washout.
- **Large-conductance ATP-sensitive K+ channel (L-KATP):** examples had unitary conductances around 180 and 230 pS and weak inward rectification. The group was inhibited by ATP (IC50 approximately 350 µM), AMP-PNP and glibenclamide. Activity required micromolar cytosolic Ca2+, but charybdotoxin did not block it. The exact human cell/patch n for this component was not stated in the passages inspected, so no population sample count is assigned here.
- **Large-conductance Ca2+-activated BK-like channel:** observed in eight patches from 15 human neocortical neurons (one patch per cell). Slope conductance was 277 ± 24 pS (n=8). The channel was voltage activated, lacked inward rectification, and was almost completely blocked by external charybdotoxin (50 nM), iberiotoxin (100 nM), or TEA (2 mM); internal TEA above 40 mM did not block it. ATP increased open probability (0.096 ± 0.011 to 0.172 ± 0.014, n=5) and unitary conductance (267 ± 6 to 295 ± 7 pS, n=5). It was not inhibited by glibenclamide.

The authors also demonstrated a levcromakalim-sensitive whole-cell inward current at a holding potential of −60 mV under symmetric K+, low-Na+ and Co2+ conditions; levcromakalim (5 µM) increased the current and glibenclamide (20 µM) blocked it. This is a pharmacologically identified KATP current, not a voltage-gated Kv activation/inactivation assay.

**Interpretation and limits.** This is direct human neocortical evidence for metabolic KATP conductances and a Ca2+- and voltage-activated BK-like single-channel conductance. It complements the A-current and delayed-rectifier literature, and is relevant to energy-state regulation and calcium-dependent repolarization. It does **not** provide classical Kv1/Kv4/Kv7 activation, steady-state inactivation or recovery kinetics. The inside-out excised-patch preparation does not preserve cell compartments or whole-cell dendritic/axonal context. The selected cells were morphologically pyramidal-like and presumed to derive from layers III–V, but this is not equivalent to a laminar molecularly identified cell class. No public per-patch raw recording archive was located in this review.

### Lorenzon and Foehring (1992): human neocortical afterhyperpolarization conductances

**Citation:** N. M. Lorenzon and R. C. Foehring, “Relationship between repetitive firing and afterhyperpolarizations in human neocortical neurons,” Journal of Neurophysiology 67(2) (1992), 350–363. DOI [10.1152/jn.1992.67.2.350](https://doi.org/10.1152/jn.1992.67.2.350); PMID [1373765](https://pubmed.ncbi.nlm.nih.gov/1373765/).

The study combined intracellular recordings in human neocortical slices with pharmacological manipulations. It characterized fast, medium and slow afterhyperpolarizations (AHPs), and repetitive firing/adaptation during long depolarizing current injections. It is **not** an isolated voltage-clamp K-current study.

- Fast AHP reversal was approximately −65 mV. It was eliminated by extracellular Co2+, TEA or 4-AP and by intracellular TEA or CsCl; these interventions also broadened spikes.
- Medium AHP reversal was approximately −90 to −93 mV. It was reduced by Co2+, apamin, tubocurare and several neuromodulators; the authors inferred contributions from a Ca2+-dependent K+ current and Ih.
- Slow AHP reversal was approximately −83 to −87 mV. Its pharmacology was consistent with a slowly acting Ca2+-dependent K+ current.
- Human neurons showed spike-frequency adaptation and habituation under repeated 1-s current stimuli. The mean steady-state f–I slope reported in the abstract was 57.8 Hz/nA.

These are useful human functional constraints on repolarization, AHPs and firing adaptation, but do not identify Kv subunits, gate activation/inactivation curves, recovery constants or channel densities. Do not reinterpret the TEA/4-AP-sensitive fast AHP as a molecularly specific Kv current.

### Sah (1995): fetal human central-neuron voltage-gated K+ current classes

**Citation:** D. W. Sah, “Human fetal central neurons in culture: voltage- and ligand-gated currents,” Journal of Neurophysiology 74(5) (1995), 1889–1899. DOI [10.1152/jn.1995.74.5.1889](https://doi.org/10.1152/jn.1995.74.5.1889); PMID [8592182](https://pubmed.ncbi.nlm.nih.gov/8592182/). The accessible [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/8592182/) describes dissociated monolayer cultures of fetal human brain neurons studied with whole-cell patch clamp.

The abstract reports at least two K+ current classes resembling a delayed rectifier and a fast-inactivating current. They differed in kinetics, voltage dependence of activation/inactivation, and sensitivity to 4-aminopyridine and TEA. The abstract does not provide quantitative K-current parameters, sample sizes, fetal age, exact brain region for the K-current subset, or a raw-data repository. The article includes comparisons of cortical and cerebellar ligand-gated responses, but that does not establish the anatomical origin of each reported K-current class.

This is direct human developmental-neuron current evidence at the broad level, but it is not an adult temporal-neocortical or L2/3 pyramidal-cell parameter source. Treat its K-current classes as qualitative fetal-culture evidence only; no numeric Kv gate values are inferred.

### Decision for HumanJS

- Correct the earlier statement that no direct human cortical Kv current evidence had been identified: published human neocortical A-type current kinetics do exist.
- Retain the stricter data-access statement: no public raw human neocortical K-current sweep dataset or per-cell kinetic table suitable for independent trace refitting was located in this review.
- Do not infer Kv4 molecular identity, layer-specific distribution, AIS/somatic density, or cortical pyramidal-cell subtype from the A-current phenotype alone.
- Do not transfer the reported \(V_{1/2}\), slope, or recovery values into Rust yet. First reconcile protocol details, preparation, temperature, pharmacological isolation, current definition, series-resistance effects, and population/anatomical differences with the target HumanJS cell class.
- Keep hippocampal dentate data, cortical temporal-lobe A-current data, temporal-neocortical KATP/BK currents, human AHP pharmacology, fetal-culture K currents, axonal Kv1 summaries, and human L2/3 network-level KCNQ pharmacology as distinct evidence classes.
- No Rust equation, gate, conductance density, temperature parameter, or spike-model parameter was changed by this review. ADR-014 remains open; the single-compartment spike-capable model remains exploratory and unaccepted.

The review was a targeted literature and public-repository search, not a systematic review of all human neuronal potassium-current publications. No authors or researchers were contacted.
