use crate::error::require_finite;
use crate::{
    Amperes, Farads, GlutamatergicSynapseModel, GlutamatergicSynapseRuntimeState, Ohms,
    Siemens, SimDuration, SimTime, SimulationError, SynapticConductances, TimeConstant, Volts,
};

/// Parameters for a lumped, single-compartment passive membrane approximation.
///
/// This model contains capacitance and a leak pathway only. It does not model
/// active ion channels, synaptic receptors, dendritic cable structure, or spikes.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct PassiveMembraneModel {
    capacitance: Farads,
    leak_conductance: Siemens,
    equilibrium_potential: Volts,
}

impl PassiveMembraneModel {
    pub const fn new(
        capacitance: Farads,
        leak_conductance: Siemens,
        equilibrium_potential: Volts,
    ) -> Self {
        Self {
            capacitance,
            leak_conductance,
            equilibrium_potential,
        }
    }

    /// Derive a lumped RC approximation from passive input resistance and time constant.
    ///
    /// Uses G = 1/R and C = tau/R. The equilibrium potential is the effective
    /// zero-injected-current operating point, not necessarily a measured single-channel
    /// leak reversal potential.
    pub fn from_input_resistance_and_time_constant(
        equilibrium_potential: Volts,
        input_resistance: Ohms,
        time_constant: TimeConstant,
    ) -> Result<Self, SimulationError> {
        let resistance = input_resistance.as_ohms();
        let conductance = Siemens::from_siemens(1.0 / resistance)?;
        let capacitance = Farads::from_farads(time_constant.as_seconds() / resistance)?;
        Ok(Self::new(capacitance, conductance, equilibrium_potential))
    }

    pub const fn capacitance(self) -> Farads {
        self.capacitance
    }
    pub const fn leak_conductance(self) -> Siemens {
        self.leak_conductance
    }
    pub const fn equilibrium_potential(self) -> Volts {
        self.equilibrium_potential
    }

    fn advance_voltage(
        self,
        voltage: Volts,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<Volts, SimulationError> {
        let conductance = self.leak_conductance.as_siemens();
        let equilibrium =
            self.equilibrium_potential.as_volts() + injected_current.as_amperes() / conductance;
        require_finite("current-driven equilibrium voltage (V)", equilibrium)
            .map_err(|_| SimulationError::NumericalOverflow)?;

        // Exact solution of C dV/dt = -g_L (V - E_L) + I for
        // a current held constant over this time interval.
        let exponent = -conductance * duration.as_seconds() / self.capacitance.as_farads();
        let decay = exponent.exp();
        let next_voltage = equilibrium + (voltage.as_volts() - equilibrium) * decay;
        Volts::from_volts(next_voltage).map_err(|_| SimulationError::NumericalOverflow)
    }

    fn advance_voltage_with_synaptic_conductances(
        self,
        voltage: Volts,
        duration: SimDuration,
        injected_current: Amperes,
        synaptic_model: GlutamatergicSynapseModel,
        conductances: SynapticConductances,
    ) -> Result<Volts, SimulationError> {
        let ampa = conductances.ampa_siemens();
        let nmda = conductances.nmda_siemens();
        require_finite("mean AMPA conductance (S)", ampa)?;
        require_finite("mean NMDA conductance (S)", nmda)?;

        // NMDA magnesium unblock depends on membrane voltage. Use a midpoint
        // predictor-corrector: first estimate the interval endpoint using the
        // starting voltage, then recalculate unblock at the predicted midpoint.
        let initial_block = synaptic_model
            .nmda_magnesium_block()
            .fraction_unblocked(voltage)?;
        let first = self.solve_with_conductances(
            voltage,
            duration,
            injected_current,
            synaptic_model.reversal_potential(),
            ampa,
            nmda,
            initial_block,
        )?;
        let midpoint = (voltage.as_volts() + first.as_volts()) * 0.5;
        require_finite("predicted midpoint membrane voltage (V)", midpoint)
            .map_err(|_| SimulationError::NumericalOverflow)?;
        let midpoint_voltage = Volts::from_volts(midpoint)
            .map_err(|_| SimulationError::NumericalOverflow)?;
        let midpoint_block = synaptic_model
            .nmda_magnesium_block()
            .fraction_unblocked(midpoint_voltage)?;

        self.solve_with_conductances(
            voltage,
            duration,
            injected_current,
            synaptic_model.reversal_potential(),
            ampa,
            nmda,
            midpoint_block,
        )
    }

    fn solve_with_conductances(
        self,
        voltage: Volts,
        duration: SimDuration,
        injected_current: Amperes,
        synaptic_reversal: Volts,
        ampa_siemens: f64,
        nmda_siemens: f64,
        nmda_unblocked_fraction: f64,
    ) -> Result<Volts, SimulationError> {
        let leak = self.leak_conductance.as_siemens();
        let nmda_effective = nmda_siemens * nmda_unblocked_fraction;
        let synaptic = ampa_siemens + nmda_effective;
        let total = leak + synaptic;
        require_finite("total membrane conductance (S)", total)
            .map_err(|_| SimulationError::NumericalOverflow)?;
        if total <= 0.0 {
            return Err(SimulationError::NumericalOverflow);
        }

        let weighted_reversals = leak * self.equilibrium_potential.as_volts()
            + synaptic * synaptic_reversal.as_volts()
            + injected_current.as_amperes();
        require_finite("total conductance-weighted current (A)", weighted_reversals)
            .map_err(|_| SimulationError::NumericalOverflow)?;
        let equilibrium = weighted_reversals / total;
        require_finite("synaptically driven equilibrium voltage (V)", equilibrium)
            .map_err(|_| SimulationError::NumericalOverflow)?;

        // The interval-mean receptor conductances and midpoint NMDA block are
        // held fixed for this analytic membrane update.
        let exponent = -total * duration.as_seconds() / self.capacitance.as_farads();
        let decay = exponent.exp();
        let next_voltage = equilibrium + (voltage.as_volts() - equilibrium) * decay;
        Volts::from_volts(next_voltage).map_err(|_| SimulationError::NumericalOverflow)
    }
}

/// Initial condition for a passive membrane simulation.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct MembranePatchInitialConditions {
    voltage: Volts,
}

