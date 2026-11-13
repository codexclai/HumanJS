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
