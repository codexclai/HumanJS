use crate::error::{require_finite, require_positive};
use crate::{Siemens, SimDuration, SimulationError, TimeConstant, Volts};

/// Effective rise/decay parameters for one ionotropic glutamate-receptor component.
///
/// This normalized biexponential conductance kernel is the waveform abstraction
/// used for human L2/L3 pyramidal-cell synapses by Eyal et al. (2018). Its rise
/// and decay values are effective waveform parameters, not microscopic receptor
/// transition rates or a molecular receptor Markov model.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SynapticReceptorKinetics {
    peak_conductance: Siemens,
    rise_time: TimeConstant,
    decay_time: TimeConstant,
    normalization: f64,
}

impl SynapticReceptorKinetics {
    pub fn new(
        peak_conductance: Siemens,
        rise_time: TimeConstant,
        decay_time: TimeConstant,
    ) -> Result<Self, SimulationError> {
        let tau_rise = rise_time.as_seconds();
        let tau_decay = decay_time.as_seconds();
        if tau_decay <= tau_rise {
            return Err(SimulationError::InvalidKineticOrdering {
                rise_seconds: tau_rise,
                decay_seconds: tau_decay,
            });
        }

        let log_ratio = tau_decay.ln() - tau_rise.ln();
        let peak_time = tau_rise * tau_decay / (tau_decay - tau_rise) * log_ratio;
        let denominator = (-peak_time / tau_decay).exp() - (-peak_time / tau_rise).exp();
        let normalization = 1.0 / denominator;
        require_finite("synaptic conductance normalization", normalization)?;
        if normalization <= 0.0 {
            return Err(SimulationError::NumericalOverflow);
        }

        Ok(Self {
            peak_conductance,
            rise_time,
            decay_time,
            normalization,
        })
    }

    pub const fn peak_conductance(self) -> Siemens {
        self.peak_conductance
    }

    pub const fn rise_time(self) -> TimeConstant {
        self.rise_time
    }

    pub const fn decay_time(self) -> TimeConstant {
        self.decay_time
    }

    /// Time at which an isolated release reaches its specified peak conductance.
    pub fn peak_time(self) -> Result<TimeConstant, SimulationError> {
        let rise = self.rise_time.as_seconds();
        let decay = self.decay_time.as_seconds();
        let peak = rise * decay / (decay - rise) * (decay.ln() - rise.ln());
        TimeConstant::from_seconds(peak)
    }

    fn advance(
        self,
        state: BiExponentialState,
        duration: SimDuration,
    ) -> Result<(f64, BiExponentialState), SimulationError> {
        let dt = duration.as_seconds();
        let tau_rise = self.rise_time.as_seconds();
        let tau_decay = self.decay_time.as_seconds();

        // Integrate each exponential analytically to obtain the exact mean
        // conductance over this interval, then retain its decayed state.
        let rise_integral = state.rise * tau_rise * -(-dt / tau_rise).exp_m1();
        let decay_integral = state.decay * tau_decay * -(-dt / tau_decay).exp_m1();
        let average = self.peak_conductance.as_siemens()
            * self.normalization
            * (decay_integral - rise_integral)
            / dt;
        require_finite("mean synaptic conductance (S)", average)?;
        if average < 0.0 {
            return Err(SimulationError::NumericalOverflow);
        }

        let next = BiExponentialState {
            rise: state.rise * (-dt / tau_rise).exp(),
            decay: state.decay * (-dt / tau_decay).exp(),
        };
        require_finite("synaptic rise state", next.rise)?;
        require_finite("synaptic decay state", next.decay)?;
        Ok((average, next))
    }

    fn instantaneous(self, state: BiExponentialState) -> Result<f64, SimulationError> {
        let conductance =
            self.peak_conductance.as_siemens() * self.normalization * (state.decay - state.rise);
        require_finite("instantaneous synaptic conductance (S)", conductance)?;
        if conductance < 0.0 {
            return Err(SimulationError::NumericalOverflow);
        }
        Ok(conductance)
    }
}

/// Parameters for the voltage-dependent magnesium block of NMDA receptors.
///
/// The equation follows the Jahr-Stevens form used by Eyal et al. (2018):
/// B(V) = 1 / (1 + exp(-gamma * V_mV) * [Mg] * n).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct NmdaMagnesiumBlock {
    gamma_per_millivolt: f64,
    magnesium_millimolar: f64,
    coefficient_per_millimolar: f64,
}

