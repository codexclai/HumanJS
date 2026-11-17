# Human L4 IT nucleated-patch K-current evidence and raw NWB audit

**Reviewed:** 2026-11-18  
**Scope:** Direct human neocortical perisomatic potassium-current experiments from the 2026 Dalley et al. multimodal Patch-seq study and its open DANDI NWB release.  
**Status:** Raw human nucleated-patch voltage-clamp current and command series are publicly available. A metadata-only audit identified seven candidate NWB assets and inspected one asset at series and waveform level. Exact cell-subclass mapping, absolute command-voltage calibration, current subtraction, nucleus-area normalization and kinetic refitting are not complete. No HumanJS parameter transfer is authorized.

## 1. Primary source and deposit

**Citation:** Dalley et al., “Human neocortical glutamatergic neurons revealed through multimodal profiling,” Cell Reports (published online 2026-11-12), DOI [10.1016/j.celrep.2026.118269](https://doi.org/10.1016/j.celrep.2026.118269); [full article](https://www.sciencedirect.com/science/article/pii/S2211124726013483).

The paper's Data and Code Availability statement specifies:
- Electrophysiology in NWB format: [DANDI:002018](https://dandiarchive.org/dandiset/002018).
- Morphological reconstructions in SWC format and TIFF image stacks: [Brain Image Library, DOI 10.35077/g.1223](https://doi.org/10.35077/g.1223).
- Original code and extracted features: [AllenInstitute/human_patchseq_excitatory](https://github.com/AllenInstitute/human_patchseq_excitatory).

The inspected DANDI release was version 0.261117.2218, published on 2026-11-17, DOI [10.48324/dandi.002018/0.261117.2218](https://doi.org/10.48324/dandi.002018/0.261117.2218). It contains 163 NWB assets (approximately 6.04 GB) and is released under CC BY 4.0. This is a distinct source from the Wilbers 2023 DataverseNL deposit.

## 2. Published current-isolation protocol

The final Cell Reports STAR Methods describes perisomatic potassium-current measurements in Giga-seal nucleated patches:

1. Capacitance transients were compensated during pipette approach.
2. Patches were held at −90 mV. Total current (I_total) was recorded using 1-s voltage steps in 15-mV increments from −65 to +70 mV.
3. Leak current was recorded with a −10-mV command for 1 s while the cell was held at −90 mV. The leak waveform was scaled to match the original step protocol and digitally subtracted from I_total.
4. To estimate the slowly inactivating delayed-rectifier component (I_K), the step family was repeated after a 125-ms +70-mV prepulse while the cell was held at −20 mV, intended to substantially inactivate the A-current.
5. The A-type component was calculated as I_A = I_total − I_K.
6. The nucleus was imaged during nucleated-patch formation. Its ellipsoid surface area was measured in ImageJ, and currents were divided by this area to obtain current density.

Figure 4G compares current-density components across L4 IT subclasses. The paper reports the lowest peak outward K-current density in L4 IT_4, the highest in L4 IT_1, and the largest rapidly inactivating A-type component in L4 IT_1. It also reports an association between I_A and AP downstroke speed, with KCND2/KCND3 expression associated with downstroke speed. These results describe cell-class-associated macroscopic current phenotypes; they do not provide microscopic Kv gate equations or kinetic constants.

## 3. Reproducible NWB inventory audit

A metadata-only scan used HTTP byte-range reads of HDF5/NWB metadata for all 163 assets in DANDI:002018 version 0.261117.2218. All 163 files opened successfully, each contained at least one VoltageClampSeries, and the scan recorded zero metadata-read errors. This did not download the full 6-GB corpus or fit currents from all files.

Seven assets contain named nucleated-patch voltage-clamp protocol families. Six have session metadata dated 2022–2025; one additional asset is dated 2018 and is treated as a legacy/provenance-separated candidate rather than presumed to belong to the 2026 article's analyzed cohort.

**Six 2022–2025 candidate asset UUIDs:**
- 050d8369-dd67-4f93-b825-51b74a46a6c7
- 44b87d2f-8c36-46af-9f17-049c17bfaf56
- 4011c6ca-454e-42dd-acbd-747e06932dbb
- d737cf6f-b00b-43a5-930c-1a6127541767
- ffa5f98e-7542-4521-8e6c-9ff75c8cc22d
- bf1c6a2f-c7a1-4162-b5db-5a281584c5dd

**Legacy 2018 candidate asset UUID:** 98c62990-9971-47a0-80a3-af1d442ebaf7.

Asset UUIDs are public DANDI identifiers and deliberately replace pseudonymous subject/file paths. For example, the first candidate has a public record at [DANDI asset 050d8369-dd67-4f93-b825-51b74a46a6c7](https://api.dandiarchive.org/api/assets/050d8369-dd67-4f93-b825-51b74a46a6c7/).

## 4. Deep inspection of one candidate NWB asset

Asset 050d8369-dd67-4f93-b825-51b74a46a6c7 was examined at series and representative waveform level. It is NWB 2.3.0 and contains 127 acquisition groups, 127 stimulus groups, and 70 VoltageClampSeries. Sixty-four voltage-clamp series carry nucleated-patch protocol-family names. Current and command series are paired; sampling is 12.5 kHz.

The observed protocol families include:
- NucVCLS0: nine 1-s voltage-step sweeps.
- NucVCLS1Leak: ten leak-control sweeps.
- NucVCprepulse: nine prepulse/test sweeps.
- NucVCSus0 and NucVCSus1Leak: sustained-step and leak-control families.
- NucVCzrecovms5, NucVCzrecovms100 and NucVCzrecovs1: recovery-labelled families.

The raw command metadata for this asset includes a −20-mV baseline command, a leak command 10 mV below that baseline for 1 s, and a prepulse command 70 mV above baseline. The prepulse series has an approximately 100-ms +50-mV command segment followed by the 1-s test command. The first NucVCLS0 family contains nine test commands at +20, +35, …, +140 mV in the recorded command coordinate, separated by 15 mV and bracketed by the −20-mV baseline. The paired acquisition series contain recorded current waveforms in amperes with NWB conversion metadata; the paired stimulus series contain the recorded command waveforms.

This verifies that the public NWB release contains actual human voltage-clamp waveforms, not only feature summaries. It verifies broad correspondence with the published leak, prepulse and recovery experiment families, but it does not establish a literal, calibrated replay of every nominal voltage and duration in the paper.

## 5. Protocol and calibration discrepancies

The raw metadata inspected so far leaves several important discrepancies:

- The first asset's NucVCLS0 family contains nine activation/test sweeps, whereas the paper's inclusive −65-to-+70-mV range at 15-mV increments describes ten nominal levels.
- The NucVCprepulse waveform contains an approximately 100-ms prepulse command. The paper specifies 125 ms.
- The inspected NWB VoltageClampSeries, VoltageClampStimulusSeries, electrode description and ITC18USB device metadata do not expose an absolute command-voltage offset or holding-potential calibration. Thus, the raw command coordinates cannot be relabelled as absolute membrane voltages solely from the available NWB metadata. The article's nominal values are a protocol reference, not proof of a calibrated per-file offset.
- The paper normalizes currents by nucleus surface area measured from images. That area was not present in the inspected NWB electrode metadata, and the mapping between each NWB asset and its nucleus image has not yet been established.

The presence of similarly named Nuc protocol series in the 2018 legacy asset also does not prove that it was part of the 2026 study's analyzed cohort.

## 6. Evidence boundary and HumanJS implications

This finding supersedes the broad earlier statement that no public raw human neocortical K-current voltage-clamp sweeps exist. The correctly scoped distinction is:

- **Wilbers 2023:** the inspected Wilbers DataverseNL release still lacks its original human K-current NWB/ABF acquisition sweeps and separate Experimental-means fitting inputs. Its per-recording workbook remains processed evidence.
- **Dalley et al. 2026:** a separate public DANDI release contains raw human neocortical nucleated-patch voltage-clamp current and command series, including candidate leak, prepulse, sustained and recovery protocols. The seven UUIDs above are candidate files, not seven verified L4 IT experimental replicates.
- **Analysis completeness:** all 163 NWB assets have had metadata inspected; one candidate has had its series and representative raw waveforms inspected. No trace-level leak correction, I_K/I_A subtraction, nucleus-area normalization, current-density analysis, kinetic fit, or L4 IT subclass mapping has yet been reproduced.
- **Model implication:** these data broaden the human K-current evidence base, but do not yet supply a calibrated, cell-type-matched and area-normalized kinetic target for the HumanJS L2/L3 exploratory model. Do not infer a Kv subtype, transfer a gate parameter, alter Rust, or claim biological validation.

## 7. Next evidence work

1. Map the six 2022–2025 candidate assets to the released electrophysiology feature and cell-class tables without copying donor identifiers into the repository. Keep the 2018 legacy asset separate until its provenance is resolved.
2. Recover per-recording amplifier/clamp calibration and holding-offset metadata from original acquisition configuration or other deposited provenance. Resolve the activation-step count and 100-ms-versus-125-ms prepulse discrepancy before assigning absolute voltages.
3. Locate the corresponding nucleus images and their mapping to each nucleated patch. Reproduce surface-area normalization with uncertainty recorded.
4. Reproduce published I_total, scaled leak, I_K and I_A calculations on raw waveforms with explicit units, command windows, signs and per-recording QC. Preserve missingness and failed recordings.
5. Only after the protocol, voltage, current-density and subclass mappings are established should distribution-level comparison against HumanJS mechanism outputs be considered. Do not fit a new Rust gate or conductance from the metadata-only audit.

No authors or researchers were contacted. No Rust equation, gate, conductance density, temperature parameter or spike-model parameter changed. ADR-014 remains open; the single-compartment spike-capable model remains exploratory and unaccepted.
