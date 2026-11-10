# Human cortical glutamatergic synapse evidence note

**Status:** evidence review for the first integrated glutamatergic conductance mechanism; not a complete molecular or ultrastructural synapse model.  
**Reviewed:** 2026-11-10.

## Scope selected

The first synaptic mechanism targets a narrowly defined connection class: excitatory glutamatergic input from an adult human neocortical L2/L3 pyramidal neuron onto another L2/L3 pyramidal neuron in temporal cortex. It uses human data where available and explicitly labels model-fitted parameters and reduced representations.

It is not a universal cortical synapse. Different presynaptic and postsynaptic cell classes, layers, locations, ages, receptor complements, release machinery, and tissue conditions can produce different properties.

## Human pyramidal-to-pyramidal short-term dynamics

Testa-Silva et al. (2014), *High bandwidth synaptic communication and frequency tracking in human neocortex*, PLoS Biology 12:e1002007. [https://doi.org/10.1371/journal.pbio.1002007](https://doi.org/10.1371/journal.pbio.1002007)

The authors made paired whole-cell recordings from connected pyramidal neurons in acute adult human temporal-cortex slices from surgical tissue and compared them with mouse cortex. Human connections were purely depressing in the tested protocols. During 30 Hz trains the eighth-to-first EPSP ratio was 0.38 ± 0.03. Recovery measurements showed 0.92 ± 0.04 at 300 ms and 1.01 ± 0.07 at 500 ms relative to the first response.

A Tsodyks-Markram short-term-plasticity model fitted to the recordings yielded a utilization parameter U = 0.45 ± 0.03 and a recovery time constant of 144 ± 13 ms. These are parameters of a fitted model at the recorded connection level. They are not direct single-vesicle fusion-probability measurements, nor direct observations of one bouton's readily releasable pool.

The code uses the bounded deterministic resource abstraction:
- Each presynaptic event produces a conductance-kernel amplitude proportional to the currently available resource fraction x.
- The event depletes availability by x ← x(1 − U).
- Between events, availability recovers according to dx/dt = (1 − x)/tau_recovery.

With U = 0.45 and tau_recovery = 144 ms, the recurrence gives an eighth-to-first response ratio of approximately 0.369 at 30 Hz, close to the reported 0.38 mean. This is a computational correspondence to the fitted connection-level dynamics, not independent validation of a microscopic vesicle-pool mechanism.

## Human L2/L3 AMPA and NMDA conductance estimates

Eyal et al. (2018), *Human cortical pyramidal neurons: From spines to spikes via models*, Frontiers in Cellular Neuroscience 12:181. [https://doi.org/10.3389/fncel.2018.00181](https://doi.org/10.3389/fncel.2018.00181)

The study combined paired recordings from connected human L2/L3 pyramidal-neuron pairs, human neocortical morphology, passive membrane models, and extracellularly evoked composite EPSPs. AMPA- and NMDA-mediated inputs were represented with normalized rise/decay conductance waveforms.

The synaptic current equation used in the model is:
`I_syn = g_syn(t,V) (V - E_syn)`

Both AMPA and NMDA reversal potentials were set to 0 mV. AMPA conductance was treated as voltage independent. The stated AMPA waveform parameters were a 0.3 ms rise time and 1.8 ms decay time. AMPA kinetics were held constant in the study; peak conductance was fitted to experimental EPSPs.

The representative fitted NMDA parameters were:
- Rise time: 8.02 ms.
- Decay time: 34.99 ms.
- Voltage-dependence steepness gamma: 0.077 per mV.
- Peak NMDA conductance: 1.31 nS per modeled contact.
- Peak AMPA conductance in the representative fit: 0.73 nS per contact.

The representative fit used extracellular Mg2+ = 1 mM and the coefficient n = 0.28 mM^-1 from the earlier Jahr and Stevens magnesium-block formulation. The NMDA block is:
`B(V) = 1 / (1 + exp(-gamma V_mV) [Mg2+] n)`

The model therefore represents NMDA conductance as voltage dependent and relieves magnesium block with depolarization. The kinetic and peak-conductance values above are model-fitted/effective waveform parameters, not direct isolated measurements of AMPA or NMDA receptor microscopic transition rates at a single human synapse. AMPA conductance/contact estimates also depend on an assumed average of five contacts per pyramidal-to-pyramidal connection. The authors explicitly identify this contact-count assumption as needing further study.

## Cell-type specificity warning: human pyramidal-to-interneuron evidence

Molnár et al. (2016), *Human pyramidal to interneuron synapses are mediated by multi-vesicular release and multiple docked vesicles*, eLife 5:e18167. [https://doi.org/10.7554/eLife.18167](https://doi.org/10.7554/eLife.18167)

This study examined a different connection class: human pyramidal-cell to fast-spiking-interneuron synapses. Paired recordings, multiple-probability fluctuation analysis, light microscopy, and electron microscopy indicated more functional release sites and docked vesicles in the sampled human connections than in rat comparisons.

These observations demonstrate that release-site organization can differ across species and connection classes. They are not used as numerical presynaptic parameters for the pyramidal-to-pyramidal model in this implementation. Extrapolating the interneuron-targeted results to pyramidal-to-pyramidal boutons would be unjustified.

## Implemented computational abstraction

The Rust implementation combines:
1. Separate AMPA- and NMDA-like normalized biexponential conductance kernels.
2. A voltage-dependent NMDA magnesium-unblock factor.
3. A deterministic presynaptic availability/depression variable with exponential recovery.
4. A single-compartment postsynaptic passive membrane equation.
5. An interval-mean conductance update with midpoint evaluation of voltage-dependent magnesium unblock.

Conductance kernels are normalized to their specified peak conductance. The membrane solver uses their interval-average conductance for each simulation step. NMDA magnesium unblock is estimated at the predicted midpoint voltage. The numerical approximation therefore depends on the chosen integration interval; reducing the interval should converge toward the time-varying response.

## Explicit exclusions and validation limits

This version does not yet model:
- A presynaptic action-potential waveform, voltage-gated Ca2+ entry, Ca2+ nanodomains, docking/priming, stochastic vesicle fusion, multivesicular release, or a measured release probability.
- An explicit synaptic-cleft glutamate concentration waveform, diffusion, spillover, uptake, or astrocytic transporter kinetics.
- Molecular AMPA/NMDA receptor ligand-binding, channel-opening Markov states, desensitization/recovery, subunit composition, or co-agonist occupancy.
- Dendritic spines, spine-neck resistance, dendritic cable filtering, spatially distributed synapses, or NMDA dendritic spikes.
- Inhibitory synapses or other connection classes.

The event trigger is a presynaptic-spike input boundary. The effective conductance response compresses release and receptor activation into receptor-specific fitted waveform kernels. The resource model is a deterministic approximation of connection-level short-term depression and recovery. The current implementation is an integrated computational mechanism, but passing software tests does not biologically validate it or establish full synaptic physiology.
