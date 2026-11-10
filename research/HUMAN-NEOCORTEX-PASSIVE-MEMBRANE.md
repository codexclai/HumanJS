# Human neocortical passive-membrane evidence note

**Status:** evidence review for the first CPU implementation slice; not a calibrated cell model.  
**Reviewed:** 2026-11-10.

## Direct human evidence used

Chameh et al. (2021), *Diversity amongst human cortical pyramidal neurons revealed via their sag currents and frequency preferences*, Nature Communications 12, 2497. [https://doi.org/10.1038/s41467-021-22741-9](https://doi.org/10.1038/s41467-021-22741-9)

The study used in-vitro whole-cell recordings from acute human neocortical slices collected from 61 surgical patients. Recordings targeted pyramidal neurons in L2&3, L3c, and L5. The authors reported substantial electrophysiological heterogeneity within and across layers.

Reported group summaries included:

- Resting membrane potential: L2&3, −68.2 ± 5.3 mV; L3c, −65.6 ± 3.8 mV; L5, −65.6 ± 6.5 mV.
- Input resistance for L2&3: 83 ± 38.1 MΩ.
- Membrane time constant: L2&3, 13.7 ± 7.1 ms; L3c, 17.1 ± 5.7 ms; L5, 19.3 ± 9.1 ms.

The same study measured hyperpolarization-activated sag and rebound behavior and reported layer-related differences. Those active subthreshold properties are outside the first implementation slice.

## Modeling interpretation

The initial implementation represents only the passive, single-compartment RC equation:

`C dV/dt = -g_L (V - E_L) + I_injected`

For a lumped passive approximation, an input resistance `R_in` and membrane time constant `tau_m` imply:

- `g_L = 1 / R_in`
- `C = tau_m / R_in`

The implementation exposes this conversion but does not install the published group mean as a universal human parameter set. Parameter heterogeneity, cell layer, morphology, age, tissue preparation, and active currents matter. A group mean from surgical tissue is not a canonical neuron.

The model's equilibrium-potential argument is the effective zero-injected-current operating point. It is not automatically a direct measurement of a single leak-channel reversal potential. This mapping is an engineering reduction for the limited RC model.

## Evidence class and limitations

- **Species:** human.
- **Preparation/method:** acute surgical neocortical tissue; in-vitro whole-cell patch-clamp recordings.
- **Anatomical resolution:** layer-targeted pyramidal-cell recordings, not a whole-cell census.
- **Population caveat:** surgical patient samples are not a random sample of healthy human cortex.
- **Measured findings:** group distributions and means for passive membrane properties; evidence of heterogeneity and layer differences.
- **Model inference:** lumped capacitance and leak conductance derived from `R_in` and `tau_m` using the single-compartment RC relation.
- **Not established:** a calibrated parameter distribution, dendritic cable model, active ion-channel model, synaptic transmission, action-potential generation, network dynamics, or biological validation of HumanJS.

The first software tests check the mathematical behavior of the declared reduced equation. They do not validate that equation as a complete model of any human neuron.
