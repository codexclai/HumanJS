# Human axonal Kv1 evidence: Mittermaier et al. (2024)

**Reviewed:** 2026-11-15  
**Status:** public preprocessed human axonal evidence independently reanalysed; not a substitute for somatic nucleated-patch targets or raw current traces.

## Primary sources and provenance

- Franz X. Mittermaier et al., “Membrane potential states gate synaptic consolidation in human neocortical tissue,” Nature Communications 15, 10340 (2024), published 2024-12-12. [DOI: 10.1038/s41467-024-53901-2](https://doi.org/10.1038/s41467-024-53901-2).
- Public data and original R scripts: [Figshare DOI: 10.6084/m9.figshare.24793218.v1](https://doi.org/10.6084/m9.figshare.24793218.v1). Dataset version 1, posted 2024-09-30, CC BY 4.0. The deposit explicitly describes the tables as pseudonymized and preprocessed data used to create the paper's figures, and includes the original R scripts.

The paper's whole-bleb electrophysiology is relevant to human neocortical axonal Kv1-mediated current, but the preparation is distinct from the nucleated somatic patch used by Wilbers et al. (2023). It does not directly measure somatic gate kinetics or provide an AIS-resolved functional channel-density map. Do not substitute these axonal values into the Wilbers somatic mechanism.

## Preparation and protocol

The paper reports patch-clamp measurements in acute human neocortical slices obtained during neurosurgery. Kv measurements used a voltage-clamped axonal bleb in the whole-bleb configuration. The Methods describe 35 ± 2 °C recordings, −P/4 leak/capacitance subtraction, TTX 0.5 μM and XE991 10 μM in the ACSF, and 10 mM intracellular EGTA for voltage-clamp experiments. The liquid-junction potential was −15.2 ± 0.5 mV and command voltages were not corrected for it. The potassium reversal potential for the recording solutions was −105 mV.

The deposited author R scripts document these protocols:

| Protocol | Voltage sequence | Public source observations |
|---|---|---|
| Activation | Hold −80 mV; 200 ms prepulse to −110 mV; test steps −90 to +70 mV in 20 mV increments | 9 experiment IDs × 9 voltages = 81 normalized observations |
| Steady-state inactivation | Hold −80 mV; 5 s conditioning steps −110 to 0 mV in 10 mV increments; test pulse +40 mV | 5 experiment IDs × 12 voltages = 60 normalized observations |
| Long inactivation | 3 s depolarization from −80 to +20 mV | 20 processed normalized traces, each 145,001 samples from 0.02 to 2900.02 ms at 0.02 ms spacing |
| Recovery | After the 3 s +20 mV pulse, return to −80 mV for 100, 300, 1000, or 3000 ms before a brief +20 mV test | 20 table rows over five experiment IDs and four intervals; the R script adds one t=0 anchor from the terminal long-inactivation trace |
| DTX-I | Repeat activation before/after local 500 nM dendrotoxin-I application | 5 paired recordings |

The article reports axonal Kv sample sizes n=9 for activation, n=5 for inactivation, n=5 for recovery/long-inactivation and n=5 for toxin experiments. Source-table experiment/trace identifiers are pseudonymized; the 20 long-pulse traces are repeated processed observations, not evidence for 20 independent donors or cells.

## Public files and integrity

The Figshare deposit includes these Kv tables and the original analysis scripts:

- t_Kv_activation_voltage_psd.csv (3,502 bytes)
- t_Kv_inactivation_voltage_psd.csv (2,619 bytes)
- t_Kv_recovery_psd.csv (927 bytes)
- t_Kv_toxin_psd.csv (441 bytes)
- t_Kv_long_inactivation_psd.csv (154,469,163 bytes)
- R_script_files.zip (43,915 bytes), including Kv_act_inact_curves.Rmd, Kv_recov_inact.Rmd and Kv_toxin.Rmd

SHA-256 checksums used by the HumanJS reproduction:

| File | SHA-256 |
|---|---|
| Activation | a2e44974b3691c9f9078e9bae91c61089cac16a0beb5ec5bbc578a693c38fc75 |
| Inactivation | 0e97dc80027de9e37f9e732aa383d65f6fe61a1075770e11e70d297824cc0590 |
| Recovery | f8a429419040ab07d88b47903ba7f27591567079b7bf2fc1187df9fcfe04fad5 |
| Toxin | 09feb2c5f27595a0f6acaf8d8ba049dd808efaeae08bf377ba88c1366aadea36 |
| Long inactivation | d0f27bfaf107c7d53c4ea2737973a33dd71d682bd477a49a38d747e324a58909 |
| R script archive | b722842a0e9ba99dedf2e5105741b2363ec84e92434c3598a99ab68cecba25d3 |

The paper's data-availability statement says raw electrophysiological trace files from human samples cannot be made public because of German and European privacy-law restrictions. The Figshare files are processed/pseudonymized tables, not original raw voltage-clamp sweeps. Therefore no independent raw-sweep re-fit or trace-level noise analysis is possible from this deposit.

## Reproduction of the author analysis

The original R scripts were retrieved and inspected. HumanJS's Python analyzer reproduces the source-table transformations and saves per-recording outcomes alongside two distinct aggregate views.

1. **Author-equivalent pooled fit:** the R activation/inactivation script normalizes chord conductance within each experiment by its own Gmax, then fits one Boltzmann nls curve to all normalized observations pooled across experiments (81 activation and 60 inactivation points). It does not fit the group-mean curve. The Python analyzer explicitly retains this as activation_pooled_observations and inactivation_pooled_observations.
2. **Group-mean curve fit:** the Python analyzer separately fits the arithmetic mean of the normalized per-recording curves on the shared voltage grid. This is a descriptive fit, not the authors' pooled-data estimator. Results happen to be close for this dataset but the estimators are distinct.
3. **Per-recording curves:** the five/nine source experiment IDs are fitted independently for descriptive heterogeneity. These pseudonymous IDs must not be reinterpreted as donor IDs.

Direct execution of the archived original R pooled nls fits yielded:

| Pooled source fit | V1/2 (mV) | Slope (mV) | R-script bottom | R-script top |
|---|---:|---:|---:|---:|
| Activation | −6.62907347 | 24.23965052 | −0.04025787 | 1.03462682 |
| Inactivation | −43.3419644 | 12.6233452 | 0.9915642 | 0.1478343 |

The Python pooled fit uses an explicitly decreasing logistic for inactivation, so its low/high asymptote field names are reversed relative to the R equation's bottom/top labels. V1/2 and slope are directly comparable. Python/R estimates differ slightly because the nonlinear least-squares implementations differ; they are not bit-identical.

The author's long-inactivation R script first averages all processed traces by time point, then fits y = a exp(−t/t1) + b exp(−t/t2) + (1−a−b), using starting values a=0.55, b=0.2, t1=1500 ms, t2=150 ms. Direct R execution returned t1=1330.3305 ms, t2=120.1067 ms. The HumanJS script computes the same time-point mean and model; its sorted output is tau_fast=120.105632 ms, tau_slow=1330.319646 ms, offset=0.408140773, RMSE=0.007828645. The input hash and exact 20 × 145,001 sample layout are checked before fitting.

The R recovery script derives its t=0 anchor as the mean of samples 144900:145000 of the 145,001-point mean trace (0.4423915697884116), appends the 20 four-delay recovery observations, and fits the analogous two-exponential recovery curve. The original R fit returned approximately tau_fast=110.6775 ms and tau_slow=1013.4574 ms; the source-matched Python fit returns 110.684712 and 1013.485386 ms. There are only four experimental delay values; the zero-time point is a derived anchor, not an independent measurement. The five DTX-I block fractions give mean 0.546260, sample SD 0.133461 and SEM 0.059685 (n=5).

The compact and long-inactivation CSV summaries are committed as references and compared field-by-field in CI. The workflow downloads the large public table, checks its SHA-256, regenerates the 20-trace fit, and compares every output field. The R archive is not copied into the repository; the Figshare DOI provides its public provenance.

## Interpretation limits and model boundary

- These are axonal whole-bleb measurements, not Wilbers' somatic nucleated-patch data. They do not provide a somatic K-gate replacement or complete AIS channel-distribution evidence.
- DTX-I block supports a Kv1-family contribution under the stated conditions; it is not a molecular-subunit-specific assay or full channel-composition measurement.
- Activation/inactivation are normalized chord-conductance curves using the source potassium reversal of −105 mV; command voltages are not corrected for the stated liquid-junction potential.
- Long-inactivation and recovery are group summary fits, not per-cell kinetic distributions. Recovery relies on four experimental delay values plus one derived zero-time anchor.
- The source deposit has no raw human traces. These findings do not establish raw-trace fit uncertainty, biological validation, Rust K-gate kinetics or AIS channel density.

No Rust channel equation, gate, conductance density, or model parameter is changed by this evidence audit.