impl NmdaMagnesiumBlock {
    pub fn new(
        gamma_per_millivolt: f64,
        magnesium_millimolar: f64,
        coefficient_per_millimolar: f64,
    ) -> Result<Self, SimulationError> {
        require_positive("NMDA magnesium-block gamma (mV^-1)", gamma_per_millivolt)?;
        require_positive(
            "extracellular magnesium concentration (mM)",
            magnesium_millimolar,
        )?;
        require_positive(
            "NMDA magnesium-block coefficient (mM^-1)",
            coefficient_per_millimolar,
        )?;
        Ok(Self {
            gamma_per_millivolt,
            magnesium_millimolar,
            coefficient_per_millimolar,
        })
    }

    pub const fn gamma_per_millivolt(self) -> f64 {
        self.gamma_per_millivolt
    }

    pub const fn magnesium_millimolar(self) -> f64 {
        self.magnesium_millimolar
    }

    pub const fn coefficient_per_millimolar(self) -> f64 {
        self.coefficient_per_millimolar
    }

    /// Fraction of NMDA conductance not blocked by extracellular magnesium.
    pub fn fraction_unblocked(self, voltage: Volts) -> Result<f64, SimulationError> {
        let log_block = self.magnesium_millimolar.ln() + self.coefficient_per_millimolar.ln()
            - self.gamma_per_millivolt * voltage.as_volts() * 1_000.0;
        if log_block.is_nan() {
            return Err(SimulationError::NumericalOverflow);
        }

        // Stable logistic evaluation; avoids overflow for strongly negative V.
        let unblocked = if log_block >= 0.0 {
            let inverse = (-log_block).exp();
            inverse / (1.0 + inverse)
        } else {
            1.0 / (1.0 + log_block.exp())
        };
        if unblocked.is_finite() && (0.0..=1.0).contains(&unblocked) {
            Ok(unblocked)
        } else {
            Err(SimulationError::NumericalOverflow)
        }
    }
}

/// Deterministic short-term depression parameters for a presynaptic connection.
///
/// Utilization is the fraction of available resources consumed by a
/// presynaptic spike. Recovery is represented by a first-order exponential.
/// The human L2/L3 parameter values are connection-level fit parameters; using
/// them with this one-contact conductance abstraction is an explicit reduction.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct PresynapticDepressionModel {
    utilization: f64,
    recovery_time_constant: TimeConstant,
}

impl PresynapticDepressionModel {
    pub fn new(
        utilization: f64,
        recovery_time_constant: TimeConstant,
    ) -> Result<Self, SimulationError> {
        require_finite("presynaptic utilization", utilization)?;
        if utilization <= 0.0 || utilization > 1.0 {
            return Err(SimulationError::OutOfRangeValue {
                field: "presynaptic utilization",
                value: utilization,
                minimum: 0.0,
                maximum: 1.0,
            });
        }
        Ok(Self {
            utilization,
            recovery_time_constant,
        })
    }

    pub const fn utilization(self) -> f64 {
        self.utilization
    }

    pub const fn recovery_time_constant(self) -> TimeConstant {
        self.recovery_time_constant
    }
}

/// Model parameters for a single glutamatergic synaptic contact.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct GlutamatergicSynapseModel {
    ampa: SynapticReceptorKinetics,
    nmda: SynapticReceptorKinetics,
    nmda_magnesium_block: NmdaMagnesiumBlock,
    presynaptic_depression: PresynapticDepressionModel,
    reversal_potential: Volts,
}

impl GlutamatergicSynapseModel {
    pub const fn new(
        ampa: SynapticReceptorKinetics,
        nmda: SynapticReceptorKinetics,
        nmda_magnesium_block: NmdaMagnesiumBlock,
        presynaptic_depression: PresynapticDepressionModel,
        reversal_potential: Volts,
    ) -> Self {
        Self {
            ampa,
            nmda,
            nmda_magnesium_block,
            presynaptic_depression,
            reversal_potential,
        }
    }

    pub const fn ampa(self) -> SynapticReceptorKinetics {
        self.ampa
    }

    pub const fn nmda(self) -> SynapticReceptorKinetics {
        self.nmda
    }

    pub const fn nmda_magnesium_block(self) -> NmdaMagnesiumBlock {
        self.nmda_magnesium_block
    }

    pub const fn presynaptic_depression(self) -> PresynapticDepressionModel {
        self.presynaptic_depression
    }

    pub const fn reversal_potential(self) -> Volts {
        self.reversal_potential
    }
}

/// Configurable initial availability for one synaptic contact.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct GlutamatergicSynapseInitialConditions {
    available_resources: f64,
}

