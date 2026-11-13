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

## Amplitude and offset compensation along the profile

The profile coefficients show a strong exchange between the two exponential amplitudes while the offset changes very little. Among the 27 sampled points whose R² is within 10⁻⁶ of the profile maximum (tau1 = 270.323–361.762 ms):

- Fast amplitude a1 spans 2.74797×10⁻⁵ to 8.22542×10⁻⁵ mA/cm².
- Fixed-slow-component amplitude a2 spans 3.24249×10⁻⁶ to 6.07438×10⁻⁵ mA/cm².
- Steady offset ss spans 4.12425×10⁻⁴ to 4.15089×10⁻⁴ mA/cm², a total range of about 0.64% of its mean.
- Pearson correlation across those sampled profile points is −0.99995 for a1 versus a2, +0.98006 for a1 versus ss, and −0.98197 for a2 versus ss.

The tighter four-point band within 1% of the minimum RMSE (tau1 = 334.468–345.904 ms) still has an a1/a2 correlation of −0.9999993 across the sampled points: a1 spans 5.63725×10⁻⁵–6.55126×10⁻⁵, a2 spans 2.04546×10⁻⁵–2.99346×10⁻⁵, while ss spans only 4.14294×10⁻⁴–4.14627×10⁻⁴ mA/cm². At the best sampled point (338.2372 ms), (a1, a2, ss) = (5.91708×10⁻⁵, 2.70242×10⁻⁵, 4.14404×10⁻⁴) mA/cm².

These are descriptive Pearson correlations along the deterministic profile grid, not parameter-estimation covariance, confidence intervals, or independent measurements. They show that materially different allocations between the fast and fixed-slow exponentials can preserve a nearly unchanged current offset and almost indistinguishable fit quality.

The exact source-literal nonlinear fit at −70 mV returned tau1 = 213.8193 ms, R² = 0.999994545, RMSE = 4.19431×10⁻⁸ mA/cm². On the same waveform, the fixed-tau profile at the source-domain upper end has RMSE 1.49170×10⁻⁸ mA/cm²; the extended profile minimum has RMSE 1.16791×10⁻⁸ mA/cm². These profile minima are approximately 2.81 and 3.59 times lower in RMSE, respectively. This indicates that the source nonlinear fit's accepted interior result is not the best sampled least-squares point on this waveform. The extended minimum remains outside the deposited 300-ms bound and is only a diagnostic counterfactual.

## Reproducible records and verification

- Same-waveform results: `research/HUMAN-L23-WILBERS-K-IV-FIT-START-DIAGNOSTICS.csv`.
- Source-bound profile: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE.csv`.
- Extended-bound profile: `research/HUMAN-L23-WILBERS-K-IV-FIT-PROFILE-EXTENDED.csv`.
- Generator: `experiments/wilbers_k_iv_fit_diagnostics.py`, integrated into `experiments/replay_wilbers_k_iv_neuron.py`.
- Validators: `experiments/validate_wilbers_k_iv_fit_diagnostics.py` and `experiments/validate_wilbers_k_iv_fit_profile.py`.
- Tests: `experiments/test_wilbers_k_iv_protocols.py`.
- CI workflow: `.github/workflows/repository-policy.yml`.

GitHub Actions [43458532278](https://github.com/codexclai/HumanJS/actions/runs/43458532278) passed on exact code HEAD `f2df2e2e27b5b53a97a84f7c6b472f503c8f504d`. It ran 41 Rust unit tests, 3 synapse integration tests, 6 passive-membrane integration tests, parsed 20 Python experiment scripts, passed 37 Python tests, executed the five original NEURON 9.0.2 Na/K source protocols, validated the source replay tables and all three fit-sensitivity outputs, and passed repository policy.

## Interpretation boundary and next step

This experiment establishes a numerical sensitivity and profile-boundary problem in the deposited model's current-fit helper. It does not establish a biological fast-inactivation time constant, resolve a human-versus-animal inference, or validate the HumanJS single-compartment spike model. The inspected 65-file Dataverse v3.0 inventory still contains no raw human K voltage-clamp NWB traces or individual K kinetic CSVs. No empirical current refit is possible from this release.

Next, refine the fixed-tau profile over 320–360 ms at sub-millisecond resolution and inspect the residual waveform around the optimum before considering any source-equation change. Keep the raw-human-trace task open, keep the exploratory HumanJS spike model unaccepted, and do not contact authors or researchers.
