# Human neuronal potassium-current voltage-clamp evidence: neocortical A-type and hippocampal currents

**Reviewed:** 2026-11-17  
**Scope:** Published human neuronal voltage-clamp current summaries and related human network-level KCNQ evidence.  
**Status:** Direct human neocortical A-type current kinetics and human hippocampal K-current measurements are documented below. Public raw sweeps and per-cell records sufficient for an independent refit were not located in this review. This note does not authorize parameter transfer into HumanJS.

## Executive finding

The previous 2026-11-15 literature screen was too narrow in its wording. A follow-up search located two primary studies reporting direct human voltage-clamp potassium currents:

1. Rüschenschmidt et al. (2004) characterize a fast transient A-type current in acutely dissociated human temporal neocortical neurons from epilepsy surgery tissue. The PubMed abstract reports activation, steady-state inactivation and recovery summaries from five cells.
2. Beck et al. (1997) characterize voltage- and calcium-dependent K currents in acutely isolated human hippocampal dentate granule cells. Their open full-text article reports a delayed outward current in all 34 recorded neurons and an A-type current in six neurons from three patients with Ammon's horn sclerosis.

These papers establish that direct human neuronal K-current measurements and published kinetic summaries exist beyond the previously considered Wilbers and Mittermaier sources. They do **not** supply a public raw-trace/per-cell repository in the sources reviewed here. The neocortical A-type study has small reported kinetic-fit samples and does not identify a molecular Kv subunit or a specific cortical layer/cell class in its abstract. The Beck study is hippocampal dentate-granule-cell evidence, with important pathology-dependent differences; it is not cortical pyramidal-cell evidence.

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
| Wilbers et al. (2023) | Human somatic nucleated-patch Na/K source study | Published measurements and deposited source/model protocols | Model/source reproductions and published summaries | Raw human K NWB sweeps not found in inspected DataverseNL v3 inventory | Model-generated protocol replay is not raw experimental trace refitting |

The Rüschenschmidt neocortical A-current study is now the most directly relevant located human cortical voltage-clamp kinetic summary for a transient outward current. Beck et al. add direct human hippocampal \(I_K\) and \(I_A\) evidence, but must remain anatomically and pathologically separate. Kushner et al. (2026) add an independent type of evidence: KCNQ modulation of human L2/3 network excitability, not direct Kv7 gate measurements.

The Rüschenschmidt A-current inactivation \(V_{1/2}\) (−98.9 ± 8.3 mV) and the small Beck figure-specific TEA-resistant transient-current estimate (−58.0 mV) differ substantially. They come from different preparations, sampling and protocols, and must not be averaged or treated as a single common parameter. The Beck A-current summary also depends on AHS pathology, and its tiny two-cell figure-specific parameter fit is not interchangeable with the Rüschenschmidt n=5 group summary.


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