impl GlutamatergicSynapseInitialConditions {
    pub fn new(available_resources: f64) -> Result<Self, SimulationError> {
        require_finite(
            "initial presynaptic resource availability",
            available_resources,
        )?;
        if !(0.0..=1.0).contains(&available_resources) {
            return Err(SimulationError::OutOfRangeValue {
                field: "initial presynaptic resource availability",
                value: available_resources,
                minimum: 0.0,
                maximum: 1.0,
            });
        }
        Ok(Self {
            available_resources,
        })
    }

    /// A rested contact with no residual receptor activation.
    pub const fn fully_recovered() -> Self {
        Self {
            available_resources: 1.0,
        }
    }

    pub const fn available_resources(self) -> f64 {
        self.available_resources
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq)]
struct BiExponentialState {
    rise: f64,
    decay: f64,
}

/// Live presynaptic resource and postsynaptic receptor activation state.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct GlutamatergicSynapseRuntimeState {
    available_resources: f64,
    ampa: BiExponentialState,
    nmda: BiExponentialState,
}

impl GlutamatergicSynapseRuntimeState {
    pub const fn from_initial_conditions(
        initial_conditions: GlutamatergicSynapseInitialConditions,
    ) -> Self {
        Self {
            available_resources: initial_conditions.available_resources,
            ampa: BiExponentialState {
                rise: 0.0,
                decay: 0.0,
            },
            nmda: BiExponentialState {
                rise: 0.0,
                decay: 0.0,
            },
        }
    }

    pub const fn available_resources(self) -> f64 {
        self.available_resources
    }

    /// Apply a presynaptic spike and return its normalized effective response.
    ///
    /// The response is scaled by currently available resources; the resource
    /// pool is then depleted by the model's utilization fraction. This is a
    /// deterministic short-term-plasticity approximation, not stochastic
    /// single-vesicle fusion.
    pub fn trigger_presynaptic_spike(
        &mut self,
        model: GlutamatergicSynapseModel,
    ) -> Result<f64, SimulationError> {
        let amplitude = self.available_resources;
        let next_resources = amplitude * (1.0 - model.presynaptic_depression.utilization);
        let next_ampa = BiExponentialState {
            rise: self.ampa.rise + amplitude,
            decay: self.ampa.decay + amplitude,
        };
        let next_nmda = BiExponentialState {
            rise: self.nmda.rise + amplitude,
            decay: self.nmda.decay + amplitude,
        };
        require_finite("presynaptic resource availability", next_resources)?;
        require_finite("AMPA receptor rise state", next_ampa.rise)?;
        require_finite("AMPA receptor decay state", next_ampa.decay)?;
        require_finite("NMDA receptor rise state", next_nmda.rise)?;
        require_finite("NMDA receptor decay state", next_nmda.decay)?;

        self.available_resources = next_resources;
        self.ampa = next_ampa;
        self.nmda = next_nmda;
        Ok(amplitude)
    }

    /// Return instantaneous AMPA and NMDA conductance in siemens.
    pub fn instantaneous_conductances(
        self,
        model: GlutamatergicSynapseModel,
    ) -> Result<SynapticConductances, SimulationError> {
        Ok(SynapticConductances {
            ampa_siemens: model.ampa.instantaneous(self.ampa)?,
            nmda_siemens: model.nmda.instantaneous(self.nmda)?,
        })
    }

    pub(crate) fn prepare_step(
        self,
        model: GlutamatergicSynapseModel,
        duration: SimDuration,
    ) -> Result<(SynapticConductances, Self), SimulationError> {
        let (ampa_average, next_ampa) = model.ampa.advance(self.ampa, duration)?;
        let (nmda_average, next_nmda) = model.nmda.advance(self.nmda, duration)?;

        let dt = duration.as_seconds();
        let tau_recovery = model
            .presynaptic_depression
            .recovery_time_constant
            .as_seconds();
        let recovery = (-dt / tau_recovery).exp();
        let next_resources = 1.0 - (1.0 - self.available_resources) * recovery;
        require_finite("presynaptic resource recovery", next_resources)?;
        if !(0.0..=1.0).contains(&next_resources) {
            return Err(SimulationError::NumericalOverflow);
        }

        let next_state = Self {
            available_resources: next_resources,
            ampa: next_ampa,
            nmda: next_nmda,
        };
        Ok((
            SynapticConductances {
                ampa_siemens: ampa_average,
                nmda_siemens: nmda_average,
            },
            next_state,
        ))
    }
}

/// Mean or instantaneous receptor conductances in siemens.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SynapticConductances {
    ampa_siemens: f64,
    nmda_siemens: f64,
}

impl SynapticConductances {
    pub const fn ampa_siemens(self) -> f64 {
        self.ampa_siemens
    }