impl MembranePatchInitialConditions {
    pub const fn new(voltage: Volts) -> Self {
        Self { voltage }
    }
    pub const fn voltage(self) -> Volts {
        self.voltage
    }
}

/// Live state of the currently simulated passive membrane patch.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct MembranePatchRuntimeState {
    time: SimTime,
    voltage: Volts,
}

impl MembranePatchRuntimeState {
    pub const fn time(self) -> SimTime {
        self.time
    }
    pub const fn voltage(self) -> Volts {
        self.voltage
    }
}

/// CPU simulation for one passive membrane patch.
#[derive(Debug, Clone, PartialEq)]
pub struct PassiveMembraneSimulation {
    model: PassiveMembraneModel,
    initial_conditions: MembranePatchInitialConditions,
    state: MembranePatchRuntimeState,
}

impl PassiveMembraneSimulation {
    pub const fn new(
        model: PassiveMembraneModel,
        initial_conditions: MembranePatchInitialConditions,
    ) -> Self {
        Self {
            model,
            initial_conditions,
            state: MembranePatchRuntimeState {
                time: SimTime::ZERO,
                voltage: initial_conditions.voltage,
            },
        }
    }

    pub const fn model(&self) -> PassiveMembraneModel {
        self.model
    }
    pub const fn initial_conditions(&self) -> MembranePatchInitialConditions {
        self.initial_conditions
    }
    pub const fn state(&self) -> MembranePatchRuntimeState {
        self.state
    }

    /// Advance a passive membrane using constant injected current.
    ///
    /// The live state is assigned only after the next time and voltage have
    /// both been computed successfully.
    pub fn step(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<MembranePatchRuntimeState, SimulationError> {
        let next_time = self.state.time.checked_add(duration)?;
        let next_voltage =
            self.model
                .advance_voltage(self.state.voltage, duration, injected_current)?;
        let next_state = MembranePatchRuntimeState {
            time: next_time,
            voltage: next_voltage,
        };
        self.state = next_state;
        Ok(next_state)
    }

    /// Advance with one externally-triggered glutamatergic synaptic contact.
    ///
    /// Receptor conductances are analytically averaged over the interval.
    /// NMDA magnesium unblock uses a midpoint predictor-corrector. The
    /// membrane and synaptic live states are committed together only after
    /// the complete coupled step succeeds.
    pub fn step_with_glutamatergic_synapse(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
        synapse_model: GlutamatergicSynapseModel,
        synapse_state: &mut GlutamatergicSynapseRuntimeState,
    ) -> Result<MembranePatchRuntimeState, SimulationError> {
        let next_time = self.state.time.checked_add(duration)?;
        let (conductances, next_synapse_state) =
            synapse_state.prepare_step(synapse_model, duration)?;
        let next_voltage = self.model.advance_voltage_with_synaptic_conductances(
            self.state.voltage,
            duration,
            injected_current,
            synapse_model,
            conductances,
        )?;

        let next_membrane_state = MembranePatchRuntimeState {
            time: next_time,
            voltage: next_voltage,
        };
        self.state = next_membrane_state;
        *synapse_state = next_synapse_state;
        Ok(next_membrane_state)
    }

    /// Restore the initial voltage and reset the simulation clock to zero.
    pub fn reset(&mut self) {
        self.state = MembranePatchRuntimeState {
            time: SimTime::ZERO,
            voltage: self.initial_conditions.voltage,
        };
    }
}
