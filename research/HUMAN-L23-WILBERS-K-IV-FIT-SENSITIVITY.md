# Wilbers K_IV fast-inactivation fit: initialization and profile sensitivity

**Date:** 2026-11-13  
**Status:** source-model numerical audit; not an experimental human-current refit or biological validation.

## Question and source identity

The deposited K_IV replay reproduces the original human potassium mechanism and analysis helper, but repeated hosted runs returned different accepted fast-inactivation time constants at the same command voltage. This record investigates whether the difference is caused by the nonlinear optimizer's starting values and whether the fitted \(\tau_1\) is well constrained by the deposited source waveform.

The source artifacts were retrieved from the CC0-1.0 DataverseNL v3.0 deposit (DOI [10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD)):

- `channel_tools.py`, file 326242, SHA-1 `615595a270c6170987757cd35743f5d5b5b2af0e`.
- `k_human.mod`, file 318647, SHA-1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`.
- `fit_k_hh_cma_human.py`, file 326237, SHA-1 `c819e59813acd70fae7af7151752bb1d8bbc7357`.

The analysis follows the deposited helper used in the Wilbers human L2/L3 pyramidal-cell model ([Science Advances article](https://doi.org/10.1126/sciadv.ade3300)). The original NMODL and source helper were not patched.

## Exact helper behavior

The released `get_tau_inact_double_fixedtau2(x, y, est1=30, tau2=450)` function fits

\[
I(t)=a_1 e^{-t/\tau_1}+a_2 e^{-t/450\,\mathrm{ms}}+s_s
\]

with free parameter order `(a1, tau1, a2, ss)`, nonnegative bounds on all four fitted parameters, \(0 < \tau_1 \le 300\) ms, fixed \(\tau_2=450\) ms, and a source acceptance threshold R² > 0.95. It first shifts the supplied time vector by `x = x - x[0]`.

The exact source initial vector is

```python
p0 = ((y[0] - y[-1]) * 0.5,
      (y[0] - y[-1]) * 0.5,
      est1,
      y[0] * 0.1)