    pub const fn nmda_siemens(self) -> f64 {
        self.nmda_siemens
    }
}

#[cfg(test)]
mod tests {
    use super::{
        GlutamatergicSynapseInitialConditions, GlutamatergicSynapseModel,
        GlutamatergicSynapseRuntimeState, NmdaMagnesiumBlock, PresynapticDepressionModel,
        SynapticReceptorKinetics,
    };
    use crate::{Siemens, SimDuration, SimulationError, TimeConstant, Volts};

    fn human_l23_synapse_model() -> GlutamatergicSynapseModel {
        let ampa = SynapticReceptorKinetics::new(
            Siemens::from_nanosiemens(0.73).unwrap(),
            TimeConstant::from_milliseconds(0.3).unwrap(),
            TimeConstant::from_milliseconds(1.8).unwrap(),
        )
        .unwrap();
        let nmda = SynapticReceptorKinetics::new(
            Siemens::from_nanosiemens(1.31).unwrap(),
            TimeConstant::from_milliseconds(8.02).unwrap(),
            TimeConstant::from_milliseconds(34.99).unwrap(),
        )
        .unwrap();
        let block = NmdaMagnesiumBlock::new(0.077, 1.0, 0.28).unwrap();
        let depression =
            PresynapticDepressionModel::new(0.45, TimeConstant::from_milliseconds(144.0).unwrap())
                .unwrap();
        GlutamatergicSynapseModel::new(
            ampa,
            nmda,
            block,
            depression,
            Volts::from_millivolts(0.0).unwrap(),
        )
    }

    #[test]
    fn biexponential_kernel_is_normalized_to_the_requested_peak() {
        let kinetics = SynapticReceptorKinetics::new(
            Siemens::from_nanosiemens(0.73).unwrap(),
            TimeConstant::from_milliseconds(0.3).unwrap(),
            TimeConstant::from_milliseconds(1.8).unwrap(),
        )
        .unwrap();
        let peak = kinetics.peak_time().unwrap().as_seconds();
        let state = super::BiExponentialState {
            rise: (-peak / kinetics.rise_time().as_seconds()).exp(),
            decay: (-peak / kinetics.decay_time().as_seconds()).exp(),
        };
        let observed = kinetics.instantaneous(state).unwrap();
        assert!((observed - kinetics.peak_conductance().as_siemens()).abs() < 1.0e-20);
    }

    #[test]
    fn receptor_kinetics_require_a_slower_decay_than_rise() {
        let result = SynapticReceptorKinetics::new(
            Siemens::from_nanosiemens(1.0).unwrap(),
            TimeConstant::from_milliseconds(2.0).unwrap(),
            TimeConstant::from_milliseconds(1.0).unwrap(),
        );
        assert!(matches!(
            result,
            Err(SimulationError::InvalidKineticOrdering { .. })
        ));
    }

    #[test]
    fn magnesium_block_is_relaxed_by_depolarization() {
        let model = NmdaMagnesiumBlock::new(0.077, 1.0, 0.28).unwrap();
        let resting = model
            .fraction_unblocked(Volts::from_millivolts(-68.0).unwrap())
            .unwrap();
        let depolarized = model
            .fraction_unblocked(Volts::from_millivolts(-30.0).unwrap())
            .unwrap();
        assert!(resting < depolarized);
        assert!((0.0..=1.0).contains(&resting));
        assert!((0.0..=1.0).contains(&depolarized));
    }

    #[test]
    fn presynaptic_depression_and_recovery_match_the_human_fit_scale() {
        let model = human_l23_synapse_model();
        let mut state = GlutamatergicSynapseRuntimeState::from_initial_conditions(
            GlutamatergicSynapseInitialConditions::fully_recovered(),
        );
        let mut amplitudes = Vec::new();
        amplitudes.push(state.trigger_presynaptic_spike(model).unwrap());

        let interval = SimDuration::from_nanoseconds(33_333_333).unwrap();
        for _ in 1..8 {
            let (_, next) = state.prepare_step(model, interval).unwrap();
            state = next;
            amplitudes.push(state.trigger_presynaptic_spike(model).unwrap());
        }

        assert!(amplitudes.windows(2).all(|pair| pair[1] < pair[0]));
        assert!((amplitudes[7] - 0.368).abs() < 0.01);

        let recovery = SimDuration::from_milliseconds(500).unwrap();
        let (_, next) = state.prepare_step(model, recovery).unwrap();
        state = next;
        let recovered = state.trigger_presynaptic_spike(model).unwrap();
        assert!(recovered > 0.95);
    }
}