```

This is four values for four free parameters; the fixed slow time constant is not a fifth fitted parameter. The earlier five-versus-four arity-error claim is false and remains retracted.

There is, however, a striking parameter-scale mismatch in that initial vector under the source replay's current-density units. At −70 mV:

- \( (y_0-y_{end})/2 = 3.141640790281283\times10^{-5}\) mA/cm².
- That current-density value is also passed as the initial \(\tau_1\) in milliseconds: \(3.141640790281283\times10^{-5}\) ms.
- The default `est1=30` is passed into \(a_2\), i.e. an initial amplitude of 30 mA/cm².
- The observed activation-current peak is 0.000500295140138606 mA/cm², so this initial \(a_2\) is about 59,965 times that peak.

The source therefore seeds a time constant with a current-density difference and an amplitude with a value many orders above the observed current. This is a directly observed parameter-order/scale mismatch and a strong candidate for poor optimizer conditioning. It is not proof of the source author's intent, and the original helper has deliberately been left unchanged.

## Same-waveform multi-start experiment

The runner now captures the exact post-peak NEURON samples passed to the original helper at each attempted K_IV voltage. On each unchanged waveform it runs the same equation, time shift, fixed \(\tau_2\), bounds and R² gate from six initial vectors: the exact source vector and five controlled alternatives varying \(\tau_1\) and the nonnegative amplitude split. Only the initial vector changes.

The result has 192 rows: six starts at each of 32 source-fit-attempted voltages. All 192 numerical optimizations converged. The source's R² > 0.95 gate accepts 27/32 source-literal results; the five alternative starts are accepted at 32/32, 32/32, 30/32, 32/32 and 32/32 voltages, respectively.

At −70 mV, all six starts pass the source gate but converge to materially different fast time constants despite similarly high R²:

| Initialisation | Fitted \(\tau_1\) (ms) | R² |
|---|---:|---:|
| Exact source vector | 213.8193 | 0.999994545 |
| \(\tau_1\)=30 ms, equal amplitudes | 196.0183 | 0.999991938 |
| \(\tau_1\)=100 ms, equal amplitudes | 186.6256 | 0.999990012 |
| \(\tau_1\)=200 ms, equal amplitudes | 212.8816 | 0.999994504 |
| \(\tau_1\)=100 ms, slow amplitude 25% | 200.1972 | 0.999992661 |
| \(\tau_1\)=100 ms, slow amplitude 75% | 186.6098 | 0.999990023 |

The accepted −70-mV spread is 27.2095 ms. Across all attempted voltages, the largest within-voltage spread is 111.4199 ms at −85 mV (five accepted starts). The result confirms that the fitted fast component is initialization-sensitive on a fixed waveform; the very high R² values alone do not establish a unique \(\tau_1\).

## Fixed-`tau1` profile

A second diagnostic profiles the same −70-mV post-peak waveform over \(\tau_1\). At each grid value, \(a_1\), \(a_2\), and \(s_s\) are solved by nonnegative bounded linear least squares. This exactly minimizes the linear subproblem for that fixed \(\tau_1\); it is a diagnostic profile, not a replacement for the deposited `curve_fit`.

Two grids were recorded:

| Profile domain | Grid | Best sampled \(\tau_1\) | Best R² | RMSE (mA/cm²) |
|---|---:|---:|---:|---:|
| 0.05–300 ms (source bounds) | 601 points | 300 ms (upper bound) | 0.999999324534 | \(1.47586\times10^{-8}\) |
| 0.05–1200 ms (extended counterfactual) | 901 points | 338.2372 ms | 0.999999577007 | \(1.16791\times10^{-8}\) |

Within the extended profile, the 1%-of-minimum-RMSE band spans approximately 334.468–345.904 ms (four grid points). The broader band within 10⁻⁶ of the maximum R² spans approximately 270.323–361.762 ms (27 points). The best sampled profile point is therefore outside the source's 300-ms upper bound, while the best point inside that bound lies exactly on its boundary.

This is evidence that the deposited fit is boundary-sensitive and that the source optimizer's accepted interior estimates do not identify a unique, well-conditioned kinetic target. The profile is computed from the deposited model's generated current, not from an experimental human trace. Values beyond 300 ms are explicitly counterfactual and must not be reported as source-model or biological parameters.

## High-resolution local profile around the minimum

A dedicated local profile uses the same −70-mV NEURON post-peak samples over tau1 = 320–360 ms, with 801 logarithmically spaced values. Grid spacing is 0.0471–0.0530 ms, and all 801 bounded linear least-squares solves succeeded.

The best sampled point is tau1 = 339.41125497 ms, R² = 0.999999577179, RMSE = 1.16767714×10⁻⁸ mA/cm². Its coefficients are a1 = 6.00828885×10⁻⁵, a2 = 2.60772361×10⁻⁵, and ss = 4.14437813×10⁻⁴ mA/cm². This refines the coarse extended-grid minimum at 338.2372 ms.

The band within 1% of the minimum RMSE spans 326 of 801 grid points, tau1 = 331.4605–347.7063 ms. Its R² values are 0.999999568739–0.999999577179. The much wider criterion of 10⁻⁶ below the best R² includes the entire local 320–360-ms window, so that threshold does not meaningfully narrow the local optimum. The dense grid shows that the high-fit-quality region is broad even at sub-millisecond sampling; it does not establish a statistical confidence interval.

## Amplitude and offset compensation along the profile

The profile coefficients show a strong exchange between the two exponential amplitudes while the offset changes very little. Among the 27 sampled points whose R² is within 10⁻⁶ of the profile maximum (tau1 = 270.323–361.762 ms):

- Fast amplitude a1 spans 2.74797×10⁻⁵ to 8.22542×10⁻⁵ mA/cm².
- Fixed-slow-component amplitude a2 spans 3.24249×10⁻⁶ to 6.07438×10⁻⁵ mA/cm².
- Steady offset ss spans 4.12425×10⁻⁴ to 4.15089×10⁻⁴ mA/cm², a total range of about 0.64% of its mean.
- Pearson correlation across those sampled profile points is −0.99995 for a1 versus a2, +0.98006 for a1 versus ss, and −0.98197 for a2 versus ss.

The initial 901-point extended grid represented its 1%-RMSE band with only four samples. The 801-point local profile resolves that band into 326 points from 331.4605 to 347.7063 ms. Within that band, a1 spans 5.42726×10⁻⁵–6.71468×10⁻⁵, a2 spans 1.87670×10⁻⁵–3.21239×10⁻⁵, and ss spans 4.14206×10⁻⁴–4.14679×10⁻⁴ mA/cm². Across the 326 profile points, Pearson r(a1,a2) = −0.99999896, r(a1,ss) = +0.99921558, and r(a2,ss) = −0.99927167. The offset span is about 0.114% of its mean. At the best local point (339.4113 ms), (a1, a2, ss) = (6.00829×10⁻⁵, 2.60772×10⁻⁵, 4.14438×10⁻⁴) mA/cm².

These are descriptive Pearson correlations along the deterministic profile grid, not parameter-estimation covariance, confidence intervals, or independent measurements. They show that materially different allocations between the fast and fixed-slow exponentials can preserve a nearly unchanged current offset and almost indistinguishable fit quality.

The exact source-literal nonlinear fit at −70 mV returned tau1 = 213.8193 ms, R² = 0.999994545, RMSE = 4.19431×10⁻⁸ mA/cm². On the same waveform, the fixed-tau profile at the source-domain upper end has RMSE 1.49170×10⁻⁸ mA/cm²; the extended profile minimum has RMSE 1.16791×10⁻⁸ mA/cm². These profile minima are approximately 2.81 and 3.59 times lower in RMSE, respectively. This indicates that the source nonlinear fit's accepted interior result is not the best sampled least-squares point on this waveform. The extended minimum remains outside the deposited 300-ms bound and is only a diagnostic counterfactual.

## Time-resolved residual waveform at the local-profile optimum

The residual export refits the three nonnegative linear coefficients at the best sampled local-profile value, tau1 = 339.41125497 ms, on the same 4,890 NEURON post-peak current samples. The retained source clock spans 30.9–519.8 ms; the source helper's shifted fit clock spans 0–488.9 ms in 0.1-ms increments. The refitted coefficients match the local profile: a1 = 6.00828885×10⁻⁵, a2 = 2.60772361×10⁻⁵, and ss = 4.14437813×10⁻⁴ mA/cm².

The reconstructed residual record reproduces the local-profile objective (R² = 0.999999577179; RMSE = 1.16767714×10⁻⁸ mA/cm²). The mean residual is approximately 1.65×10⁻¹⁹ mA/cm². Its largest absolute value occurs at the first post-peak sample: observed current 5.00295140×10⁻⁴ mA/cm² versus fitted 5.00597938×10⁻⁴ mA/cm², residual −3.02797528×10⁻⁷ mA/cm². The residual remains negative through 3.9 ms and first becomes positive at 4.0 ms.

This early transient dominates the integrated residual scale. Over the first 10 ms, residual RMSE is 7.80270×10⁻⁸ mA/cm². From 10 ms onward, it falls to 3.28972×10⁻⁹ mA/cm², about 23.7 times lower; after 50 ms it is 1.76161×10⁻⁹ mA/cm². The largest absolute residual after 10 ms is 1.45430×10⁻⁸ mA/cm² at 10.1 ms. Thus the most visible discrepancy is concentrated in the first few milliseconds after the activation-current peak, while the remaining 479 ms are fitted much more closely.

The residual series is strongly temporally correlated (lag-1 correlation 0.9284 across the full 0.1-ms series and 0.9979 after the first 10 ms). This is expected of a smooth deterministic model residual and is not evidence for measurement noise or an independently sampled error process. No stochastic error model, empirical confidence interval, or biological significance test is implied. The residual record is a model-equation diagnostic only.

## Reproducible records and verification

- Same-waveform results: `research/HUMAN-L23-WILBERS-K-IV-FIT-START-DIAGNOSTICS.csv`.
- Source-bound profile: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE.csv`.
- Extended-bound profile: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-EXTENDED.csv`.
- High-resolution local profile: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-LOCAL.csv`.
- Time-resolved local-profile residual waveform: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv`.
- Generator: `experiments/wilbers_k_iv_fit_diagnostics.py`, integrated into `experiments/replay_wilbers_k_iv_neuron.py`.
- Validators: `experiments/validate_wilbers_k_iv_fit_diagnostics.py`, `experiments/validate_wilbers_k_iv_fit_profile.py`, and `experiments/validate_wilbers_k_iv_fit_residuals.py`.
- Tests: `experiments/test_wilbers_k_iv_protocols.py`.
- CI workflow: `.github/workflows/repository-policy.yml`.

GitHub Actions [43462311680](https://github.com/codexclai/HumanJS/actions/runs/43462311680) passed on exact code HEAD `55d469485edb00a9d65c105645f58b9bb1a92a39`: rustfmt, Clippy, 41 Rust unit tests, 3 synapse integration tests, 6 passive-membrane integration tests, syntax for 21 Python experiment scripts, 37 Python tests, five original Wilbers Na/K NEURON source protocols and validators, all 192 K_IV fit-start runs, the 601-point source-bound profile, the 901-point extended profile, the 801-point high-resolution local profile, the 4,890-row residual export and validator, and repository policy. The first residual-test run exposed an overstrict synthetic assertion; the test was corrected to compare independently reconstructed residual RMSE with the profiled objective, and this complete rerun passed.


## Interpretation boundary and next step

This experiment establishes a numerical sensitivity and profile-boundary problem in the deposited model's current-fit helper. It does not establish a biological fast-inactivation time constant, resolve a human-versus-animal inference, or validate the HumanJS single-compartment spike model. The inspected 65-file Dataverse v3.0 inventory still contains no raw human K voltage-clamp NWB traces or individual K kinetic CSVs. No empirical current refit is possible from this release.

Next, preserve and inspect the residual waveform for the source-literal nonlinear fit and the 339.4113-ms local-profile solution to determine whether structured residuals remain. Do not change the deposited source helper or NMODL until that comparison is complete. Keep the raw-human-trace task open, keep the exploratory HumanJS spike model unaccepted, and do not contact authors or researchers.


## 2026-11-13 — non-source third-exponential correction of the early residual

### Question and data boundary

The earlier local-profile residual export showed that most two-exponential mismatch sits in the first few milliseconds after the post-peak fit origin. This experiment asks whether one extra short-time exponential can reduce that discrepancy without distorting the rest of the waveform. It uses only the existing NEURON 9.0.2 output from the deposited pure-human k_human.mod and Dataverse channel_tools.py at the −70-mV K_IV command. It is **not** a fit to raw human potassium recordings: the inspected DataverseNL v3.0 release still lacks the raw K voltage-clamp NWB traces and individual K kinetic CSVs.

Input is the 4,890-row HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-RESIDUALS.csv at 0.1-ms spacing, relative time 0–488.9 ms and original NEURON time 30.9–519.8 ms. The two-exponential baseline is

\[
I_2(t)=a_1e^{-t/\tau_1}+a_2e^{-t/450\ \mathrm{ms}}+s_s,
\]

with tau1=339.41125497 ms, the best sampled point of the 320–360-ms high-resolution local profile. This tau1 is already outside the deposited source helper's 0–300-ms bound; the experiment leaves the original source bound/helper unchanged and treats the local-profile value as a separate counterfactual reference. The fixed 450-ms term preserves the source helper's slow component.

### Counterfactual model and fitting method

The tested model adds one descriptive short-time term:

\[
I_3(t)=a_1e^{-t/\tau_1}+a_2e^{-t/450\ \mathrm{ms}}+a_3e^{-t/\tau_3}+s_s.
\]

The tau3 grid is linear from 0.6 to 2.0 ms with 801 points. At each grid point, all four coefficients are refit by bounded linear least squares **on all 4,890 samples**. The original two amplitudes and offset are constrained nonnegative; the added a3 is allowed to be signed. The selected point minimizes full-waveform residual sum of squares. Early (t<10 ms) and late (t>=10 ms) RMSE are held out as descriptive partitions of the same fit, not used as weights or as separate optimizers.

A control refit uses the same tau3 chosen by the signed full-waveform profile but imposes a3>=0. This is deliberately a narrow control at the selected optimum; it does not assert that every conceivable positive extra-component family has been exhausted.

### Results

| Quantity | Two-exponential baseline | Signed three-exponential correction |
|---|---:|---:|
| tau1 | 339.411255 ms | 339.411255 ms (fixed) |
| tau2 | 450 ms | 450 ms (fixed) |
| tau3 | — | approximately 1.2335 ms |
| a1 (mA/cm²) | 6.00829×10⁻⁵ | 6.03028×10⁻⁵ |
| a2 (mA/cm²) | 2.60772×10⁻⁵ | 2.58350×10⁻⁵ |
| a3 (mA/cm²) | 0 | approximately −3.1823×10⁻⁷ |
| Offset (mA/cm²) | 4.14437813×10⁻⁴ | 4.14469867×10⁻⁴ |
| Full-waveform RMSE (mA/cm²) | 1.16768×10⁻⁸ | 2.45019×10⁻⁹ |
| First-10-ms RMSE (mA/cm²) | 7.80270×10⁻⁸ | 4.65627×10⁻⁹ |
| After-10-ms RMSE (mA/cm²) | 3.28972×10⁻⁹ | 2.38177×10⁻⁹ |

The signed extension reduces full-waveform RMSE by about **79.0%**, first-10-ms RMSE by about **94.0%**, and after-10-ms RMSE by about **27.6%**. The original fitted a1 increases about 0.37%, a2 decreases about 0.93%, and the offset increases about 0.0077%. The added term's magnitude is only about **0.064% of the observed peak current**.

At the signed optimum, the nonnegative-a3 control drives a3 to zero within numerical tolerance and recovers the two-component baseline objective. The improvement therefore depends on a small **negative** fast correction. It is not evidence for a new positive current component, microscopic inactivation gate, or biological tau3. It simply captures a small oppositely signed part of this deterministic model's residual waveform. No channel parameter, source helper, source caller, NMODL source, HumanJS runtime equation, or Rust mechanism was changed.

### Reproduction and limitations

The reproducible implementation is experiments/wilbers_k_iv_three_component.py; experiments/validate_wilbers_k_iv_three_component.py reloads the source residual and local-profile CSVs, recomputes the 801-point full-waveform profile, and checks source identity, time alignment, interior optimum, coefficient sign/magnitude, objective reductions, limited movement of the original terms, and the nonnegative control. Three synthetic tests cover recovery of a signed transient, the nonnegative control, and invalid-input rejection. The validator is part of .github/workflows/repository-policy.yml.

Workflow [43466274672](https://github.com/codexclai/HumanJS/actions/runs/43466274672) passed on exact pushed experiment commit 46586e97695eae9b756e3d007b4daeb4069ae683. This is a reproducible software/numerical analysis of model-generated current, not raw-trace reproduction, biological validation, or evidence that the added exponent corresponds to a human potassium channel process. See also ADR-018.


## 2026-11-13 — signed short-time residual correction across adjacent K_IV voltages

### Question and source data

The earlier -70-mV K_IV residual study found that an additional short-time exponential with a small negative coefficient substantially reduced the deterministic first few milliseconds of fit residual. This extension asks whether the same signed correction appears at adjacent source command voltages, rather than relying on the single -70-mV waveform.

The three waveforms are taken from the original deposited pure-human k_human.mod and DataverseNL v3.0 channel_tools.py, executed by the unchanged source replay using NEURON 9.0.2 and built-in VClamp at 34°C and 0.1-ms sampling. Commands are -75, -70 and -65 mV. The runner captures exactly the post-peak slice passed to the source fast-inactivation helper (activation_times[peak_index:-1]), not a reconstructed or interpolated waveform. Both the source NEURON simulation clock and the shifted fit clock are retained. The checked-in summary contains these fit outcomes and provenance; the complete sampled current waveforms are ephemeral CI inputs and are not duplicated as another large research CSV.

### Fitting protocol

For each command voltage separately:
1. Use the exact post-peak source-model current samples and time-shift them to the first sample, as the source helper does.
2. Profile the two-exponential long-tau objective over 0.05-1200 ms using 901 logarithmic points; refine over a 6% multiplicative neighbourhood using 801 points. Keep tau2=450 ms fixed as in the deposited helper.
3. At the selected local tau1, profile the non-source short tau3 over 0.6-2.0 ms using 801 equally spaced points.
4. At every tau3, refit all four coefficients on the **full waveform**. Constrain the two original amplitudes and offset to be nonnegative; allow the short extra coefficient a3 to be signed. Select the point minimizing the full-waveform residual sum of squares.
5. At that selected tau3, repeat the fit with a3>=0 as a sign control. Report full, first-10-ms and after-10-ms RMSE partitions, plus movement of the original coefficients. The time partitions are diagnostics, not separate weighted fits.

This is explicitly a non-source fit diagnostic. The local long-tau1 profile is outside the deposited 0-300-ms source bound at -75 and -70 mV; those estimates are not source parameters. The 450-ms slow component is fixed across all three voltages.

### Results

| Quantity | -75 mV | -70 mV | -65 mV |
|---|---:|---:|---:|
| Samples | 4,896 | 4,890 | 4,883 |
| Source-clock start (ms) | 30.3 | 30.9 | 31.6 |
| Local tau1 (ms) | 393.4039 | 339.4072 | 291.4180 |
| Short tau3 (ms) | 1.111 | 1.2335 | 1.384 |
| Signed a3 (mA/cm²) | -1.00654e-7 | -3.18235e-7 | -9.95616e-7 |
| Absolute a3 as % of peak current | 0.0391% | 0.0636% | 0.1060% |
| Full-waveform RMSE reduction | 80.386% | 79.023% | 77.371% |
| First-10-ms RMSE reduction | 94.278% | 94.034% | 93.789% |
| After-10-ms RMSE reduction | 27.728% | 27.614% | 27.433% |

The short tau3 increases smoothly over these three commands, and the negative extra amplitude grows in absolute value with depolarization while remaining below 0.11% of peak current. The correction improves the full 488-ms waveform, not just the initial 10 ms. The original fast and fixed-slow amplitudes move by less than 5% across these independent refits (per-voltage shifts are preserved in the summary CSV); the steady offset moves by less than 0.014%.

At each voltage, the nonnegative-a3 control collapses the additional coefficient to zero at the signed optimum. The improvement therefore depends on a small **negative** correction term. This is not an extra positive potassium current or a newly identified molecular gate. It describes the direction and timescale of residual compensation required by this particular two-exponential current-fit family when applied to these deterministic source-model waveforms.

### Reproducibility and limitations

The compact, provenance-bearing result table is research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv. The exporter is integrated into experiments/replay_wilbers_k_iv_neuron.py; profiling is implemented in experiments/wilbers_k_iv_multivoltage.py; analysis CLI, synthetic/input-contract tests and expected-output validator are in experiments/analyze_wilbers_k_iv_multivoltage.py, experiments/test_wilbers_k_iv_multivoltage.py, and experiments/validate_wilbers_k_iv_multivoltage.py. The main workflow exports the exact source post-peak records to a temporary file, replays the analysis, and compares every output field to the committed result table with a narrow numerical tolerance. The expected summary includes no raw experimental current data.

Workflow [43469283136](https://github.com/codexclai/HumanJS/actions/runs/43469283136) passed on exact pushed main commit 5d5e180bc5068f647edc040de39481801be52a0e: rustfmt, Clippy, 41 Rust unit tests, 3 synapse integration tests, 6 passive membrane integration tests, 28 Python experiment scripts parsed, 43 Python tests, all Wilbers source-model replays and validators, the three-voltage residual profile, committed-summary comparison and repository policy.

Two intermediate workflow failures exposed test-fixture/roundoff details and were corrected transparently. The clock test originally applied a uniform clock offset, which is valid because the source clock is separately retained; it now perturbs one interior timestamp and tests real sample misalignment. The positive-amplitude control mathematically reproduces the baseline but its independently solved floating-point residual produced a sub-1e-8% apparent improvement; code and checked-in summary now normalize that negligible numerical residue to zero. No source fit bound, source R2 gate, channel parameter, biological criterion, or mechanism was weakened.

**Interpretation boundary:** this establishes repeatability of a small negative residual correction across three adjacent model-generated command waveforms only. Three voltages do not establish a general voltage law, microscopic gating process or biological time constant. The inspected DataverseNL v3.0 release still lacks raw human K voltage-clamp NWB recordings and individual K kinetic targets; no empirical current refit is possible. The deposited original helper/caller and NMODL remain untouched. ADR-014 remains open and the HumanJS single-compartment spike-capable model remains exploratory and biologically unvalidated.


## 2026-11-14 — signed K_IV residual profile across all finite source-fit voltages

### Predeclared source selection

The three-voltage result is now extended to every K_IV command at which the original deposited source fit was attempted and returned a finite positive fast-inactivation time constant. The command protocol still contains 34 voltages from -110 to +55 mV in 5-mV increments. The original source current-selection threshold (>1e-8 mA/cm²) is passed at 32 commands (-100 through +55 mV). Five of those attempted fits (-100, -95, -90, -85 and -80 mV) return non-finite fast time constants and are excluded from the residual fit. The remaining 27 commands (-75 through +55 mV) have finite positive source fast-fit values and are all included. The two commands -110 and -105 mV do not pass the source threshold and are separately recorded as not attempted. The runner now asserts these three disjoint source-selection outcomes, and exports post-peak data only for the 27 finite-positive commands.

The exact post-peak slices remain the vectors passed to the original helper (activation\_times[peak\_index:-1]); the runner retains both the shifted fit clock and the original NEURON clock. The samples are generated by the unmodified deposited pure-human k\_human.mod and channel\_tools.py under NEURON 9.0.2/VClamp at 34°C and 0.1-ms sampling. They are model outputs, not raw human experimental current recordings.

### Fitting protocol

Each of the 27 voltage waveforms is analyzed independently. The two-exponential long component is profiled over 0.05–1200 ms (901 logarithmic points), then locally refined over a 6% multiplicative interval (801 points), retaining the source fixed tau2=450 ms. At the selected local tau1, a non-source tau3 is profiled over 0.6–2.0 ms (801 equally spaced points). At each tau3, all coefficients are fitted to the full waveform; the two source-form amplitudes and steady offset are nonnegative, while the added a3 is signed. A second fit at the selected tau3 constrains a3 to be nonnegative. The first-10-ms and after-10-ms errors are diagnostics of the same full-waveform fit, not separate fitting objectives.

### Results

All 27 commands select a negative a3. At the selected signed optimum, the nonnegative-a3 control sets its added amplitude to zero and gives zero full-waveform improvement at all 27 voltages. The full-waveform RMSE reduction ranges from 55.467% to 80.386% (median 66.126%); first-10-ms RMSE reduction ranges from 75.608% to 94.278% (median 84.935%). The added term's absolute amplitude ranges from 0.0391% to 2.0965% of peak current.

The result is not a uniformly improving late-window correction. After-10-ms RMSE improves by 20.814% at the median, with a range from a 27.728% reduction to a 41.467% increase. The after-10-ms metric becomes worse at seven commands (+25 through +55 mV), even though the full-waveform objective improves at every command. This reflects the full-waveform optimization's weighting of the much larger early transient; the late window is not optimized independently.

The fitted tau3 ranges from 0.6 to 2.0 ms (median 1.384 ms), but 11/27 profiles land exactly on a tau3 grid boundary: the upper 2.0-ms boundary at -50 through -15 mV and the lower 0.6-ms boundary at +45, +50 and +55 mV. These are boundary-limited profile outcomes, not interior tau estimates. Tau3 does not form a globally monotonic voltage trend. The local tau1 profile ranges from 17.195 to 393.404 ms; only -75 and -70 mV lie above the original helper's 300-ms upper bound. No coarse or local long-tau profile selected a boundary in its declared grid.

### Interpretation and limitations

This broader sweep strengthens one limited conclusion: within this exact model-generated data set and this specific fit family, a small negative short-time correction is selected at every finite-positive source-fit command. It does **not** establish a biological current component, a microscopic gate, a voltage-dependent channel kinetic law, or a human experimental result. The non-source tau3 grid has boundary hits at 11 commands, and the late residual becomes worse at seven depolarized commands. Neither the signed coefficient nor tau3 should be transferred into Rust channel parameters. The deposited source helper, caller, NMODL and HumanJS runtime parameters remain unchanged.

The complete per-voltage result and provenance are in `research/HUMAN-L23-WILBERS-K-IV-MULTIVOLTAGE-RESIDUAL-SUMMARY.csv`. The exporter, analysis, tests and strict expected-output validator are in `experiments/replay_wilbers_k_iv_neuron.py`, `experiments/wilbers_k_iv_multivoltage.py`, `experiments/analyze_wilbers_k_iv_multivoltage.py`, `experiments/test_wilbers_k_iv_multivoltage.py` and `experiments/validate_wilbers_k_iv_multivoltage.py`. GitHub Actions [43487894255](https://github.com/codexclai/HumanJS/actions/runs/43487894255) passed on exact code HEAD `2368066b9602c846e527211d7d5d80ef0c6008c6`, including Rust formatting/Clippy/tests, Python tests, all original Wilbers source replays and validators, the expanded 27-voltage analysis and structural validation, and repository policy. The committed-reference comparison is restored with this update and runs in CI.


## 2026-11-14 — expanded K_IV short-time profile: 0.1–5.0 ms

### Question and method

The preceding 0.6–2.0-ms tau3 search selected a boundary value at 11/27 commands. This follow-up widens the predeclared profile interval while retaining the same source command eligibility, exact post-peak waveforms, long-tau1 profile, full-waveform fitting objective, and nonnegative-amplitude sign control.

All 27 profile inputs remain the finite-positive fast-inactivation fits selected by the unchanged source routine: 34 commands were executed; the source current-selection threshold passed at 32 (-100 through +55 mV); five attempted fits (-100, -95, -90, -85 and -80 mV) returned non-finite fast taus; and the remaining 27 commands (-75 through +55 mV) returned finite positive values. The two threshold exclusions (-110 and -105 mV) and five non-finite attempts remain disjoint, explicitly recorded exclusions.

For each of the same 27 exact NEURON/VClamp post-peak current waveforms, the long component was profiled as before (901 logarithmic tau1 points from 0.05 to 1200 ms, then an 801-point local 6% refinement), with the source slow time constant fixed at 450 ms. The non-source tau3 search was widened to 0.1–5.0 ms using 2,801 equally spaced points (approximately 0.00175-ms spacing, matching the previous 0.6–2.0-ms/801-point grid resolution). At each tau3 point, all coefficients were fit against the complete waveform; the added amplitude remained signed, and a separate nonnegative-amplitude control was evaluated at the selected signed optimum. The first-10-ms and after-10-ms RMSE values remain diagnostics, not separate fitting objectives.

### Results

All 27 selected tau3 values are now strictly interior to the expanded 0.1–5.0-ms grid: there are **zero tau3 boundary hits**, compared with 11/27 hits on the narrower 0.6–2.0-ms search. The fitted tau3 values span 0.49725–2.9805 ms (median 1.38275 ms) and are **not globally monotonic** with voltage; the largest selected value is 2.9805 ms at -30 mV.

The signed added amplitude remains negative at all 27 commands, and the nonnegative-amplitude control still collapses to zero at all 27 selected optima. Full-waveform RMSE reduction is 59.945–80.386% (median 66.126%); first-10-ms RMSE reduction is 82.625–94.280% (median 89.018%). After-10-ms RMSE reduction ranges from -35.719% to +27.726% (median +20.817%): the late-window error still worsens at +25 through +55 mV (seven commands), even though the full-waveform fit improves at all 27 commands. The absolute added-amplitude magnitude is 0.0391–1.8791% of peak current (median 1.5976%).

The complete result table is `research/HUMAN-L23-WILBERS-K-IV-TAU3-EXTENDED-RESIDUAL-SUMMARY.csv` (27 voltage rows, 42 columns). It preserves the selected tau3, coefficient estimates, full/early/late residual partitions, control results, and explicit search bounds/boundary flags. The main workflow regenerates the output from the temporary NEURON waveform export and compares every field with the committed reference using the validator's declared numerical tolerances.

### Interpretation and limitations

The expanded interval removes the earlier grid-boundary ambiguity for this particular discrete search, but it does not establish a biological time constant or a voltage-dependent kinetic law. The selected tau3 profile remains non-source and non-monotonic; the fit's full-waveform objective can trade late-window accuracy for a lower total residual, as reflected by the seven depolarized commands whose after-10-ms error increases. These currents are generated by the deposited pure-human model under NEURON 9.0.2/VClamp, not raw human experimental recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. Do not transfer tau3 or the signed term into Rust channel parameters or gate equations; the deposited helper, caller, NMODL and HumanJS runtime parameters remain unchanged. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

This resolves only the *grid-boundary* question for the chosen non-source fit family; it does not resolve parameter identifiability, objective-family sensitivity, or biological validity. The same-waveform numerical fit does not constitute experimental human K-current reproduction.

GitHub Actions [43492075297](https://github.com/codexclai/HumanJS/actions/runs/43492075297) passed on exact code/data HEAD `8f4dc55bb0af0580b63e0bdac1c375b1d1df2e38` with all 32 workflow steps successful: rustfmt, Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 28 Python experiment scripts parsed, 46 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, the 27-command 0.6–2.0-ms reference comparison, the new 27-command 0.1–5.0-ms profile and strict comparison with its committed 42-column CSV, the existing three-exponential residual validator, and repository policy.


## 2026-11-14 — local K_IV tau3 full-waveform objective-shape audit

### Method

The summary is derived from the same 27 exact post-peak NEURON 9.0.2/VClamp model-current waveforms and the same extended 0.1–5.0-ms tau3 grid (2,801 equally spaced points). At each grid point, all four coefficients are refit against the **full-waveform RSS** while tau1 is fixed at that command's independently profiled local optimum and source tau2 remains 450 ms. For each command, the report records the normalized central second difference of relative RSS at the selected grid minimum, the immediately adjacent left/right relative RSS increases, and the contiguous grid basin around the minimum whose relative RSS increase is no more than 1%, 5%, or 10%.

For each threshold, only the contiguous grid basin containing the selected minimum is retained; disconnected grid points that independently fall below the same objective threshold are not merged. The curvature is the central second finite difference of `RSS/RSS_min - 1`, divided by the squared grid step. The left/right adjacent deltas are likewise expressed as percentage increases in full-waveform RSS over the selected minimum.

### Results

All 27 selected minima are interior, and **none of the 1%, 5%, or 10% near-minimum basins touches either edge** of the 0.1–5.0-ms grid. The normalized local curvature spans 0.382621–17.942831 ms⁻² (median 3.541781 ms⁻²). The contiguous 1%-RSS-increase basin spans 0.06475–0.45500 ms (median 0.14875 ms); the 5% basin spans 0.14875–1.02550 ms (median 0.33425 ms); and the 10% basin spans 0.21175–1.46125 ms (median 0.47600 ms).

The broadest profile occurs at -30 mV: normalized curvature 0.382621 ms⁻², with 1%, 5%, and 10% basin spans of 0.45500, 1.02550, and 1.46125 ms. The narrowest occurs at +55 mV: curvature 17.942831 ms⁻², with corresponding spans of 0.06475, 0.14875, and 0.21175 ms. Thus, although the expanded grid removed the previous boundary clipping, the local objective width is voltage-dependent and some selected minima are appreciably flatter than others.

The broadest and narrowest examples are not interchangeable: -30 mV has the broadest near-minimum basin and lowest local curvature, while +55 mV has the narrowest basin and highest curvature. This variation cautions against presenting a single common precision for the fitted tau3 values.

### Interpretation and limitations

These are **descriptive grid-basin spans of a deterministic model-output objective**, not statistical confidence intervals, measurement uncertainty, or biological uncertainty estimates. No noise model was fitted. The widths are conditional on tau1 being held at its selected per-voltage local optimum; they do not account for coupling to tau1 or uncertainty in the source fit. The waveforms are generated by the deposited pure-human K mechanism under NEURON 9.0.2/VClamp, not raw human experimental K-current recordings. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. The deposited fitting helper, caller, pure-human NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or the signed residual correction into Rust channel kinetics. ADR-014 remains open, and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The complete reproducible output is `research/HUMAN-L23-WILBERS-K-IV-TAU3-PROFILE-SHAPE.csv`. The analyzer computes its rows from the same 2,801-point profile used for the extended-grid result, and CI compares all 26 fields across all 27 voltages against the committed reference. GitHub Actions [43495085251](https://github.com/codexclai/HumanJS/actions/runs/43495085251) passed on exact code/data HEAD `dfac63b6c99c6c77981a390e4b3da25affd45dfe` with all 33 workflow steps successful: Rust formatting/Clippy/tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), 29 Python experiment scripts parsed, 47 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and expanded 27-row K_IV residual summaries, strict comparison of the 27-row/26-column tau3 objective-shape reference, the three-exponential residual validator, and repository policy.

This completes the planned *conditional* profile-shape review. It does not account for coupling to tau1; that remains an explicit next numerical sensitivity check. It is not evidence for human experimental K kinetics.


## 2026-11-14 — conditional K_IV tau1–tau3 objective surface

### Method

The predeclared subset is -30, -60, and +55 mV, representing the broadest, median, and narrowest single-tau1 1% objective basins in the preceding profile-shape audit. At each command, nine tau1 values span the existing local 6% refinement interval around the already selected local tau1; the middle node is that reference tau1. At every tau1 node, tau3 is profiled over 0.1–10.0 ms on 5,601 equally spaced points. All coefficients are refit at each tau3 against the **full waveform RSS**, with the original two current amplitudes and steady offset constrained nonnegative, the added third amplitude signed, and source tau2 fixed at 450 ms. First-10-ms and after-10-ms RMSE remain diagnostics of the same full-waveform fit, not separate objectives. The result is a conditional tau1–tau3 sensitivity surface on three waveforms, not a global fit across all 27 voltages.

The surface CSV, `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-SURFACE-SUMMARY.csv`, contains 27 conditional slices (nine tau1 nodes for each of three predeclared voltages) and 44 columns. It retains each slice's selected tau3, full/early/late fit errors, signed and constrained coefficients, normalized local curvature, contiguous 1%/5%/10% RSS basins, edge flags, and relative RSS to the best tau1 slice at that command. The earlier single-tau1 tau3 estimate is retained separately as `reference_tau3_ms`; it is not forced to equal the new selected tau3 when the expanded surface interval changes the conditional optimum.

### Results

| Command | Existing local tau1 (ms) | Existing single-tau1 tau3 (ms) | Tau1 local window (ms) | Conditional tau3 minima over the window (ms) | Best sampled surface tau1 / tau3 (ms) | Full-RSS reduction vs center tau1 slice |
|---:|---:|---:|---:|---:|---:|---:|
| -30 mV | 112.958 | 2.9805 | 106.021–119.556 | 2.057–5.092 | 107.755 / 4.339 | 96.276% |
| -60 mV | 251.949 | 1.56825 | 237.580–267.909 | 1.224–2.140 | 244.764 / 1.802 | 96.955% |
| +55 mV | 17.195 | 0.49725 | 16.134–18.194 | 0.498–10.000 | 17.195 / 0.498 | 0% |

At -30 and -60 mV all nine conditional tau3 minima are interior to the 0.1–10-ms grid. Allowing tau1 to move within its existing local interval materially shifts the sampled full-RSS minimum: the -30-mV minimum is at tau1 107.755 ms/tau3 4.339 ms, while the -60-mV minimum is at 244.764 ms/1.802 ms. Relative to the center tau1 slice, their full-waveform RSS falls by 96.276% and 96.955%, respectively. These are reductions in the objective RSS, not RMSE percentages.

The +55-mV surface behaves differently. Six of its nine tau1 slices select tau3 at the expanded 10-ms upper boundary. Its best sampled surface point remains at the center tau1 (17.195 ms) and tau3 0.49777 ms, so the global full-RSS objective does not improve relative to that center slice. The signed extra amplitude is negative at tau1 indices 0–4 but positive at indices 5–8. Thus, the sign and fitted short component are sensitive to the allowed tau1 change at this depolarized command, and the 10-ms upper limit still fails to localize several conditional minima.

At the center tau1 node, the contiguous 1%/5%/10% objective-basin spans are 0.4561/1.0254/1.4620 ms at -30 mV, 0.1485/0.3359/0.4756 ms at -60 mV, and 0.06541/0.14673/0.21037 ms at +55 mV. These widths are conditional slices through a discrete, deterministic objective surface; they are not statistical uncertainty intervals.

### Interpretation and limitations

This surface demonstrates that the previously reported tau3 curvature and basin width conditional on fixed tau1 do not capture all tau1–tau3 coupling. The strong objective reductions at -30 and -60 mV arise from shifting tau1 inside the existing 6% local window while refitting the signed short component. At +55 mV, both the tau3 boundary and a sign reversal in the added coefficient show that the correction is not stable under tau1 variation. The 0.1–10-ms range therefore does not resolve all +55-mV conditional profiles.

All inputs are deterministic NEURON 9.0.2/VClamp outputs from the deposited pure-human K model, not raw human experimental K-current recordings. Raw human K voltage-clamp NWB traces and individual kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. No noise model was fitted; do not interpret the basin widths as confidence intervals, measurement uncertainty, biological uncertainty, or human channel kinetics. The deposited helper/caller/NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or the signed correction into Rust. ADR-014 remains open and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The surface is deliberately limited to the three predeclared representative voltages; it does not imply the same tau1–tau3 coupling at the other 24 commands. Its purpose is to show that fixed-tau1 objective-shape summaries are conditional, and that the added residual term's parameters can move substantially when tau1 is allowed to vary. GitHub Actions [43500401868](https://github.com/codexclai/HumanJS/actions/runs/43500401868) passed on exact code/data HEAD `5e41b681bcb6307921f466c90b4fbe680d1f2681` with all 34 workflow steps successful. Hosted verification included Rust formatting/Clippy and tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), syntax parsing of 30 Python experiment scripts, 48 Python tests, original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and extended 27-row K_IV profiles, the 27-row/26-column fixed-tau1 objective-shape reference, the new 27-row/44-column tau1–tau3 surface reference, the three-exponential residual validator, and repository policy (16 required files).


## 2026-11-14 — +55 mV conditional tau1–tau3 surface extended to 40 ms

### Question and method

The preceding +55 mV tau1–tau3 surface showed six of nine tau1 slices with tau3 minima pinned at 10 ms. Its signed added coefficient was positive at four of those high-tau1 nodes. The bounded follow-up asks whether those minima and positive coefficients persist once the short time-constant grid is allowed to extend farther, without changing the waveform, tau1 nodes, fitting objective, or coefficient sign constraints.

The previous +55 mV conditional surface used nine fixed tau1 nodes in the already defined local 6% refinement interval and a 0.1–10.0 ms tau3 grid. Six of nine conditional minima were pinned at the 10 ms upper limit, and the added signed coefficient was positive at four of those high-tau1 nodes. To test whether that behavior persisted away from the limit, the same nine tau1 nodes and exact source waveform were reprofiled over 0.1–40.0 ms on 11,401 equally spaced tau3 points (0.0035 ms spacing). At every tau3 point all four coefficients were refit against full-waveform RSS; source tau2 remained fixed at 450 ms; a1, a2 and the steady offset remained nonnegative while a3 remained signed. First-10-ms and after-10-ms RMSE were retained as diagnostics, not alternative objectives.

### Results

All **nine of nine selected tau3 minima are now interior** to the expanded 0.1–40 ms grid, ranging from 0.4955 to 28.6495 ms. Compared with the 0.1–10 ms surface, the six upper-bound minima disappear. More importantly, the signed added coefficient is now negative at all nine tau1 nodes. The four positive coefficients previously found at tau1 indices 5–8 do not persist when tau3 can move beyond 10 ms. That makes the earlier sign reversal consistent with a truncated conditional fit, not a stable feature of this surface.

| Tau1 grid index | Tau1 (ms) | Selected tau3 (ms) | Signed a3 (mA/cm²) |
|---:|---:|---:|---:|
| 0 | 16.134424 | 13.4280 | -0.0965012 |
| 1 | 16.399624 | 11.9685 | -0.0440700 |
| 2 | 16.664824 | 8.4615 | -0.0162458 |
| 3 | 16.930024 | 0.9540 | -0.0103225 |
| 4 | 17.195223 | 0.4955 | -0.0093360 |
| 5 | 17.444952 | 28.6495 | -0.0070376 |
| 6 | 17.694681 | 23.5780 | -0.0239165 |
| 7 | 17.944409 | 21.6355 | -0.0551058 |
| 8 | 18.194138 | 20.6030 | -0.1105878 |

The lowest full-waveform RSS remains at the middle tau1 node (17.195223 ms), with tau3=0.4955 ms; the global surface minimum is therefore still the centre-tau1 fit. The tau3 minima nevertheless move substantially across the allowed tau1 window, spanning approximately 0.50–28.65 ms. This is strong tau1–tau3 coupling in the selected numerical fit family, not an identified biological kinetic process.

The *selected minima* are no longer at the tau3 search boundary, but one local basin remains incompletely enclosed: at tau1 index 5 (17.444952 ms), its 1% basin is interior ([23.9805, 34.5365] ms), while the 5% basin reaches 40 ms ([19.3605, 40] ms; 20.6395 ms span) and the 10% basin also reaches 40 ms ([17.446, 40] ms; 22.554 ms span). The other eight tau1 slices have 1%, 5%, and 10% basin edge flags clear. Thus the point estimate is interior at every node, but the broader 5% and 10% neighbourhood at index 5 is still truncated by the current 40 ms ceiling.

The complete reference is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-55MV-40MS-SUMMARY.csv` (9 rows, 44 columns). It preserves the selected tau3 and coefficients, full/early/late RMSE diagnostics, relative full-RSS values, conditional basin bounds/spans/point counts and boundary flags. The workflow regenerates this surface from the same original NEURON 9.0.2/VClamp replay and compares all 44 fields against the committed reference.

### Interpretation and limitations

This is a descriptive sensitivity calculation on deterministic model-generated current, not raw human experimental K-current data, a statistical confidence region, measurement uncertainty, or biological uncertainty. The source fitting helper, source caller, pure-human NMODL, HumanJS Rust equations and channel parameters remain unchanged. Raw human K voltage-clamp NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory. Do not transfer tau3 or the signed correction into Rust channel kinetics. ADR-014 remains open and the single-compartment spike-capable model remains exploratory and biologically unvalidated.

The strict reference is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-55MV-40MS-SUMMARY.csv` (9 rows, 44 columns). The source replay regenerates the result and CI compares every numeric, Boolean, and integer field with the committed reference using the declared tolerances. GitHub Actions [43552164142](https://github.com/codexclai/HumanJS/actions/runs/43552164142) passed on exact code/data HEAD `cdba13783f435645fb5f194a0e2bd2d5858ce1ab` with all 35 job steps successful and no failed steps. Hosted checks included Rust formatting and Clippy, Rust tests (41 core unit, 3 synapse integration, 6 passive-membrane integration), syntax parsing of 30 Python experiment scripts, 48 Python tests, the original Wilbers NEURON 9.0.2 Na/K protocol replays and validators, strict comparisons of the baseline and expanded 27-row K_IV residual summaries, the 27-row/26-column fixed-tau1 objective-shape reference, the 27-row/44-column three-voltage tau1–tau3 surface, the new 9-row/44-column +55 mV 0.1–40 ms surface, the three-exponential residual validator, and repository policy (16 required files).

This resolves the 10 ms *point-minimum* clipping at this representative voltage, and shows that the earlier positive signed coefficients do not persist under the wider domain. It does not close the broader near-minimum basin at tau1 index 5, identify a biological kinetic component, or replace missing experimental data.


## 2026-11-14 — +55 mV fixed-tau1 objective basin extended to 120 ms

### Question and method

The preceding nine-node +55 mV tau1–tau3 surface extended tau3 only to 40 ms. At tau1 index 5 (tau1=17.44495210313133 ms), the selected minimum was interior at 28.6495 ms, but the 5% and 10% near-minimum basins reached the 40 ms upper edge. This follow-up isolates that exact node: tau1 remains fixed at 17.44495210313133 ms, source tau2 remains fixed at 450 ms, and tau3 is profiled from 0.1 to 120 ms on 34,258 equally spaced points (0.0035000146 ms spacing). The same exact source-replay waveform is used. At every tau3 point, all four coefficients are refit against full-waveform RSS; a1, a2, and the steady offset are constrained nonnegative, while the additional a3 remains signed. The nonnegative-amplitude control is refit at the selected signed optimum. First-10-ms and after-10-ms RMSE are diagnostic windows only; neither defines a separate fitting objective.

### Results

The selected tau3 is 28.649619055959366 ms and is interior to the expanded grid. The contiguous relative-full-RSS basins are:

| Relative RSS threshold | Lower bound (ms) | Upper bound (ms) | Span (ms) | Grid points | Touches grid edge |
|---:|---:|---:|---:|---:|---:|
| 1% | 23.980600 | 34.536644 | 10.556044 | 3,017 | No |
| 5% | 19.360580 | 44.459185 | 25.098605 | 7,172 | No |
| 10% | 17.446072 | 55.148230 | 37.702157 | 10,773 | No |

The 5% basin therefore continues 4.4592 ms beyond the former 40 ms ceiling and the 10% basin continues 15.1482 ms beyond it; both are now fully enclosed. The 1% basin remains essentially the same as the previous 40 ms result. The normalized central second difference of relative RSS is 0.00073845005 ms⁻²; the immediate neighbouring increases are extremely small on this broad profile (left 5.89893×10⁻⁸%, right 8.45620×10⁻⁷%).

At the signed optimum, a1=0.2605146500, a2=0.2016783568, a3=-0.00703754981, and the steady offset is 0.08970440010 mA/cm². The positive control sets a3=0 and has full-waveform RSS 0.0004568998835 mA²/cm⁴, compared with 0.0002418441098 mA²/cm⁴ for the signed fit (88.9233% higher). The full-waveform RMSE is 0.0002206362989 mA/cm². These quantify the chosen non-source signed-exponential fit family only; a signed residual correction is not an identified positive current or a biological state.

The complete one-row/39-column reference is `research/HUMAN-L23-WILBERS-K-IV-TAU1-TAU3-55MV-INDEX5-120MS-SUMMARY.csv`. The main workflow regenerates the exact NEURON 9.0.2/VClamp waveform and compares every numeric, integer, and Boolean field with the committed reference.

### Interpretation and limitations

The 120 ms domain encloses all three descriptive objective basins at this fixed tau1 node; it does not establish global identifiability, tau1–tau3 joint uncertainty, or a probability interval. The source data are deterministic output from the deposited pure-human K mechanism, not raw human experimental voltage-clamp currents. No measurement-noise model was fitted. The basin spans are not confidence intervals, biological uncertainty, or human K channel kinetics. The deposited fitting helper, caller, pure-human NMODL, HumanJS Rust equations, and channel parameters remain unchanged. Do not transfer tau3 or a3 into Rust. Raw human K NWB traces and individual K kinetic target CSVs remain absent from the inspected DataverseNL v3.0 inventory; ADR-014 remains open and the exploratory spike-capable single-compartment model remains biologically unvalidated.
