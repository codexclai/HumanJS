use crate::error::{require_finite, require_positive};
use crate::{
    Amperes, FaradsPerSquareMeter, SiemensPerSquareMeter, SimDuration, SimTime, SimulationError,
    SquareMeters, Volts,
};

#[derive(Debug, Clone, Copy, PartialEq)]
struct GateRates {
    steady_state: f64,
    time_constant_ms: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct SodiumRates {
    activation: GateRates,
    inactivation: GateRates,
    temperature_factor: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct PotassiumRates {
    activation: GateRates,
    fast_inactivation: GateRates,
    slow_inactivation_time_constant_ms: f64,
}

/// Outward membrane-current balance at one coupled RK4 derivative stage.
/// Current densities use A/m² and voltage derivative uses V/s.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct HumanL23SingleCompartmentCurrentBalance {
    sodium_current_density_a_per_m2: f64,
    potassium_current_density_a_per_m2: f64,
    leak_current_density_a_per_m2: f64,
    injected_current_density_a_per_m2: f64,
    voltage_derivative_v_per_s: f64,
}

impl HumanL23SingleCompartmentCurrentBalance {
    const ZERO: Self = Self {
        sodium_current_density_a_per_m2: 0.0,
        potassium_current_density_a_per_m2: 0.0,
        leak_current_density_a_per_m2: 0.0,
        injected_current_density_a_per_m2: 0.0,
        voltage_derivative_v_per_s: 0.0,
    };
    pub const fn sodium_current_density_a_per_m2(self) -> f64 {
        self.sodium_current_density_a_per_m2
    }
    pub const fn potassium_current_density_a_per_m2(self) -> f64 {
        self.potassium_current_density_a_per_m2
    }
    pub const fn leak_current_density_a_per_m2(self) -> f64 {
        self.leak_current_density_a_per_m2
    }
    pub const fn injected_current_density_a_per_m2(self) -> f64 {
        self.injected_current_density_a_per_m2
    }
    pub const fn voltage_derivative_v_per_s(self) -> f64 {
        self.voltage_derivative_v_per_s
    }
    pub const fn total_ionic_current_density_a_per_m2(self) -> f64 {
        self.sodium_current_density_a_per_m2
            + self.potassium_current_density_a_per_m2
            + self.leak_current_density_a_per_m2
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct RatePrefactor {
    // The pure NMODL files and Table S2 declare these prefactors as ms^-1.
    // But trap0 multiplies a by the voltage-valued term (V - th), so the
    // equation requires mV^-1 ms^-1 for its result to be a rate in ms^-1.
    // Preserve source numeric values, but expose the equation-consistent unit.
    per_millivolt_per_ms: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct SodiumChannelParameters {
    activation_half_voltage_mv: f64,
    activation_slope_mv: f64,
    activation_rate_half_voltage_mv: f64,
    activation_rate_slope_mv: f64,
    activation_rate: RatePrefactor,
    inactivation_half_voltage_mv: f64,
    inactivation_slope_mv: f64,
    inactivation_rate_half_voltage_mv: f64,
    recovery_rate_half_voltage_mv: f64,
    inactivation_rate_slope_mv: f64,
    recovery_rate_slope_mv: f64,
    inactivation_rate: RatePrefactor,
    recovery_rate: RatePrefactor,
    reference_temperature_celsius: f64,
    q10: f64,
    inactivation_voltage_shift_mv: f64,
}

impl SodiumChannelParameters {
    const HUMAN_L23: Self = Self {
        activation_half_voltage_mv: -42.29145668954657,
        activation_slope_mv: 10.231152896063074,
        activation_rate_half_voltage_mv: -58.59235606617833,
        activation_rate_slope_mv: 9.21455371864071,
        activation_rate: RatePrefactor {
            per_millivolt_per_ms: 0.2139849270413559,
        },
        inactivation_half_voltage_mv: -64.48,
        inactivation_slope_mv: 11.02,
        inactivation_rate_half_voltage_mv: -39.298676911255,
        recovery_rate_half_voltage_mv: -77.16674532461128,
        inactivation_rate_slope_mv: 7.21636386592805,
        recovery_rate_slope_mv: 4.749450048393884,
        inactivation_rate: RatePrefactor {
            per_millivolt_per_ms: 0.0476391878313753,
        },
        recovery_rate: RatePrefactor {
            per_millivolt_per_ms: 0.011951655023359499,
        },
        reference_temperature_celsius: 25.0,
        q10: 2.3,
        inactivation_voltage_shift_mv: 0.0,
    };
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct PotassiumChannelParameters {
    activation_half_voltage_mv: f64,
    activation_slope_mv: f64,
    activation_rate_half_voltage_mv: f64,
    activation_rate_slope_mv: f64,
    activation_rate: RatePrefactor,
    inactivation_half_voltage_mv: f64,
    inactivation_slope_mv: f64,
    inactivation_rate_half_voltage_mv: f64,
    recovery_rate_half_voltage_mv: f64,
    inactivation_rate_slope_mv: f64,
    recovery_rate_slope_mv: f64,
    inactivation_rate: RatePrefactor,
    recovery_rate: RatePrefactor,
    slow_inactivation_time_constant_ms: f64,
    slow_recovery_time_constant_ms: f64,
    inactivating_fraction: f64,
    slow_fraction_of_inactivating: f64,
    inactivation_rate_factor: f64,
    reference_temperature_celsius: f64,
    q10: f64,
}

impl PotassiumChannelParameters {
    const HUMAN_L23: Self = Self {
        activation_half_voltage_mv: -18.406163539758502,
        activation_slope_mv: 19.199550273441083,
        activation_rate_half_voltage_mv: -29.961798016904638,
        activation_rate_slope_mv: 6.590405688881463,
        activation_rate: RatePrefactor {
            per_millivolt_per_ms: 0.018459250585411965,
        },
        inactivation_half_voltage_mv: -52.61,
        inactivation_slope_mv: 13.09,
        inactivation_rate_half_voltage_mv: 40.5659148938157,
        recovery_rate_half_voltage_mv: -75.93822659307075,
        inactivation_rate_slope_mv: 26.773929244740913,
        recovery_rate_slope_mv: 0.40183382749400054,
        inactivation_rate: RatePrefactor {
            per_millivolt_per_ms: 0.0016901435659310753,
        },
        recovery_rate: RatePrefactor {
            per_millivolt_per_ms: 0.0004968791312639546,
        },
        slow_inactivation_time_constant_ms: 450.0,
        slow_recovery_time_constant_ms: 2789.7929428108187,
        inactivating_fraction: 0.85,
        slow_fraction_of_inactivating: 0.4,
        inactivation_rate_factor: 1.0,
        reference_temperature_celsius: 34.0,
        q10: 2.3,
    };
}

/// Parameters for a single-compartment human L2/L3 single-compartment model.
///
/// This is the Wilbers et al. human Na+/K+ channel model coupled to a lumped
/// single compartment. It has no spatially resolved AIS, axon, or dendritic
/// compartments. The channel gate equations and fitted values are retained,
/// but the source's singular rate function is evaluated with its analytic limit.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct HumanL23SingleCompartmentModel {
    surface_area: SquareMeters,
    specific_capacitance: FaradsPerSquareMeter,
    sodium_max_conductance_density: SiemensPerSquareMeter,
    potassium_max_conductance_density: SiemensPerSquareMeter,
    leak_conductance_density: SiemensPerSquareMeter,
    sodium_reversal: Volts,
    potassium_reversal: Volts,
    leak_reversal: Volts,
    temperature_celsius: f64,
    voltage_shift_mv: f64,
    max_internal_step: SimDuration,
    sodium: SodiumChannelParameters,
    potassium: PotassiumChannelParameters,
}

impl HumanL23SingleCompartmentModel {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        surface_area: SquareMeters,
        specific_capacitance: FaradsPerSquareMeter,
        sodium_max_conductance_density: SiemensPerSquareMeter,
        potassium_max_conductance_density: SiemensPerSquareMeter,
        leak_conductance_density: SiemensPerSquareMeter,
        sodium_reversal: Volts,
        potassium_reversal: Volts,
        leak_reversal: Volts,
        temperature_celsius: f64,
        voltage_shift_mv: f64,
        max_internal_step: SimDuration,
    ) -> Result<Self, SimulationError> {
        require_finite("single-compartment temperature (°C)", temperature_celsius)?;
        require_finite("channel voltage shift (mV)", voltage_shift_mv)?;
        Ok(Self {
            surface_area,
            specific_capacitance,
            sodium_max_conductance_density,
            potassium_max_conductance_density,
            leak_conductance_density,
            sodium_reversal,
            potassium_reversal,
            leak_reversal,
            temperature_celsius,
            voltage_shift_mv,
            max_internal_step,
            sodium: SodiumChannelParameters::HUMAN_L23,
            potassium: PotassiumChannelParameters::HUMAN_L23,
        })
    }

    /// All-human-kinetics endpoint of the Wilbers et al. (2023) current-clamp
    /// conductance calibration grid.
    ///
    /// The conductance densities (114.47654963753565 and
    /// 29.045736151752504 pS/μm²) are the (Na ratio=1, K ratio=1) corner of
    /// the deposited 20×20 grid. The Powell objective still targets the
    /// 50:50 average of human and mouse median AP peak voltage, upstroke,
    /// and downstroke features. These are fitted model values, not direct
    /// human nucleated-patch conductance measurements or a human-only AP fit.
    /// The 10 μm × 10 μm cylinder, 34°C temperature, -10 mV channel shift,
    /// and +15 mV reversal-potential offsets reproduce the authors' current-
    /// clamp setup. The 20 μs maximum step matches their single-AP runner.
    pub fn wilbers_2023_human_l23_current_clamp_fit() -> Result<Self, SimulationError> {
        let area_um2 = std::f64::consts::PI * 10.0 * 10.0;
        Self::new(
            SquareMeters::from_square_micrometers(area_um2)?,
            FaradsPerSquareMeter::from_microfarads_per_square_centimeter(1.0)?,
            SiemensPerSquareMeter::from_picosiemens_per_square_micrometer(114.48)?,
            SiemensPerSquareMeter::from_picosiemens_per_square_micrometer(29.05)?,
            SiemensPerSquareMeter::from_picosiemens_per_square_micrometer(1.0)?,
            Volts::from_millivolts(68.0)?,
            Volts::from_millivolts(-86.0)?,
            Volts::from_millivolts(-70.0)?,
            34.0,
            -10.0,
            SimDuration::from_microseconds(20)?,
        )
    }

    pub const fn with_max_internal_step(mut self, duration: SimDuration) -> Self {
        self.max_internal_step = duration;
        self
    }

    pub const fn surface_area(self) -> SquareMeters {
        self.surface_area
    }

    pub const fn specific_capacitance(self) -> FaradsPerSquareMeter {
        self.specific_capacitance
    }

    pub const fn sodium_max_conductance_density(self) -> SiemensPerSquareMeter {
        self.sodium_max_conductance_density
    }

    pub const fn potassium_max_conductance_density(self) -> SiemensPerSquareMeter {
        self.potassium_max_conductance_density
    }

    pub const fn leak_conductance_density(self) -> SiemensPerSquareMeter {
        self.leak_conductance_density
    }

    pub const fn temperature_celsius(self) -> f64 {
        self.temperature_celsius
    }

    pub const fn max_internal_step(self) -> SimDuration {
        self.max_internal_step
    }

    pub fn sodium_temperature_factor(self) -> Result<f64, SimulationError> {
        temperature_factor(
            self.sodium.q10,
            self.temperature_celsius,
            self.sodium.reference_temperature_celsius,
        )
    }

    pub fn potassium_temperature_factor(self) -> Result<f64, SimulationError> {
        temperature_factor(
            self.potassium.q10,
            self.temperature_celsius,
            self.potassium.reference_temperature_celsius,
        )
    }

    fn sodium_rates(self, voltage_mv: f64) -> Result<SodiumRates, SimulationError> {
        let vm = voltage_mv + self.voltage_shift_mv;
        let vs = vm - self.sodium.inactivation_voltage_shift_mv;
        let factor = self.sodium_temperature_factor()?;

        let alpha_m = trap0(
            vm,
            self.sodium.activation_rate_half_voltage_mv,
            self.sodium.activation_rate,
            self.sodium.activation_rate_slope_mv,
        )?;
        let beta_m = trap0(
            -vm,
            -self.sodium.activation_rate_half_voltage_mv,
            self.sodium.activation_rate,
            self.sodium.activation_rate_slope_mv,
        )?;
        let tau_m = 1.0 / (factor * (alpha_m + beta_m));
        let m_inf = sigmoid(
            (vm - self.sodium.activation_half_voltage_mv) / self.sodium.activation_slope_mv,
        );

        let alpha_h = trap0(
            vs,
            self.sodium.inactivation_rate_half_voltage_mv,
            self.sodium.inactivation_rate,
            self.sodium.inactivation_rate_slope_mv,
        )?;
        let beta_h = trap0(
            -vs,
            -self.sodium.recovery_rate_half_voltage_mv,
            self.sodium.recovery_rate,
            self.sodium.recovery_rate_slope_mv,
        )?;
        let tau_h = 1.0 / (factor * (alpha_h + beta_h));
        let h_inf = sigmoid(
            (self.sodium.inactivation_half_voltage_mv - vs) / self.sodium.inactivation_slope_mv,
        );

        positive_time_constant("human sodium activation tau (ms)", tau_m)?;
        positive_time_constant("human sodium inactivation tau (ms)", tau_h)?;
        Ok(SodiumRates {
            activation: GateRates {
                steady_state: m_inf,
                time_constant_ms: tau_m,
            },
            inactivation: GateRates {
                steady_state: h_inf,
                time_constant_ms: tau_h,
            },
            temperature_factor: factor,
        })
    }

    fn potassium_rates(
        self,
        voltage_mv: f64,
        slow_gate: f64,
    ) -> Result<PotassiumRates, SimulationError> {
        let vm = voltage_mv + self.voltage_shift_mv;
        let factor = self.potassium_temperature_factor()?;

        let alpha_m = trap0(
            vm,
            self.potassium.activation_rate_half_voltage_mv,
            self.potassium.activation_rate,
            self.potassium.activation_rate_slope_mv,
        )?;
        let beta_m = trap0(
            -vm,
            -self.potassium.activation_rate_half_voltage_mv,
            self.potassium.activation_rate,
            self.potassium.activation_rate_slope_mv,
        )?;
        let tau_m = 1.0 / (factor * (alpha_m + beta_m));
        let m_inf = sigmoid(
            (vm - self.potassium.activation_half_voltage_mv) / self.potassium.activation_slope_mv,
        );

        let alpha_h = trap0(
            vm,
            self.potassium.inactivation_rate_half_voltage_mv,
            self.potassium.inactivation_rate,
            self.potassium.inactivation_rate_slope_mv,
        )?;
        let beta_h = trap0(
            -vm,
            -self.potassium.recovery_rate_half_voltage_mv,
            self.potassium.recovery_rate,
            self.potassium.recovery_rate_slope_mv,
        )?;
        let mut tau_h1 = 1.0 / (factor * (alpha_h + beta_h));
        let h_inf = sigmoid(
            (self.potassium.inactivation_half_voltage_mv - vm)
                / self.potassium.inactivation_slope_mv,
        );

        let tau_h2 = if h_inf > slow_gate {
            self.potassium.slow_recovery_time_constant_ms
        } else {
            tau_h1 /= self.potassium.inactivation_rate_factor;
            self.potassium.slow_inactivation_time_constant_ms
                / self.potassium.inactivation_rate_factor
        };

        positive_time_constant("human potassium activation tau (ms)", tau_m)?;
        positive_time_constant("human potassium fast-inactivation tau (ms)", tau_h1)?;
        positive_time_constant("human potassium slow-inactivation tau (ms)", tau_h2)?;
        Ok(PotassiumRates {
            activation: GateRates {
                steady_state: m_inf,
                time_constant_ms: tau_m,
            },
            fast_inactivation: GateRates {
                steady_state: h_inf,
                time_constant_ms: tau_h1,
            },
            slow_inactivation_time_constant_ms: tau_h2,
        })
    }

    fn derivatives(
        self,
        state: [f64; 6],
        injected_current: Amperes,
        current_balance: Option<&mut HumanL23SingleCompartmentCurrentBalance>,
    ) -> Result<[f64; 6], SimulationError> {
        let voltage_v = state[0];
        let voltage_mv = voltage_v * 1_000.0;
        let sodium = self.sodium_rates(voltage_mv)?;
        let potassium = self.potassium_rates(voltage_mv, state[5])?;
        let g_na = self
            .sodium_max_conductance_density
            .as_siemens_per_square_meter()
            * sodium.temperature_factor
            * state[1].powi(3)
            * state[2];
        let k_fast = state[4]
            * self.potassium.inactivating_fraction
            * (1.0 - self.potassium.slow_fraction_of_inactivating);
        let k_slow = state[5]
            * self.potassium.inactivating_fraction
            * self.potassium.slow_fraction_of_inactivating;
        let k_non_inactivating = 1.0 - self.potassium.inactivating_fraction;
        let g_k = self
            .potassium_max_conductance_density
            .as_siemens_per_square_meter()
            * state[3].powi(2)
            * (k_fast + k_slow + k_non_inactivating);
        let sodium_current_density = g_na * (voltage_v - self.sodium_reversal.as_volts());
        let potassium_current_density = g_k * (voltage_v - self.potassium_reversal.as_volts());
        let leak_current_density = self.leak_conductance_density.as_siemens_per_square_meter()
            * (voltage_v - self.leak_reversal.as_volts());
        let injected_current_density =
            injected_current.as_amperes() / self.surface_area.as_square_meters();
        let ionic_current_density =
            sodium_current_density + potassium_current_density + leak_current_density;
        let voltage_derivative = (injected_current_density - ionic_current_density)
            / self.specific_capacitance.as_farads_per_square_meter();
        let derivatives = [
            voltage_derivative,
            gate_derivative(sodium.activation, state[1]),
            gate_derivative(sodium.inactivation, state[2]),
            gate_derivative(potassium.activation, state[3]),
            gate_derivative(potassium.fast_inactivation, state[4]),
            (potassium.fast_inactivation.steady_state - state[5])
                / (potassium.slow_inactivation_time_constant_ms * 1.0e-3),
        ];
        for derivative in derivatives {
            require_finite("human single-compartment derivative", derivative)
                .map_err(|_| SimulationError::NumericalOverflow)?;
        }
        if let Some(balance) = current_balance {
            *balance = HumanL23SingleCompartmentCurrentBalance {
                sodium_current_density_a_per_m2: sodium_current_density,
                potassium_current_density_a_per_m2: potassium_current_density,
                leak_current_density_a_per_m2: leak_current_density,
                injected_current_density_a_per_m2: injected_current_density,
                voltage_derivative_v_per_s: voltage_derivative,
            };
        }
        Ok(derivatives)
    }

    fn initial_state(
        self,
        initial_voltage: Volts,
    ) -> Result<HumanL23SingleCompartmentRuntimeState, SimulationError> {
        let voltage_mv = initial_voltage.as_volts() * 1_000.0;
        let sodium = self.sodium_rates(voltage_mv)?;
        let potassium = self.potassium_rates(voltage_mv, 0.5)?;
        Ok(HumanL23SingleCompartmentRuntimeState {
            time: SimTime::ZERO,
            voltage: initial_voltage,
            sodium_activation: sodium.activation.steady_state,
            sodium_inactivation: sodium.inactivation.steady_state,
            potassium_activation: potassium.activation.steady_state,
            potassium_fast_inactivation: potassium.fast_inactivation.steady_state,
            potassium_slow_inactivation: potassium.fast_inactivation.steady_state,
        })
    }
}

/// Initial voltage for a human single-compartment simulation.
///
/// Channel gates are initialized at their model steady states at this voltage.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct HumanL23SingleCompartmentInitialConditions {
    voltage: Volts,
}

impl HumanL23SingleCompartmentInitialConditions {
    pub const fn new(voltage: Volts) -> Self {
        Self { voltage }
    }

    pub const fn voltage(self) -> Volts {
        self.voltage
    }
}

/// Live voltage and channel-gate state of the single-compartment model.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct HumanL23SingleCompartmentRuntimeState {
    time: SimTime,
    voltage: Volts,
    sodium_activation: f64,
    sodium_inactivation: f64,
    potassium_activation: f64,
    potassium_fast_inactivation: f64,
    potassium_slow_inactivation: f64,
}

impl HumanL23SingleCompartmentRuntimeState {
    pub const fn time(self) -> SimTime {
        self.time
    }

    pub const fn voltage(self) -> Volts {
        self.voltage
    }

    pub const fn sodium_activation(self) -> f64 {
        self.sodium_activation
    }

    pub const fn sodium_inactivation(self) -> f64 {
        self.sodium_inactivation
    }

    pub const fn potassium_activation(self) -> f64 {
        self.potassium_activation
    }

    pub const fn potassium_fast_inactivation(self) -> f64 {
        self.potassium_fast_inactivation
    }

    pub const fn potassium_slow_inactivation(self) -> f64 {
        self.potassium_slow_inactivation
    }

    fn as_array(self) -> [f64; 6] {
        [
            self.voltage.as_volts(),
            self.sodium_activation,
            self.sodium_inactivation,
            self.potassium_activation,
            self.potassium_fast_inactivation,
            self.potassium_slow_inactivation,
        ]
    }

    fn from_array(time: SimTime, values: [f64; 6]) -> Result<Self, SimulationError> {
        for (name, gate) in [
            ("sodium activation gate", values[1]),
            ("sodium inactivation gate", values[2]),
            ("potassium activation gate", values[3]),
            ("potassium fast-inactivation gate", values[4]),
            ("potassium slow-inactivation gate", values[5]),
        ] {
            require_finite(name, gate).map_err(|_| SimulationError::NumericalOverflow)?;
            if !(0.0..=1.0).contains(&gate) {
                return Err(SimulationError::NumericalOverflow);
            }
        }
        Ok(Self {
            time,
            voltage: Volts::from_volts(values[0])
                .map_err(|_| SimulationError::NumericalOverflow)?,
            sodium_activation: values[1],
            sodium_inactivation: values[2],
            potassium_activation: values[3],
            potassium_fast_inactivation: values[4],
            potassium_slow_inactivation: values[5],
        })
    }
}

/// CPU simulation of one human L2/L3 single-compartment compartment.
#[derive(Debug, Clone, PartialEq)]
pub struct HumanL23SingleCompartmentSimulation {
    model: HumanL23SingleCompartmentModel,
    initial_conditions: HumanL23SingleCompartmentInitialConditions,
    initial_state: HumanL23SingleCompartmentRuntimeState,
    state: HumanL23SingleCompartmentRuntimeState,
}

impl HumanL23SingleCompartmentSimulation {
    pub fn new(
        model: HumanL23SingleCompartmentModel,
        initial_conditions: HumanL23SingleCompartmentInitialConditions,
    ) -> Result<Self, SimulationError> {
        let initial_state = model.initial_state(initial_conditions.voltage)?;
        Ok(Self {
            model,
            initial_conditions,
            initial_state,
            state: initial_state,
        })
    }

    pub const fn model(&self) -> HumanL23SingleCompartmentModel {
        self.model
    }

    pub const fn initial_conditions(&self) -> HumanL23SingleCompartmentInitialConditions {
        self.initial_conditions
    }

    pub const fn state(&self) -> HumanL23SingleCompartmentRuntimeState {
        self.state
    }

    /// Evaluate the current balance at the committed live state without advancing time.
    pub fn current_balance(
        &self,
        injected_current: Amperes,
    ) -> Result<HumanL23SingleCompartmentCurrentBalance, SimulationError> {
        let mut balance = HumanL23SingleCompartmentCurrentBalance::ZERO;
        self.model
            .derivatives(self.state.as_array(), injected_current, Some(&mut balance))?;
        Ok(balance)
    }

    /// Advance one fixed RK4 step and return the four voltage values actually
    /// supplied to the coupled derivative evaluations.
    ///
    /// The returned stages are ordered as (k1, k2, k3, k4), at the RK4
    /// evaluation times t, t + dt/2, t + dt/2, and t + dt. They are the
    /// voltage components of the exact intermediate state vectors used by
    /// this step, not endpoint interpolation estimates.
    ///
    /// This diagnostic form advances the simulation identically to step().
    /// It is intended for numerical attribution and reproducibility, not as
    /// a separate integration method.
    pub fn step_with_voltage_stages(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<(HumanL23SingleCompartmentRuntimeState, [Volts; 4]), SimulationError> {
        let mut voltage_stages = [Volts::from_volts(0.0)?; 4];
        let state =
            self.integrate_step(duration, injected_current, Some(&mut voltage_stages), None)?;
        Ok((state, voltage_stages))
    }

    /// Advance one RK4 step and expose the four coupled voltage and current stages.
    /// Current densities are A/m²; voltage derivatives are V/s.
    pub fn step_with_voltage_and_current_stages(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<
        (
            HumanL23SingleCompartmentRuntimeState,
            [Volts; 4],
            [HumanL23SingleCompartmentCurrentBalance; 4],
        ),
        SimulationError,
    > {
        let mut voltage_stages = [Volts::from_volts(0.0)?; 4];
        let mut current_stages = [HumanL23SingleCompartmentCurrentBalance::ZERO; 4];
        let state = self.integrate_step(
            duration,
            injected_current,
            Some(&mut voltage_stages),
            Some(&mut current_stages),
        )?;
        Ok((state, voltage_stages, current_stages))
    }

    /// Advance one RK4 step and expose current balance at its four derivative stages.
    /// Current densities are A/m²; voltage derivatives are V/s.
    pub fn step_with_current_balance_stages(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<
        (
            HumanL23SingleCompartmentRuntimeState,
            [HumanL23SingleCompartmentCurrentBalance; 4],
        ),
        SimulationError,
    > {
        let mut current_stages = [HumanL23SingleCompartmentCurrentBalance::ZERO; 4];
        let state =
            self.integrate_step(duration, injected_current, None, Some(&mut current_stages))?;
        Ok((state, current_stages))
    }

    /// Advance one fixed RK4 step with constant injected current.
    ///
    /// The duration must not exceed the model's configured maximum internal
    /// step. The full step is transactional: clock, voltage and gates are
    /// committed only if all six state variables remain finite and bounded.
    pub fn step(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
    ) -> Result<HumanL23SingleCompartmentRuntimeState, SimulationError> {
        self.integrate_step(duration, injected_current, None, None)
    }

    fn integrate_step(
        &mut self,
        duration: SimDuration,
        injected_current: Amperes,
        voltage_stages: Option<&mut [Volts; 4]>,
        mut current_stages: Option<&mut [HumanL23SingleCompartmentCurrentBalance; 4]>,
    ) -> Result<HumanL23SingleCompartmentRuntimeState, SimulationError> {
        if duration.as_nanoseconds() > self.model.max_internal_step.as_nanoseconds() {
            return Err(SimulationError::OutOfRangeValue {
                field: "single-compartment integration step (ns)",
                value: duration.as_nanoseconds() as f64,
                minimum: 1.0,
                maximum: self.model.max_internal_step.as_nanoseconds() as f64,
            });
        }

        let next_time = self.state.time.checked_add(duration)?;
        let dt = duration.as_seconds();
        let y = self.state.as_array();
        let stage_1 = y;
        let k1 = if let Some(stages) = current_stages.as_mut() {
            self.model
                .derivatives(stage_1, injected_current, Some(&mut stages[0]))?
        } else {
            self.model.derivatives(stage_1, injected_current, None)?
        };
        let stage_2 = add_scaled(y, k1, dt * 0.5);
        let k2 = if let Some(stages) = current_stages.as_mut() {
            self.model
                .derivatives(stage_2, injected_current, Some(&mut stages[1]))?
        } else {
            self.model.derivatives(stage_2, injected_current, None)?
        };
        let stage_3 = add_scaled(y, k2, dt * 0.5);
        let k3 = if let Some(stages) = current_stages.as_mut() {
            self.model
                .derivatives(stage_3, injected_current, Some(&mut stages[2]))?
        } else {
            self.model.derivatives(stage_3, injected_current, None)?
        };
        let stage_4 = add_scaled(y, k3, dt);
        let k4 = if let Some(stages) = current_stages.as_mut() {
            self.model
                .derivatives(stage_4, injected_current, Some(&mut stages[3]))?
        } else {
            self.model.derivatives(stage_4, injected_current, None)?
        };
        if let Some(stages) = voltage_stages {
            *stages = [
                Volts::from_volts(stage_1[0])?,
                Volts::from_volts(stage_2[0])?,
                Volts::from_volts(stage_3[0])?,
                Volts::from_volts(stage_4[0])?,
            ];
        }
        let next = std::array::from_fn(|index| {
            y[index] + dt * (k1[index] + 2.0 * k2[index] + 2.0 * k3[index] + k4[index]) / 6.0
        });
        for value in next {
            require_finite("single-compartment integrated state", value)
                .map_err(|_| SimulationError::NumericalOverflow)?;
        }
        let next_state = HumanL23SingleCompartmentRuntimeState::from_array(next_time, next)?;
        self.state = next_state;
        Ok(next_state)
    }

    pub fn reset(&mut self) {
        self.state = self.initial_state;
    }
}

fn add_scaled(state: [f64; 6], derivative: [f64; 6], scale: f64) -> [f64; 6] {
    std::array::from_fn(|index| state[index] + derivative[index] * scale)
}

fn gate_derivative(rates: GateRates, gate: f64) -> f64 {
    (rates.steady_state - gate) / (rates.time_constant_ms * 1.0e-3)
}

fn positive_time_constant(field: &'static str, value: f64) -> Result<(), SimulationError> {
    require_positive(field, value).map_err(|_| SimulationError::NumericalOverflow)
}

fn temperature_factor(
    q10: f64,
    temperature_celsius: f64,
    reference_temperature_celsius: f64,
) -> Result<f64, SimulationError> {
    let factor = q10.powf((temperature_celsius - reference_temperature_celsius) / 10.0);
    require_positive("channel temperature factor", factor)
        .map_err(|_| SimulationError::NumericalOverflow)?;
    Ok(factor)
}

fn sigmoid(value: f64) -> f64 {
    if value >= 0.0 {
        let exp = (-value).exp();
        1.0 / (1.0 + exp)
    } else {
        let exp = value.exp();
        exp / (1.0 + exp)
    }
}

/// Stable form of the author-deposited trap0 rate function.
///
/// The source's denominator is singular at v = theta, but its branch test
/// checks v + theta and its fallback omits the prefactor. The mathematical
/// limit at the true singularity is prefactor × slope. This implementation
/// uses exp_m1 near zero and asymptotic branches at large arguments.
fn trap0(
    voltage_mv: f64,
    half_voltage_mv: f64,
    prefactor: RatePrefactor,
    slope_mv: f64,
) -> Result<f64, SimulationError> {
    require_finite("trap0 voltage (mV)", voltage_mv)?;
    require_finite("trap0 half-voltage (mV)", half_voltage_mv)?;
    require_positive("trap0 slope (mV)", slope_mv)?;
    require_positive(
        "trap0 rate prefactor (mV^-1 ms^-1)",
        prefactor.per_millivolt_per_ms,
    )?;

    let x = (voltage_mv - half_voltage_mv) / slope_mv;
    let ratio = if x.abs() < 1.0e-5 {
        1.0 + x / 2.0 + x * x / 12.0 - x.powi(4) / 720.0
    } else if x > 50.0 {
        x
    } else if x < -50.0 {
        -x * x.exp()
    } else {
        x / -(-x).exp_m1()
    };
    let rate = prefactor.per_millivolt_per_ms * slope_mv * ratio;
    require_positive("trap0 transition rate (ms^-1)", rate)
        .map_err(|_| SimulationError::NumericalOverflow)?;
    Ok(rate)
}

#[cfg(test)]
mod tests {
    use super::{
        trap0, GateRates, HumanL23SingleCompartmentInitialConditions,
        HumanL23SingleCompartmentModel, HumanL23SingleCompartmentSimulation,
        PotassiumChannelParameters, RatePrefactor,
    };
    use crate::{Amperes, SimDuration, SimTime, SimulationError, Volts};

    fn wilbers_model() -> super::HumanL23SingleCompartmentModel {
        super::HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit().unwrap()
    }

    type SourceApFeatureMetrics = (f64, f64, f64, f64);
    type SourceApReplay = (f64, Option<SourceApFeatureMetrics>, usize);

    #[test]
    fn rk4_voltage_stage_diagnostics_match_the_actual_intermediate_states() {
        let model = wilbers_model();
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let mut diagnostic = HumanL23SingleCompartmentSimulation::new(model, initial).unwrap();
        let mut ordinary = diagnostic.clone();
        let duration = SimDuration::from_microseconds(20).unwrap();
        let current = Amperes::from_picoamperes(30.0).unwrap();

        let y = diagnostic.state.as_array();
        let dt = duration.as_seconds();
        let k1 = model.derivatives(y, current, None).unwrap();
        let stage_2 = super::add_scaled(y, k1, dt * 0.5);
        let k2 = model.derivatives(stage_2, current, None).unwrap();
        let stage_3 = super::add_scaled(y, k2, dt * 0.5);
        let k3 = model.derivatives(stage_3, current, None).unwrap();
        let stage_4 = super::add_scaled(y, k3, dt);

        let (diagnostic_state, voltage_stages, current_stages) = diagnostic
            .step_with_voltage_and_current_stages(duration, current)
            .unwrap();
        let ordinary_state = ordinary.step(duration, current).unwrap();
        let state_before_query = diagnostic.state();
        let endpoint_balance = diagnostic
            .current_balance(Amperes::from_amperes(0.0).unwrap())
            .unwrap();

        assert_eq!(diagnostic.state(), state_before_query);
        assert!(endpoint_balance.voltage_derivative_v_per_s().is_finite());
        assert_eq!(diagnostic_state, ordinary_state);
        assert_eq!(diagnostic_state, diagnostic.state());
        assert_eq!(
            voltage_stages,
            [
                Volts::from_volts(y[0]).unwrap(),
                Volts::from_volts(stage_2[0]).unwrap(),
                Volts::from_volts(stage_3[0]).unwrap(),
                Volts::from_volts(stage_4[0]).unwrap(),
            ]
        );

        for balance in current_stages {
            let residual = model.specific_capacitance.as_farads_per_square_meter()
                * balance.voltage_derivative_v_per_s()
                + balance.total_ionic_current_density_a_per_m2()
                - balance.injected_current_density_a_per_m2();
            assert!(residual.abs() < 1.0e-12);
        }
        let weighted_voltage_change = dt / 6.0
            * (current_stages[0].voltage_derivative_v_per_s()
                + 2.0 * current_stages[1].voltage_derivative_v_per_s()
                + 2.0 * current_stages[2].voltage_derivative_v_per_s()
                + current_stages[3].voltage_derivative_v_per_s());
        let actual_voltage_change = diagnostic_state.voltage().as_volts() - y[0];
        assert!((weighted_voltage_change - actual_voltage_change).abs() < 1.0e-14);
    }

    fn source_rheobase_trial_spikes(current_pa: f64) -> bool {
        let model =
            wilbers_model().with_max_internal_step(SimDuration::from_microseconds(100).unwrap());
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial).unwrap();
        let dt = SimDuration::from_microseconds(100).unwrap();
        let current = Amperes::from_picoamperes(current_pa).unwrap();
        let zero = Amperes::from_amperes(0.0).unwrap();
        let threshold = Volts::from_millivolts(-20.0).unwrap();

        // Source getrheo: 7 ms total, 3-ms pulse after a 2-ms delay.
        for index in 0..70 {
            let before = simulation.state().voltage();
            let injected = if (20..50).contains(&index) {
                current
            } else {
                zero
            };
            let after = simulation.step(dt, injected).unwrap().voltage();
            if before.as_volts() < threshold.as_volts() && after.as_volts() >= threshold.as_volts()
            {
                return true;
            }
        }
        false
    }

    fn source_protocol_rheobase_pa() -> f64 {
        // The deposited helper first runs the initial 0.1-nA stimulus before
        // entering its 0.1/0.01/0.001-nA increment phases.
        let mut current_pa = 100.0;
        let mut found = source_rheobase_trial_spikes(current_pa);

        for increment_pa in [100.0, 10.0, 1.0] {
            let mut attempts = 0;
            while !found && attempts < 200 {
                current_pa += increment_pa;
                assert!(
                    current_pa <= 20_000.0,
                    "source-protocol rheobase search exceeded the safe 20-nA bound"
                );
                found = source_rheobase_trial_spikes(current_pa);
                attempts += 1;
            }
            assert!(found, "source-protocol rheobase search did not converge");

            // The source backs off after coarse/medium phases and resets APCount.
            if increment_pa > 1.0 {
                current_pa -= increment_pa;
                found = false;
            }
        }
        current_pa.round()
    }

    fn source_current_clamp_ap_features(rheobase_pa: f64) -> SourceApReplay {
        let model = wilbers_model();
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial).unwrap();
        let dt = SimDuration::from_microseconds(20).unwrap();
        let current = Amperes::from_picoamperes(rheobase_pa * 1.5).unwrap();
        let zero = Amperes::from_amperes(0.0).unwrap();
        let threshold = Volts::from_millivolts(-20.0).unwrap();
        let mut trace = Vec::with_capacity(1_450);
        let mut threshold_crossings = 0;

        // Source run_1AP: 29 ms total, 3-ms pulse after a 1-ms delay.
        for index in 0..1_450 {
            let before = simulation.state().voltage();
            let injected = if (50..200).contains(&index) {
                current
            } else {
                zero
            };
            let after = simulation.step(dt, injected).unwrap().voltage();
            if before.as_volts() < threshold.as_volts() && after.as_volts() >= threshold.as_volts()
            {
                threshold_crossings += 1;
            }
            trace.push(after.as_volts() * 1_000.0);
        }

        let peak_index = trace
            .iter()
            .enumerate()
            .max_by(|left, right| left.1.total_cmp(right.1))
            .unwrap()
            .0;
        let window_start = peak_index.saturating_sub(49);
        let window_end = (peak_index + 150).min(trace.len());
        let window = &trace[window_start..window_end];
        let derivatives: Vec<f64> = window
            .windows(2)
            .map(|pair| (pair[1] - pair[0]) / 0.02)
            .collect();
        let peak_local_index = window
            .iter()
            .enumerate()
            .max_by(|left, right| left.1.total_cmp(right.1))
            .unwrap()
            .0;
        let max_derivative_index = derivatives
            .iter()
            .enumerate()
            .max_by(|left, right| left.1.total_cmp(right.1))
            .unwrap()
            .0;
        let Some(threshold_index) = derivatives[..max_derivative_index]
            .iter()
            .rposition(|rate| *rate < 40.0)
            .map(|index| index + 1)
        else {
            // Preserve the source extractor's undefined case as an explicit
            // result. Do not substitute a threshold or relax its 40-mV/ms rule.
            return (window[peak_local_index], None, threshold_crossings);
        };
        let spike_threshold = window[threshold_index];
        let peak = window[peak_local_index];
        let amplitude = peak;
        let up_v = &window[..peak_local_index];
        let up_30 = up_v
            .iter()
            .rposition(|voltage| *voltage < spike_threshold + (amplitude - spike_threshold) * 0.3)
            .unwrap()
            + 1;
        let up_70 = up_v
            .iter()
            .rposition(|voltage| *voltage < spike_threshold + (amplitude - spike_threshold) * 0.7)
            .unwrap()
            + 1;
        let upstroke = derivatives[up_30..up_70].iter().sum::<f64>() / (up_70 - up_30) as f64;

        let down_v = &window[peak_local_index..];
        let down_30 = peak_local_index
            + down_v
                .iter()
                .rposition(|voltage| {
                    *voltage > spike_threshold + (amplitude - spike_threshold) * 0.7
                })
                .unwrap()
            + 1;
        let down_70 = peak_local_index
            + down_v
                .iter()
                .rposition(|voltage| {
                    *voltage > spike_threshold + (amplitude - spike_threshold) * 0.3
                })
                .unwrap()
            + 1;
        let downstroke =
            derivatives[down_30..down_70].iter().sum::<f64>() / (down_70 - down_30) as f64;
        let ahp_end = (peak_index + 1_250).min(trace.len());
        let ahp = trace[peak_index + 1..ahp_end]
            .iter()
            .copied()
            .fold(f64::INFINITY, f64::min);

        (
            amplitude,
            Some((spike_threshold, upstroke, downstroke, ahp)),
            threshold_crossings,
        )
    }

    #[derive(Debug, Clone, Copy)]
    struct PotassiumClampGates {
        activation: f64,
        fast_inactivation: f64,
        slow_inactivation: f64,
    }

    fn wilbers_voltage_clamp_model() -> HumanL23SingleCompartmentModel {
        let mut model = wilbers_model();
        // The deposited K+ voltage-clamp fitting cell leaves vshift at its NMODL default (0 mV).
        model.voltage_shift_mv = 0.0;
        // The deposited voltage-clamp helper initializes EK to -101 mV.
        model.potassium_reversal = Volts::from_millivolts(-101.0).unwrap();
        model
    }

    fn wilbers_mouse_voltage_clamp_model() -> HumanL23SingleCompartmentModel {
        let mut model = wilbers_voltage_clamp_model();
        // Pure k_mouse.mod values from Dataverse file 318560. Its current is
        // scaled by (1 - human_ratio); that common amplitude does not affect
        // the normalized current time-constant fits reproduced in these tests.
        model.potassium = PotassiumChannelParameters {
            activation_half_voltage_mv: -24.922394891493052,
            activation_slope_mv: 17.95852797022577,
            activation_rate_half_voltage_mv: -17.107947829817025,
            activation_rate_slope_mv: 3.6884191311479615,
            activation_rate: RatePrefactor {
                per_millivolt_per_ms: 0.0167,
            },
            inactivation_half_voltage_mv: -65.2,
            inactivation_slope_mv: 12.1,
            inactivation_rate_half_voltage_mv: 40.5659148938157,
            recovery_rate_half_voltage_mv: -75.93822659307075,
            inactivation_rate_slope_mv: 26.773929244740913,
            recovery_rate_slope_mv: 0.40183382749400054,
            inactivation_rate: RatePrefactor {
                per_millivolt_per_ms: 0.0016901435659310753,
            },
            recovery_rate: RatePrefactor {
                per_millivolt_per_ms: 0.0004968791312639546,
            },
            slow_inactivation_time_constant_ms: 450.0,
            slow_recovery_time_constant_ms: 2789.7929428108187,
            inactivating_fraction: 0.85,
            slow_fraction_of_inactivating: 0.4,
            inactivation_rate_factor: 1.0,
            reference_temperature_celsius: 34.0,
            q10: 2.3,
        };
        model
    }

    fn initial_potassium_clamp_gates(
        model: HumanL23SingleCompartmentModel,
        voltage_mv: f64,
    ) -> PotassiumClampGates {
        let rates = model.potassium_rates(voltage_mv, 0.5).unwrap();
        PotassiumClampGates {
            activation: rates.activation.steady_state,
            fast_inactivation: rates.fast_inactivation.steady_state,
            slow_inactivation: rates.fast_inactivation.steady_state,
        }
    }

    fn advance_k_clamp_step(
        model: HumanL23SingleCompartmentModel,
        gates: &mut PotassiumClampGates,
        voltage_mv: f64,
        step_ms: f64,
    ) -> f64 {
        let rates = model
            .potassium_rates(voltage_mv, gates.slow_inactivation)
            .unwrap();
        let advance_gate = |gate: f64, gate_rates: GateRates| {
            gate_rates.steady_state
                + (gate - gate_rates.steady_state) * (-step_ms / gate_rates.time_constant_ms).exp()
        };
        gates.activation = advance_gate(gates.activation, rates.activation);
        gates.fast_inactivation = advance_gate(gates.fast_inactivation, rates.fast_inactivation);
        gates.slow_inactivation = advance_gate(
            gates.slow_inactivation,
            GateRates {
                steady_state: rates.fast_inactivation.steady_state,
                time_constant_ms: rates.slow_inactivation_time_constant_ms,
            },
        );

        let fast_fraction = model.potassium.inactivating_fraction
            * (1.0 - model.potassium.slow_fraction_of_inactivating);
        let slow_fraction =
            model.potassium.inactivating_fraction * model.potassium.slow_fraction_of_inactivating;
        let non_inactivating_fraction = 1.0 - model.potassium.inactivating_fraction;
        gates.activation.powi(2)
            * (gates.fast_inactivation * fast_fraction
                + gates.slow_inactivation * slow_fraction
                + non_inactivating_fraction)
    }

    fn advance_k_clamp(
        model: HumanL23SingleCompartmentModel,
        gates: &mut PotassiumClampGates,
        voltage_mv: f64,
        duration_ms: f64,
        step_ms: f64,
    ) -> f64 {
        let steps = (duration_ms / step_ms).round() as usize;
        let mut peak_conductance = 0.0_f64;
        for _ in 0..steps {
            peak_conductance =
                peak_conductance.max(advance_k_clamp_step(model, gates, voltage_mv, step_ms));
        }
        peak_conductance
    }

    fn replay_k_activation_current(
        model: HumanL23SingleCompartmentModel,
        test_voltage_mv: f64,
    ) -> Vec<f64> {
        let mut gates = initial_potassium_clamp_gates(model, -140.0);
        advance_k_clamp(model, &mut gates, -140.0, 20.0, 0.1);
        let reversal_mv = model.potassium_reversal.as_volts() * 1_000.0;
        let mut current = Vec::with_capacity(4_995);
        let mut time_ms = 20.0;
        for _ in 1..=5_000 {
            // Accumulate like NEURON's h.t; nominal 20.4 ms rounds above the strict source mask.
            time_ms += 0.1;
            let conductance = advance_k_clamp_step(model, &mut gates, test_voltage_mv, 0.1);
            if time_ms > 20.4 && time_ms < 520.0 {
                current.push(conductance * (test_voltage_mv - reversal_mv));
            }
        }
        current
    }

    fn exponential_fit_sse(log_tau: f64, times_ms: &[f64], values: &[f64], mean_value: f64) -> f64 {
        let tau_ms = log_tau.exp();
        let exponentials: Vec<f64> = times_ms.iter().map(|time| (-time / tau_ms).exp()).collect();
        let mean_exponential = exponentials.iter().sum::<f64>() / exponentials.len() as f64;
        let variance = exponentials
            .iter()
            .map(|value| (value - mean_exponential).powi(2))
            .sum::<f64>();
        if variance <= f64::EPSILON {
            return f64::INFINITY;
        }
        let covariance = exponentials
            .iter()
            .zip(values)
            .map(|(exponential, value)| (exponential - mean_exponential) * (value - mean_value))
            .sum::<f64>();
        let amplitude = covariance / variance;
        let offset = mean_value - amplitude * mean_exponential;
        exponentials
            .iter()
            .zip(values)
            .map(|(exponential, value)| (value - (amplitude * exponential + offset)).powi(2))
            .sum()
    }

    fn fit_exponential_offset_tau(times_ms: &[f64], values: &[f64]) -> Option<(f64, f64)> {
        if times_ms.len() != values.len() || times_ms.len() < 4 {
            return None;
        }
        let mean_value = values.iter().sum::<f64>() / values.len() as f64;
        let total_sum_squares = values
            .iter()
            .map(|value| (value - mean_value).powi(2))
            .sum::<f64>();
        if total_sum_squares <= f64::EPSILON {
            return None;
        }

        const GRID_STEPS: usize = 256;
        let minimum_log_tau = 0.01_f64.ln();
        let maximum_log_tau = 100.0_f64.ln();
        let log_step = (maximum_log_tau - minimum_log_tau) / GRID_STEPS as f64;
        let mut best_index = 0;
        let mut best_error = f64::INFINITY;
        for index in 0..=GRID_STEPS {
            let log_tau = minimum_log_tau + index as f64 * log_step;
            let error = exponential_fit_sse(log_tau, times_ms, values, mean_value);
            if error < best_error {
                best_error = error;
                best_index = index;
            }
        }

        let mut left = minimum_log_tau + best_index.saturating_sub(1) as f64 * log_step;
        let mut right = minimum_log_tau + (best_index + 1).min(GRID_STEPS) as f64 * log_step;
        let golden_ratio = (5.0_f64.sqrt() - 1.0) / 2.0;
        let mut c = right - golden_ratio * (right - left);
        let mut d = left + golden_ratio * (right - left);
        let mut fc = exponential_fit_sse(c, times_ms, values, mean_value);
        let mut fd = exponential_fit_sse(d, times_ms, values, mean_value);
        for _ in 0..80 {
            if fc < fd {
                right = d;
                d = c;
                fd = fc;
                c = right - golden_ratio * (right - left);
                fc = exponential_fit_sse(c, times_ms, values, mean_value);
            } else {
                left = c;
                c = d;
                fc = fd;
                d = left + golden_ratio * (right - left);
                fd = exponential_fit_sse(d, times_ms, values, mean_value);
            }
        }

        let log_tau = (left + right) * 0.5;
        let residual_sum_squares = exponential_fit_sse(log_tau, times_ms, values, mean_value);
        let r_squared = 1.0 - residual_sum_squares / total_sum_squares;
        Some((log_tau.exp(), r_squared))
    }

    fn fit_k_activation_current_tau(current: &[f64], step_ms: f64) -> Option<(f64, f64)> {
        // Match numpy.argmax: choose the first sample when the peak is tied.
        let mut peak_index = 0;
        for (index, value) in current.iter().enumerate().skip(1) {
            if value > &current[peak_index] {
                peak_index = index;
            }
        }
        if peak_index < 4 {
            return None;
        }
        let last_before_peak = current[peak_index - 1];
        let times: Vec<f64> = (0..peak_index)
            .map(|index| index as f64 * step_ms)
            .collect();
        let values: Vec<f64> = current[..peak_index]
            .iter()
            .map(|value| value - last_before_peak)
            .collect();
        fit_exponential_offset_tau(&times, &values)
    }

    fn solve_three_coefficients(mut matrix: [[f64; 4]; 3]) -> Option<[f64; 3]> {
        for column in 0..3 {
            let pivot = (column..3).max_by(|left, right| {
                matrix[*left][column]
                    .abs()
                    .total_cmp(&matrix[*right][column].abs())
            })?;
            if matrix[pivot][column].abs() <= 1.0e-14 {
                return None;
            }
            matrix.swap(column, pivot);
            let divisor = matrix[column][column];
            for value in matrix[column].iter_mut().skip(column) {
                *value /= divisor;
            }
            let pivot_row = matrix[column];
            for (row_index, row_values) in matrix.iter_mut().enumerate() {
                if row_index == column {
                    continue;
                }
                let factor = row_values[column];
                for (value, pivot_value) in row_values.iter_mut().zip(pivot_row).skip(column) {
                    *value -= factor * pivot_value;
                }
            }
        }
        Some([matrix[0][3], matrix[1][3], matrix[2][3]])
    }

    fn biexponential_fixed_tau2_sse(
        log_tau1: f64,
        times_ms: &[f64],
        values: &[f64],
        tau2_ms: f64,
    ) -> f64 {
        let tau1_ms = log_tau1.exp();
        let mut sum_e1_squared = 0.0;
        let mut sum_e2_squared = 0.0;
        let mut sum_e1_e2 = 0.0;
        let mut sum_e1 = 0.0;
        let mut sum_e2 = 0.0;
        let mut sum_y = 0.0;
        let mut sum_e1_y = 0.0;
        let mut sum_e2_y = 0.0;
        for (time, value) in times_ms.iter().zip(values) {
            let e1 = (-time / tau1_ms).exp();
            let e2 = (-time / tau2_ms).exp();
            sum_e1_squared += e1 * e1;
            sum_e2_squared += e2 * e2;
            sum_e1_e2 += e1 * e2;
            sum_e1 += e1;
            sum_e2 += e2;
            sum_y += value;
            sum_e1_y += e1 * value;
            sum_e2_y += e2 * value;
        }
        let count = values.len() as f64;
        let coefficients = solve_three_coefficients([
            [sum_e1_squared, sum_e1_e2, sum_e1, sum_e1_y],
            [sum_e1_e2, sum_e2_squared, sum_e2, sum_e2_y],
            [sum_e1, sum_e2, count, sum_y],
        ]);
        let Some([amplitude1, amplitude2, offset]) = coefficients else {
            return f64::INFINITY;
        };
        if amplitude1 < 0.0 || amplitude2 < 0.0 || offset < 0.0 {
            return f64::INFINITY;
        }
        times_ms
            .iter()
            .zip(values)
            .map(|(time, value)| {
                let prediction = amplitude1 * (-time / tau1_ms).exp()
                    + amplitude2 * (-time / tau2_ms).exp()
                    + offset;
                (value - prediction).powi(2)
            })
            .sum()
    }

    fn fit_biexponential_fixed_tau2(
        times_ms: &[f64],
        values: &[f64],
        tau2_ms: f64,
    ) -> Option<(f64, f64)> {
        if times_ms.len() != values.len() || values.len() < 5 || tau2_ms <= 0.0 {
            return None;
        }
        let mean_value = values.iter().sum::<f64>() / values.len() as f64;
        let total_sum_squares = values
            .iter()
            .map(|value| (value - mean_value).powi(2))
            .sum::<f64>();
        if total_sum_squares <= f64::EPSILON {
            return None;
        }

        const GRID_STEPS: usize = 256;
        let minimum_log_tau = 0.01_f64.ln();
        let maximum_log_tau = 300.0_f64.ln();
        let log_step = (maximum_log_tau - minimum_log_tau) / GRID_STEPS as f64;
        let mut best_index = 0;
        let mut best_error = f64::INFINITY;
        for index in 0..=GRID_STEPS {
            let log_tau = minimum_log_tau + index as f64 * log_step;
            let error = biexponential_fixed_tau2_sse(log_tau, times_ms, values, tau2_ms);
            if error < best_error {
                best_error = error;
                best_index = index;
            }
        }

        let mut left = minimum_log_tau + best_index.saturating_sub(1) as f64 * log_step;
        let mut right = minimum_log_tau + (best_index + 1).min(GRID_STEPS) as f64 * log_step;
        let golden_ratio = (5.0_f64.sqrt() - 1.0) / 2.0;
        let mut c = right - golden_ratio * (right - left);
        let mut d = left + golden_ratio * (right - left);
        let mut fc = biexponential_fixed_tau2_sse(c, times_ms, values, tau2_ms);
        let mut fd = biexponential_fixed_tau2_sse(d, times_ms, values, tau2_ms);
        for _ in 0..80 {
            if fc < fd {
                right = d;
                d = c;
                fd = fc;
                c = right - golden_ratio * (right - left);
                fc = biexponential_fixed_tau2_sse(c, times_ms, values, tau2_ms);
            } else {
                left = c;
                c = d;
                fc = fd;
                d = left + golden_ratio * (right - left);
                fd = biexponential_fixed_tau2_sse(d, times_ms, values, tau2_ms);
            }
        }

        let log_tau = (left + right) * 0.5;
        let residual_sum_squares = biexponential_fixed_tau2_sse(log_tau, times_ms, values, tau2_ms);
        let r_squared = 1.0 - residual_sum_squares / total_sum_squares;
        Some((log_tau.exp(), r_squared))
    }

    fn replay_k_recovery_peak_currents(
        model: HumanL23SingleCompartmentModel,
        recovery_voltage_mv: f64,
        recovery_delays_ms: &[f64],
    ) -> Vec<f64> {
        let reversal_mv = model.potassium_reversal.as_volts() * 1_000.0;
        recovery_delays_ms
            .iter()
            .map(|delay_ms| {
                let mut gates = initial_potassium_clamp_gates(model, -120.0);
                advance_k_clamp(model, &mut gates, -120.0, 2.0, 0.5);
                advance_k_clamp(model, &mut gates, 40.0, 5_000.0, 0.5);
                advance_k_clamp(model, &mut gates, recovery_voltage_mv, *delay_ms, 0.5);
                let mut peak_current = 0.0_f64;
                for _ in 0..10 {
                    let conductance = advance_k_clamp_step(model, &mut gates, 40.0, 0.5);
                    peak_current = peak_current.max(conductance * (40.0 - reversal_mv));
                }
                peak_current
            })
            .collect()
    }

    fn recovery_biexponential_sse(
        log_tau1: f64,
        log_tau2: f64,
        times_ms: &[f64],
        values: &[f64],
    ) -> f64 {
        let tau1_ms = log_tau1.exp();
        let tau2_ms = log_tau2.exp();
        let mut sum_e1_squared = 0.0;
        let mut sum_e2_squared = 0.0;
        let mut sum_e1_e2 = 0.0;
        let mut sum_e1 = 0.0;
        let mut sum_e2 = 0.0;
        let mut sum_y = 0.0;
        let mut sum_e1_y = 0.0;
        let mut sum_e2_y = 0.0;
        for (time, value) in times_ms.iter().zip(values) {
            let e1 = (-time / tau1_ms).exp();
            let e2 = (-time / tau2_ms).exp();
            sum_e1_squared += e1 * e1;
            sum_e2_squared += e2 * e2;
            sum_e1_e2 += e1 * e2;
            sum_e1 += e1;
            sum_e2 += e2;
            sum_y += value;
            sum_e1_y += e1 * value;
            sum_e2_y += e2 * value;
        }
        let coefficients = solve_three_coefficients([
            [sum_e1_squared, sum_e1_e2, sum_e1, sum_e1_y],
            [sum_e1_e2, sum_e2_squared, sum_e2, sum_e2_y],
            [sum_e1, sum_e2, values.len() as f64, sum_y],
        ]);
        let Some([amplitude1, amplitude2, offset]) = coefficients else {
            return f64::INFINITY;
        };
        if amplitude1 > 0.0 || amplitude2 > 0.0 || offset > values[values.len() - 1] * 2.0 {
            return f64::INFINITY;
        }
        times_ms
            .iter()
            .zip(values)
            .map(|(time, value)| {
                let prediction = amplitude1 * (-time / tau1_ms).exp()
                    + amplitude2 * (-time / tau2_ms).exp()
                    + offset;
                (value - prediction).powi(2)
            })
            .sum()
    }

    fn golden_section_minimize<F>(mut left: f64, mut right: f64, mut objective: F) -> f64
    where
        F: FnMut(f64) -> f64,
    {
        let golden_ratio = (5.0_f64.sqrt() - 1.0) / 2.0;
        let mut c = right - golden_ratio * (right - left);
        let mut d = left + golden_ratio * (right - left);
        let mut fc = objective(c);
        let mut fd = objective(d);
        for _ in 0..80 {
            if fc < fd {
                right = d;
                d = c;
                fd = fc;
                c = right - golden_ratio * (right - left);
                fc = objective(c);
            } else {
                left = c;
                c = d;
                fc = fd;
                d = left + golden_ratio * (right - left);
                fd = objective(d);
            }
        }
        (left + right) * 0.5
    }

    fn fit_recovery_biexponential(times_ms: &[f64], values: &[f64]) -> Option<(f64, f64, f64)> {
        if times_ms.len() != values.len() || values.len() < 5 {
            return None;
        }
        let mean_value = values.iter().sum::<f64>() / values.len() as f64;
        let total_sum_squares = values
            .iter()
            .map(|value| (value - mean_value).powi(2))
            .sum::<f64>();
        if total_sum_squares <= f64::EPSILON {
            return None;
        }

        const TAU1_GRID_STEPS: usize = 128;
        const TAU2_GRID_STEPS: usize = 64;
        let min_log_tau1 = 0.1_f64.ln();
        let max_log_tau1 = 1_000.0_f64.ln();
        let min_log_tau2 = 1_000.0_f64.ln();
        let max_log_tau2 = 5_000.0_f64.ln();
        let tau1_step = (max_log_tau1 - min_log_tau1) / TAU1_GRID_STEPS as f64;
        let tau2_step = (max_log_tau2 - min_log_tau2) / TAU2_GRID_STEPS as f64;
        let mut best_log_tau1 = min_log_tau1;
        let mut best_log_tau2 = min_log_tau2;
        let mut best_error = f64::INFINITY;
        for tau1_index in 0..=TAU1_GRID_STEPS {
            let log_tau1 = min_log_tau1 + tau1_index as f64 * tau1_step;
            for tau2_index in 0..=TAU2_GRID_STEPS {
                let log_tau2 = min_log_tau2 + tau2_index as f64 * tau2_step;
                let error = recovery_biexponential_sse(log_tau1, log_tau2, times_ms, values);
                if error < best_error {
                    best_error = error;
                    best_log_tau1 = log_tau1;
                    best_log_tau2 = log_tau2;
                }
            }
        }

        for _ in 0..4 {
            let left1 = (best_log_tau1 - 2.0 * tau1_step).max(min_log_tau1);
            let right1 = (best_log_tau1 + 2.0 * tau1_step).min(max_log_tau1);
            best_log_tau1 = golden_section_minimize(left1, right1, |candidate| {
                recovery_biexponential_sse(candidate, best_log_tau2, times_ms, values)
            });
            let left2 = (best_log_tau2 - 2.0 * tau2_step).max(min_log_tau2);
            let right2 = (best_log_tau2 + 2.0 * tau2_step).min(max_log_tau2);
            best_log_tau2 = golden_section_minimize(left2, right2, |candidate| {
                recovery_biexponential_sse(best_log_tau1, candidate, times_ms, values)
            });
        }

        let residual_sum_squares =
            recovery_biexponential_sse(best_log_tau1, best_log_tau2, times_ms, values);
        let r_squared = 1.0 - residual_sum_squares / total_sum_squares;
        Some((best_log_tau1.exp(), best_log_tau2.exp(), r_squared))
    }

    fn fit_k_inactivation_current_tau1(
        current: &[f64],
        step_ms: f64,
        fixed_slow_tau_ms: f64,
    ) -> Option<(f64, f64)> {
        let mut peak_index = 0;
        for (index, value) in current.iter().enumerate().skip(1) {
            if value > &current[peak_index] {
                peak_index = index;
            }
        }
        if peak_index + 5 >= current.len() {
            return None;
        }
        let decay = &current[peak_index..current.len() - 1];
        let times: Vec<f64> = (0..decay.len())
            .map(|index| index as f64 * step_ms)
            .collect();
        fit_biexponential_fixed_tau2(&times, decay, fixed_slow_tau_ms)
    }

    fn replay_k_activation(model: HumanL23SingleCompartmentModel, test_voltage_mv: f64) -> f64 {
        let mut gates = initial_potassium_clamp_gates(model, -140.0);
        advance_k_clamp(model, &mut gates, -140.0, 20.0, 0.1);
        advance_k_clamp(model, &mut gates, test_voltage_mv, 500.0, 0.1)
    }

    fn replay_k_inactivation(
        model: HumanL23SingleCompartmentModel,
        conditioning_voltage_mv: f64,
    ) -> f64 {
        let mut gates = initial_potassium_clamp_gates(model, -140.0);
        advance_k_clamp(model, &mut gates, -140.0, 20.0, 0.1);
        advance_k_clamp(model, &mut gates, conditioning_voltage_mv, 500.0, 0.1);
        advance_k_clamp(model, &mut gates, 60.0, 50.0, 0.1)
    }

    fn replay_k_recovery(
        model: HumanL23SingleCompartmentModel,
        recovery_voltage_mv: f64,
        recovery_delay_ms: f64,
    ) -> f64 {
        let mut gates = initial_potassium_clamp_gates(model, -120.0);
        advance_k_clamp(model, &mut gates, -120.0, 2.0, 0.5);
        advance_k_clamp(model, &mut gates, 40.0, 5_000.0, 0.5);
        advance_k_clamp(
            model,
            &mut gates,
            recovery_voltage_mv,
            recovery_delay_ms,
            0.5,
        );
        advance_k_clamp(model, &mut gates, 40.0, 5.0, 0.5)
    }

    fn half_range_voltage(volts: &[f64], values: &[f64], increasing: bool) -> f64 {
        let minimum = values.iter().copied().fold(f64::INFINITY, f64::min);
        let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        for index in 0..volts.len() - 1 {
            let left = (values[index] - minimum) / (maximum - minimum);
            let right = (values[index + 1] - minimum) / (maximum - minimum);
            let crosses_half = if increasing {
                left <= 0.5 && right >= 0.5
            } else {
                left >= 0.5 && right <= 0.5
            };
            if crosses_half {
                let fraction = (0.5 - left) / (right - left);
                return volts[index] + fraction * (volts[index + 1] - volts[index]);
            }
        }
        panic!("voltage-clamp curve did not cross half range");
    }

    #[test]
    fn reconstructed_k_human_fixed_slow_tau_current_fit_matches_independent_reference() {
        let model = wilbers_voltage_clamp_model();
        let voltages_mv = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0];
        // Independent SciPy references for K_IV's post-peak current fit:
        // a1*exp(-t/tau1) + a2*exp(-t/450 ms) + offset, with tau1 in [0, 300] ms.
        let expected_fast_tau_ms = [
            52.280_407_80,
            41.563_484_62,
            33.463_646_61,
            27.264_606_91,
            22.469_336_83,
            18.745_079_68,
        ];
        for (index, voltage_mv) in voltages_mv.into_iter().enumerate() {
            let current = replay_k_activation_current(model, voltage_mv);
            let (tau1_ms, r_squared) =
                fit_k_inactivation_current_tau1(&current, 0.1, 450.0).unwrap();
            assert!(
                (tau1_ms - expected_fast_tau_ms[index]).abs() < 0.1,
                "K_IV fast inactivation tau mismatch at {voltage_mv} mV: {tau1_ms} ms"
            );
            assert!(r_squared > 0.99);
        }
    }

    #[test]
    fn reconstructed_k_mouse_fixed_slow_tau_current_fit_matches_independent_reference() {
        let model = wilbers_mouse_voltage_clamp_model();
        let voltages_mv = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0];
        // Independent SciPy references from k_mouse.mod, with the K_IV
        // activation current and fixed 450-ms slow component used in Figure S5J.
        let expected_fast_tau_ms = [53.429_1, 41.997_2, 33.677_6, 27.398_6, 22.571_7, 18.819_3];
        for (index, voltage_mv) in voltages_mv.into_iter().enumerate() {
            let current = replay_k_activation_current(model, voltage_mv);
            let (tau1_ms, r_squared) =
                fit_k_inactivation_current_tau1(&current, 0.1, 450.0).unwrap();
            assert!(
                (tau1_ms - expected_fast_tau_ms[index]).abs() < 0.02,
                "mouse K_IV fast inactivation tau mismatch at {voltage_mv} mV: {tau1_ms} ms"
            );
            assert!(r_squared > 0.99);
        }
    }

    #[test]
    fn deposited_k_recovery_current_protocol_replays_mouse_figure_s5_curves() {
        let model = wilbers_mouse_voltage_clamp_model();
        let recovery_delays_ms = [
            4.0, 144.0, 484.0, 1_024.0, 1_764.0, 2_704.0, 3_844.0, 5_184.0, 6_724.0, 8_464.0,
        ];
        let recovery_voltages_mv = [-90.0, -85.0, -80.0, -75.0, -70.0];
        // Independent SciPy references from pure k_mouse.mod for the deposited
        // 5-voltage x 10-delay protocol, followed by the 5-ms +40-mV test pulse.
        let expected_fast_tau_ms = [
            115.587_958_76,
            155.364_357_20,
            234.451_978_56,
            374.388_268_19,
            329.900_992_76,
        ];
        let expected_slow_tau_ms = [
            2_790.860_045_91,
            2_793.137_069_31,
            2_799.268_838_73,
            2_801.184_309_52,
            2_799.717_372_53,
        ];

        for (index, recovery_voltage_mv) in recovery_voltages_mv.into_iter().enumerate() {
            let pulse_peaks =
                replay_k_recovery_peak_currents(model, recovery_voltage_mv, &recovery_delays_ms);
            assert!(pulse_peaks
                .iter()
                .all(|peak| peak.is_finite() && *peak > 0.0));
            assert!(pulse_peaks.windows(2).all(|pair| pair[1] > pair[0]));
            let (fast_tau_ms, slow_tau_ms, r_squared) =
                fit_recovery_biexponential(&recovery_delays_ms, &pulse_peaks).unwrap();
            assert!(fast_tau_ms < 1_000.0);
            assert!((1_000.0..=5_000.0).contains(&slow_tau_ms));
            assert!(
                (fast_tau_ms - expected_fast_tau_ms[index]).abs() < 3.0,
                "mouse K_recovery fast tau mismatch at {recovery_voltage_mv} mV: {fast_tau_ms} ms"
            );
            assert!(
                (slow_tau_ms - expected_slow_tau_ms[index]).abs() < 15.0,
                "mouse K_recovery slow tau mismatch at {recovery_voltage_mv} mV: {slow_tau_ms} ms"
            );
            assert!(r_squared > 0.999);
            if recovery_voltage_mv == -80.0 {
                // The plotted source target is the human/mouse arithmetic mean;
                // the mechanism's slow recovery constant is also shared.
                let pooled_fast_mean_ms = (228.527_493_810_715_55 + 245.121_197_002_686_07) / 2.0;
                let pooled_slow_mean_ms = (1_999.729_496_786_659_6 + 3_579.856_388_834_977_7) / 2.0;
                assert!((fast_tau_ms - pooled_fast_mean_ms).abs() < 3.0);
                assert!((slow_tau_ms - pooled_slow_mean_ms).abs() < 20.0);
            }
        }
    }

    #[test]
    fn deposited_k_recovery_current_protocol_replays_human_figure_s5_curves() {
        let model = wilbers_voltage_clamp_model();
        let recovery_delays_ms = [
            4.0, 144.0, 484.0, 1_024.0, 1_764.0, 2_704.0, 3_844.0, 5_184.0, 6_724.0, 8_464.0,
        ];
        let recovery_voltages_mv = [-90.0, -85.0, -80.0, -75.0, -70.0];
        // Independent SciPy references for the source K_recovery protocol:
        // -120 mV for 2 ms, +40 mV for 5 s, recovery at each voltage/delay,
        // then a 5-ms +40-mV test pulse sampled at dt=0.5 ms.
        let expected_fast_tau_ms = [
            115.730_759_79,
            155.668_257_52,
            235.149_066_91,
            376.909_972_45,
            332.216_218_39,
        ];
        let expected_slow_tau_ms = [
            2_791.296_663_36,
            2_794.577_893_32,
            2_803.291_958_06,
            2_816.549_375_65,
            2_814.890_626_97,
        ];

        for (index, recovery_voltage_mv) in recovery_voltages_mv.into_iter().enumerate() {
            let pulse_peaks =
                replay_k_recovery_peak_currents(model, recovery_voltage_mv, &recovery_delays_ms);
            assert!(pulse_peaks
                .iter()
                .all(|peak| peak.is_finite() && *peak > 0.0));
            assert!(pulse_peaks.windows(2).all(|pair| pair[1] > pair[0]));
            let (fast_tau_ms, slow_tau_ms, r_squared) =
                fit_recovery_biexponential(&recovery_delays_ms, &pulse_peaks).unwrap();
            assert!(fast_tau_ms < 1_000.0);
            assert!((1_000.0..=5_000.0).contains(&slow_tau_ms));
            assert!(
                (fast_tau_ms - expected_fast_tau_ms[index]).abs() < 3.0,
                "K_recovery fast tau mismatch at {recovery_voltage_mv} mV: {fast_tau_ms} ms"
            );
            assert!(
                (slow_tau_ms - expected_slow_tau_ms[index]).abs() < 15.0,
                "K_recovery slow tau mismatch at {recovery_voltage_mv} mV: {slow_tau_ms} ms"
            );
            assert!(r_squared > 0.999);
            if recovery_voltage_mv == -80.0 {
                let pooled_fast_mean_ms = (228.527_493_810_715_55 + 245.121_197_002_686_07) / 2.0;
                let pooled_slow_mean_ms = (1_999.729_496_786_659_6 + 3_579.856_388_834_977_7) / 2.0;
                assert!((fast_tau_ms - pooled_fast_mean_ms).abs() < 3.0);
                assert!((slow_tau_ms - pooled_slow_mean_ms).abs() < 20.0);
            }
        }
    }

    #[test]
    fn exponential_offset_fit_recovers_a_known_time_constant() {
        let times: Vec<f64> = (0..100).map(|index| index as f64 * 0.1).collect();
        let values: Vec<f64> = times
            .iter()
            .map(|time| -2.5 * (-time / 3.5).exp() + 0.2)
            .collect();
        let (tau_ms, r_squared) = fit_exponential_offset_tau(&times, &values).unwrap();
        assert!((tau_ms - 3.5).abs() < 1.0e-6);
        assert!(r_squared > 0.999_999);
    }

    #[test]
    fn deposited_k_iv_current_activation_fit_replays_human_figure_s5_curve() {
        let model = wilbers_voltage_clamp_model();
        let voltages_mv = [-10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0];
        // Independent SciPy curve_fit references for the deposited K_IV protocol:
        // 20 ms at -140 mV; 500 ms test pulse; dt=0.1 ms; fit the rising
        // current before its peak with a*exp(-t/tau)+offset, as get_tau_act does.
        let expected_tau_ms = [
            3.284_746_40,
            2.298_529_85,
            1.700_318_83,
            1.330_597_10,
            1.082_613_13,
            0.902_015_07,
            0.771_108_13,
        ];
        let experimental_means_ms = [3.36, 2.41, 1.68, 1.25, 0.88, 0.69, 0.58];
        let mut squared_error = 0.0;
        for (index, voltage_mv) in voltages_mv.into_iter().enumerate() {
            let current = replay_k_activation_current(model, voltage_mv);
            let (tau_ms, r_squared) = fit_k_activation_current_tau(&current, 0.1).unwrap();
            assert!(
                (tau_ms - expected_tau_ms[index]).abs() < 0.01,
                "K_IV current activation tau mismatch at {voltage_mv} mV: {tau_ms} ms"
            );
            assert!(r_squared > 0.99);
            squared_error += (tau_ms - experimental_means_ms[index]).powi(2);
        }
        let rmse_ms = (squared_error / voltages_mv.len() as f64).sqrt();
        assert!(
            rmse_ms < 0.20,
            "source-equivalent human K_IV activation RMSE {rmse_ms} ms exceeds digitized Figure S5 tolerance"
        );
    }

    #[test]
    fn deposited_k_voltage_clamp_protocols_replay_with_stable_gate_dynamics() {
        let model = wilbers_voltage_clamp_model();

        // Golden values are from an independent exact first-order gate integration
        // of the deposited NMODL equations at 34°C, with the source clamp timings.
        let activation_at_zero = replay_k_activation(model, 0.0);
        let inactivation_after_minus_80 = replay_k_inactivation(model, -80.0);
        assert!((activation_at_zero - 0.471_306_108_091_782).abs() < 1.0e-9);
        assert!((inactivation_after_minus_80 - 0.805_281_859_671_567_1).abs() < 1.0e-9);

        // The deposited recovery protocol crosses all five recovery voltages
        // at each of its ten delays; testing only -80 mV misses 40 of 50
        // command-condition combinations.
        let recovery_voltages_mv = [-90.0, -85.0, -80.0, -75.0, -70.0];
        let delays_ms = [
            4.0, 144.0, 484.0, 1_024.0, 1_764.0, 2_704.0, 3_844.0, 5_184.0, 6_724.0, 8_464.0,
        ];
        let expected = [
            [
                0.149_241_247_781_421_23,
                0.410_822_627_485_083,
                0.541_519_564_453_313,
                0.589_017_235_172_469_3,
                0.634_943_462_843_831,
                0.678_144_573_182_064_2,
                0.714_313_571_338_087_7,
                0.741_644_333_526_286_8,
                0.760_447_557_548_322_9,
                0.772_290_896_694_584_7,
            ],
            [
                0.146_013_723_477_012_22,
                0.365_572_310_623_542_6,
                0.521_278_220_281_874_3,
                0.577_460_986_500_203_7,
                0.622_682_433_563_795_3,
                0.664_827_689_242_275_2,
                0.700_109_472_705_215_3,
                0.726_769_812_686_144_2,
                0.745_111_794_574_793_5,
                0.756_664_617_211_342,
            ],
            [
                0.142_904_731_961_108,
                0.307_594_487_634_699_65,
                0.479_816_410_714_972_83,
                0.558_336_191_281_282,
                0.605_589_654_189_097_2,
                0.646_440_719_483_724_1,
                0.680_500_889_539_857_7,
                0.706_235_845_981_651_7,
                0.723_941_159_885_072_7,
                0.735_092_972_795_100_9,
            ],
            [
                0.140_635_220_768_559_8,
                0.253_220_230_450_319_05,
                0.414_776_190_621_214_8,
                0.520_982_834_768_333_4,
                0.580_132_289_347_902_6,
                0.621_463_640_446_012_8,
                0.654_088_104_234_127_4,
                0.678_587_349_030_343_2,
                0.695_435_756_563_887_6,
                0.706_047_668_702_351_1,
            ],
            [
                0.140_820_001_864_388_06,
                0.255_944_703_300_302_83,
                0.409_712_060_396_593_1,
                0.501_479_772_159_386_3,
                0.551_908_832_031_219_3,
                0.589_375_635_257_233_5,
                0.619_713_596_811_803_6,
                0.642_582_521_152_46,
                0.658_314_450_188_136_8,
                0.668_223_288_259_362_4,
            ],
        ];

        for (voltage_index, recovery_voltage_mv) in recovery_voltages_mv.into_iter().enumerate() {
            let recovered: Vec<f64> = delays_ms
                .into_iter()
                .map(|delay| replay_k_recovery(model, recovery_voltage_mv, delay))
                .collect();
            assert!(recovered.windows(2).all(|pair| pair[1] > pair[0]));
            for (delay_index, value) in recovered.into_iter().enumerate() {
                assert!(
                    (value - expected[voltage_index][delay_index]).abs() < 1.0e-9,
                    "recovery mismatch at {} mV after {} ms: {value}",
                    recovery_voltage_mv,
                    delays_ms[delay_index]
                );
            }
        }
    }

    #[test]
    fn potassium_clamp_curves_are_consistent_with_published_human_group_summaries() {
        let model = wilbers_voltage_clamp_model();
        // K_IV_ss uses -110 to +50 mV in 10-mV increments.
        let voltages: Vec<f64> = (-110..=50).step_by(10).map(f64::from).collect();
        let activation: Vec<f64> = voltages
            .iter()
            .map(|voltage| replay_k_activation(model, *voltage))
            .collect();
        let inactivation: Vec<f64> = voltages
            .iter()
            .map(|voltage| replay_k_inactivation(model, *voltage))
            .collect();

        let activation_half = half_range_voltage(&voltages, &activation, true);
        let fit_voltages: Vec<f64> = voltages
            .iter()
            .copied()
            .filter(|voltage| *voltage <= 0.0)
            .collect();
        let fit_inactivation: Vec<f64> = inactivation
            .iter()
            .copied()
            .zip(voltages.iter())
            .filter_map(|(value, voltage)| (*voltage <= 0.0).then_some(value))
            .collect();
        let inactivation_half = half_range_voltage(&fit_voltages, &fit_inactivation, false);
        let inactivation_max = inactivation.iter().copied().fold(0.0_f64, f64::max);
        let minus_80_index = voltages
            .iter()
            .position(|voltage| *voltage == -80.0)
            .unwrap();
        let availability_at_minus_80 = inactivation[minus_80_index] / inactivation_max;

        // The half-range crossing is a transparent interpolation, not the
        // source's nonlinear least-squares Boltzmann fit. These values should
        // fall within the paper's human group mean ± SD.
        assert!((activation_half - (-3.03)).abs() < 5.95);
        assert!((inactivation_half - (-52.69)).abs() < 5.97);
        assert!((availability_at_minus_80 - 0.94).abs() < 0.05);
        assert!((activation_half - (-3.250_450_672_099_808_5)).abs() < 1.0e-8);
        assert!((inactivation_half - (-51.484_526_215_264_54)).abs() < 1.0e-8);
        assert!((availability_at_minus_80 - 0.936_220_052_891_604_8).abs() < 1.0e-8);
    }

    #[test]
    fn trap0_uses_the_analytic_limit_and_is_continuous() {
        let prefactor = RatePrefactor {
            per_millivolt_per_ms: 0.2,
        };
        let slope = 10.0;
        let half_voltage = -40.0;
        let limit = trap0(half_voltage, half_voltage, prefactor, slope).unwrap();
        let below = trap0(half_voltage - 1.0e-7, half_voltage, prefactor, slope).unwrap();
        let above = trap0(half_voltage + 1.0e-7, half_voltage, prefactor, slope).unwrap();

        assert!((limit - 2.0).abs() < 1.0e-14);
        assert!((below - limit).abs() < 1.0e-7);
        assert!((above - limit).abs() < 1.0e-7);
    }

    #[test]
    fn human_sodium_rates_are_continuous_at_all_trap0_landmarks() {
        let model = wilbers_model();
        let parameters = model.sodium;
        let temperature_factor = model.sodium_temperature_factor().unwrap();

        // Independently evaluate a*x/(1-exp(-x)) with the analytic x=0
        // limit. The deposited NMODL guard tests v+theta, while its
        // denominator is singular at v-theta.
        let source_rate =
            |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                    let x = (voltage_mv - half_voltage_mv) / slope_mv;
                    let scale = prefactor.per_millivolt_per_ms * slope_mv;
                    if x == 0.0 {
                        scale
                    } else {
                        scale * x / -(-x).exp_m1()
                    }
                };
            let expected_activation_tau = |voltage_mv: f64| {
                let alpha = source_rate(
                    voltage_mv,
                    parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                let beta = source_rate(
                    -voltage_mv,
                    -parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                1.0 / (temperature_factor * (alpha + beta))
            };
            let expected_inactivation_tau = |voltage_mv: f64| {
                let alpha = source_rate(
                    voltage_mv,
                    parameters.inactivation_rate_half_voltage_mv,
                    parameters.inactivation_rate,
                    parameters.inactivation_rate_slope_mv,
                );
                let beta = source_rate(
                    -voltage_mv,
                    -parameters.recovery_rate_half_voltage_mv,
                    parameters.recovery_rate,
                    parameters.recovery_rate_slope_mv,
                );
                1.0 / (temperature_factor * (alpha + beta))
            };
    
            let false_guard_offsets = |slope_mv: f64| {
                [
                    -1.01e-6 * slope_mv,
                    -0.99e-6 * slope_mv,
                    0.0,
                    0.99e-6 * slope_mv,
                    1.01e-6 * slope_mv,
                ]
            };
            let singularity_offsets = [-2.0e-6, -1.0e-6, 0.0, 1.0e-6, 2.0e-6];
            let landmarks = [
                (
                    "Na m activation false guard",
                    -parameters.activation_rate_half_voltage_mv,
                    true,
                    false_guard_offsets(parameters.activation_rate_slope_mv),
                ),
                (
                    "Na m activation denominator singularity",
                    parameters.activation_rate_half_voltage_mv,
                    true,
                    singularity_offsets,
                ),
                (
                    "Na h alpha false guard",
                    -parameters.inactivation_rate_half_voltage_mv,
                    false,
                    false_guard_offsets(parameters.inactivation_rate_slope_mv),
                ),
                (
                    "Na h alpha denominator singularity",
                    parameters.inactivation_rate_half_voltage_mv,
                    false,
                    singularity_offsets,
                ),
                (
                    "Na h beta false guard",
                    -parameters.recovery_rate_half_voltage_mv,
                    false,
                    false_guard_offsets(parameters.recovery_rate_slope_mv),
                ),
                (
                    "Na h beta denominator singularity",
                    parameters.recovery_rate_half_voltage_mv,
                    false,
                    singularity_offsets,
                ),
            ];
    
            for (name, center_mv, activation_path, offsets_mv) in landmarks {
                for offset_mv in offsets_mv {
                    let effective_voltage_mv = center_mv + offset_mv;
                    // sodium_rates accepts membrane voltage; map from the
                    // effective channel voltage through the configured -10-mV shift.
                    let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                    let rates = model.sodium_rates(membrane_voltage_mv).unwrap();
                    let (observed, expected) = if activation_path {
                        (
                            rates.activation.time_constant_ms,
                            expected_activation_tau(effective_voltage_mv),
                        )
                    } else {
                        (
                            rates.inactivation.time_constant_ms,
                            expected_inactivation_tau(effective_voltage_mv),
                        )
                    };
                    assert!(
                        (observed - expected).abs() < 1.0e-12,
                        "{name} tau mismatch at offset {offset_mv} mV: {observed} vs {expected} ms"
                    );
                }
            }
        }
    
        #[test]
        fn human_sodium_rates_match_source_equations_over_voltage_grid() {
            let model = wilbers_model();
            let parameters = model.sodium;
            let temperature_factor = model.sodium_temperature_factor().unwrap();
            let source_rate =
                |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                    let x = (voltage_mv - half_voltage_mv) / slope_mv;
                    let scale = prefactor.per_millivolt_per_ms * slope_mv;
                    if x == 0.0 {
                        scale
                    } else {
                        scale * x / -(-x).exp_m1()
                    }
                };
    
            // Compare both sodium gate taus and steady states against the
            // independent analytic source equations over -120..+100 mV.
            for index in 0..=440 {
                let effective_voltage_mv = -120.0 + index as f64 * 0.5;
                let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                let rates = model.sodium_rates(membrane_voltage_mv).unwrap();
    
                let alpha_m = source_rate(
                    effective_voltage_mv,
                    parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                let beta_m = source_rate(
                    -effective_voltage_mv,
                    -parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                let expected_m_tau = 1.0 / (temperature_factor * (alpha_m + beta_m));
                let expected_m_inf = 1.0
                    / (1.0
                        + ((parameters.activation_half_voltage_mv - effective_voltage_mv)
                            / parameters.activation_slope_mv)
                            .exp());
    
                let alpha_h = source_rate(
                    effective_voltage_mv,
                    parameters.inactivation_rate_half_voltage_mv,
                    parameters.inactivation_rate,
                    parameters.inactivation_rate_slope_mv,
                );
                let beta_h = source_rate(
                    -effective_voltage_mv,
                    -parameters.recovery_rate_half_voltage_mv,
                    parameters.recovery_rate,
                    parameters.recovery_rate_slope_mv,
                );
                let expected_h_tau = 1.0 / (temperature_factor * (alpha_h + beta_h));
                let expected_h_inf = 1.0
                    / (1.0
                        + ((effective_voltage_mv - parameters.inactivation_half_voltage_mv)
                            / parameters.inactivation_slope_mv)
                            .exp());
    
                assert!(
                    (rates.activation.time_constant_ms - expected_m_tau).abs() < 1.0e-12,
                    "Na activation tau mismatch at effective voltage {effective_voltage_mv} mV"
                );
                assert!(
                    (rates.activation.steady_state - expected_m_inf).abs() < 1.0e-14,
                    "Na activation steady state mismatch at effective voltage {effective_voltage_mv} mV"
                );
                assert!(
                    (rates.inactivation.time_constant_ms - expected_h_tau).abs() < 1.0e-12,
                    "Na inactivation tau mismatch at effective voltage {effective_voltage_mv} mV"
                );
                assert!(
                    (rates.inactivation.steady_state - expected_h_inf).abs() < 1.0e-14,
                    "Na inactivation steady state mismatch at effective voltage {effective_voltage_mv} mV"
                );
            }
        }
    
        #[test]
        fn human_potassium_activation_rate_is_continuous_at_both_trap0_voltage_landmarks() {
            let model = wilbers_model();
            let parameters = model.potassium;
            let temperature_factor = model.potassium_temperature_factor().unwrap();
    
            // Independently evaluate the deposited rate equation using exp_m1.
            // This specifically distinguishes the true denominator singularity
            // (v=th) from the source's former wrong-sign guard (v=-th).
            let source_rate = |voltage_mv: f64, half_voltage_mv: f64| {
                let x = (voltage_mv - half_voltage_mv) / parameters.activation_rate_slope_mv;
                let scale = parameters.activation_rate.per_millivolt_per_ms
                    * parameters.activation_rate_slope_mv;
                if x == 0.0 {
                    scale
                } else {
                    scale * x / -(-x).exp_m1()
                }
            };
            let expected_activation_tau = |effective_voltage_mv: f64| {
                let alpha = source_rate(
                    effective_voltage_mv,
                    parameters.activation_rate_half_voltage_mv,
                );
                let beta = source_rate(
                    -effective_voltage_mv,
                    -parameters.activation_rate_half_voltage_mv,
                );
                1.0 / (temperature_factor * (alpha + beta))
            };
    
            // The old NMODL guard incorrectly switched branches around v=-th.
            // Keep this point and both sides covered so a sign regression cannot
            // reintroduce a discontinuity that a generic trap0 test would miss.
            let former_false_guard_mv = -parameters.activation_rate_half_voltage_mv;
            for offset_mv in [-6.60e-6, -6.59e-6, 0.0, 6.59e-6, 6.60e-6] {
                let effective_voltage_mv = former_false_guard_mv + offset_mv;
                let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                let observed = model
                    .potassium_rates(membrane_voltage_mv, 0.5)
                    .unwrap()
                    .activation
                    .time_constant_ms;
                let expected = expected_activation_tau(effective_voltage_mv);
                assert!(
                    (observed - expected).abs() < 1.0e-12,
                    "K activation tau mismatch near former wrong-sign guard at offset {offset_mv} mV: {observed} vs {expected} ms"
                );
            }
    
            // The actual a*(v-th)/(1-exp(-(v-th)/q)) denominator singularity is
            // at v=th; check its analytic limit and nearby values as well.
            let true_singularity_mv = parameters.activation_rate_half_voltage_mv;
            for offset_mv in [-1.0e-6, 0.0, 1.0e-6] {
                let effective_voltage_mv = true_singularity_mv + offset_mv;
                let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                let observed = model
                    .potassium_rates(membrane_voltage_mv, 0.5)
                    .unwrap()
                    .activation
                    .time_constant_ms;
                let expected = expected_activation_tau(effective_voltage_mv);
                assert!(
                    (observed - expected).abs() < 1.0e-12,
                    "K activation tau mismatch near true trap0 singularity at offset {offset_mv} mV: {observed} vs {expected} ms"
                );
            }
        }
    
        #[test]
        fn human_potassium_activation_rates_match_source_equations_over_voltage_grid() {
            let model = wilbers_model();
            let parameters = model.potassium;
            let temperature_factor = model.potassium_temperature_factor().unwrap();
    
            let source_rate = |voltage_mv: f64, half_voltage_mv: f64| {
                let x = (voltage_mv - half_voltage_mv) / parameters.activation_rate_slope_mv;
                let scale = parameters.activation_rate.per_millivolt_per_ms
                    * parameters.activation_rate_slope_mv;
                if x == 0.0 {
                    scale
                } else {
                    scale * x / -(-x).exp_m1()
                }
            };
    
            // Compare the Rust channel API against the analytic form of the
            // deposited activation equation, including the model's explicit
            // voltage shift, over the full source table voltage interval.
            for index in 0..=440 {
                let effective_voltage_mv = -120.0 + index as f64 * 0.5;
                let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                let rates = model.potassium_rates(membrane_voltage_mv, 0.5).unwrap();
                let alpha = source_rate(
                    effective_voltage_mv,
                    parameters.activation_rate_half_voltage_mv,
                );
                let beta = source_rate(
                    -effective_voltage_mv,
                    -parameters.activation_rate_half_voltage_mv,
                );
                let expected_tau = 1.0 / (temperature_factor * (alpha + beta));
                let expected_steady_state = 1.0
                    / (1.0
                        + ((parameters.activation_half_voltage_mv - effective_voltage_mv)
                            / parameters.activation_slope_mv)
                            .exp());
    
                assert!(
                    (rates.activation.time_constant_ms - expected_tau).abs() < 1.0e-12,
                    "K activation tau mismatch at effective voltage {effective_voltage_mv} mV"
                );
                assert!(
                    (rates.activation.steady_state - expected_steady_state).abs() < 1.0e-14,
                    "K activation steady state mismatch at effective voltage {effective_voltage_mv} mV"
                );
            }
        }
    
        #[test]
        fn human_potassium_fast_inactivation_rates_are_continuous_at_all_trap0_landmarks() {
            let model = wilbers_model();
            let parameters = model.potassium;
            let temperature_factor = model.potassium_temperature_factor().unwrap();
    
            let source_rate =
                |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                    let x = (voltage_mv - half_voltage_mv) / slope_mv;
                    let scale = prefactor.per_millivolt_per_ms * slope_mv;
                    if x == 0.0 {
                        scale
                    } else {
                        scale * x / -(-x).exp_m1()
                    }
                };
            let expected_tau = |effective_voltage_mv: f64| {
                let alpha = source_rate(
                    effective_voltage_mv,
                    parameters.inactivation_rate_half_voltage_mv,
                    parameters.inactivation_rate,
                    parameters.inactivation_rate_slope_mv,
                );
                let beta = source_rate(
                    -effective_voltage_mv,
                    -parameters.recovery_rate_half_voltage_mv,
                    parameters.recovery_rate,
                    parameters.recovery_rate_slope_mv,
                );
                1.0 / (temperature_factor * (alpha + beta))
            };
    
            // Each component has a distinct wrong-sign guard and a distinct true
            // denominator singularity in the deposited K source.
            let landmarks = [
                (
                    -parameters.inactivation_rate_half_voltage_mv,
                    1.0e-6 * parameters.inactivation_rate_slope_mv,
                ),
                (parameters.inactivation_rate_half_voltage_mv, 1.0e-6),
                (
                    -parameters.recovery_rate_half_voltage_mv,
                    1.0e-6 * parameters.recovery_rate_slope_mv,
                ),
                (parameters.recovery_rate_half_voltage_mv, 1.0e-6),
            ];
    
            for (center_mv, width_mv) in landmarks {
                let offsets = if center_mv == -parameters.inactivation_rate_half_voltage_mv
                    || center_mv == -parameters.recovery_rate_half_voltage_mv
                {
                    [
                        -1.01 * width_mv,
                        -0.99 * width_mv,
                        0.0,
                        0.99 * width_mv,
                        1.01 * width_mv,
                    ]
                } else {
                    [-width_mv, 0.0, width_mv, 2.0 * width_mv, -2.0 * width_mv]
                };
    
                for offset_mv in offsets {
                    let effective_voltage_mv = center_mv + offset_mv;
                    let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                    let observed = model
                        .potassium_rates(membrane_voltage_mv, 0.5)
                        .unwrap()
                        .fast_inactivation
                        .time_constant_ms;
                    let expected = expected_tau(effective_voltage_mv);
                    assert!(
                        (observed - expected).abs() < 1.0e-10,
                        "K fast-inactivation tau mismatch at landmark {center_mv} mV, offset {offset_mv} mV: {observed} vs {expected} ms"
                    );
                }
            }
        }
    
        #[test]
        fn human_potassium_fast_inactivation_rates_match_source_equations_over_voltage_grid() {
            let model = wilbers_model();
            let parameters = model.potassium;
            let temperature_factor = model.potassium_temperature_factor().unwrap();
    
            let source_rate =
                |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                    let x = (voltage_mv - half_voltage_mv) / slope_mv;
                    let scale = prefactor.per_millivolt_per_ms * slope_mv;
                    if x == 0.0 {
                        scale
                    } else {
                        scale * x / -(-x).exp_m1()
                    }
                };
    
            for index in 0..=440 {
                let effective_voltage_mv = -120.0 + index as f64 * 0.5;
                let membrane_voltage_mv = effective_voltage_mv - model.voltage_shift_mv;
                let rates = model.potassium_rates(membrane_voltage_mv, 0.5).unwrap();
                let alpha = source_rate(
                    effective_voltage_mv,
                    parameters.inactivation_rate_half_voltage_mv,
                    parameters.inactivation_rate,
                    parameters.inactivation_rate_slope_mv,
                );
                let beta = source_rate(
                    -effective_voltage_mv,
                    -parameters.recovery_rate_half_voltage_mv,
                    parameters.recovery_rate,
                    parameters.recovery_rate_slope_mv,
                );
                let expected_tau = 1.0 / (temperature_factor * (alpha + beta));
                let expected_steady_state = 1.0
                    / (1.0
                        + ((effective_voltage_mv - parameters.inactivation_half_voltage_mv)
                            / parameters.inactivation_slope_mv)
                            .exp());
    
                assert!(
                    (rates.fast_inactivation.time_constant_ms - expected_tau).abs() < 1.0e-9,
                    "K fast-inactivation tau mismatch at effective voltage {effective_voltage_mv} mV"
                );
                assert!(
                    (rates.fast_inactivation.steady_state - expected_steady_state).abs() < 1.0e-14,
                    "K fast-inactivation steady state mismatch at effective voltage {effective_voltage_mv} mV"
                );
            }
        }
    
        #[test]
        fn potassium_slow_inactivation_uses_distinct_inactivation_and_recovery_constants() {
            let model = wilbers_model();
            let depolarized = model.potassium_rates(30.0, 0.5).unwrap();
            let hyperpolarized = model.potassium_rates(-70.0, 0.5).unwrap();
    
            assert_eq!(depolarized.slow_inactivation_time_constant_ms, 450.0);
            assert_eq!(
                hyperpolarized.slow_inactivation_time_constant_ms,
                2789.7929428108187
            );
            assert!(depolarized.fast_inactivation.time_constant_ms > 0.0);
            assert!(hyperpolarized.fast_inactivation.time_constant_ms > 0.0);
        }
    
        #[test]
        fn potassium_inactivation_fraction_matches_the_three_component_source_decomposition() {
            let model = wilbers_model();
            let fast_fraction = model.potassium.inactivating_fraction
                * (1.0 - model.potassium.slow_fraction_of_inactivating);
            let slow_fraction =
                model.potassium.inactivating_fraction * model.potassium.slow_fraction_of_inactivating;
            let non_inactivating_fraction = 1.0 - model.potassium.inactivating_fraction;
    
            assert!((fast_fraction - 0.51).abs() < f64::EPSILON);
            assert!((slow_fraction - 0.34).abs() < f64::EPSILON);
            assert!((non_inactivating_fraction - 0.15).abs() < f64::EPSILON);
            assert!(
                (fast_fraction + slow_fraction + non_inactivating_fraction - 1.0).abs() < f64::EPSILON
            );
        }
    
        #[test]
        fn human_gate_steady_states_reproduce_the_deposited_half_voltage_parameters() {
            let model = wilbers_model();
            let na_m = model
                .sodium_rates(model.sodium.activation_half_voltage_mv - model.voltage_shift_mv)
                .unwrap()
                .activation
                .steady_state;
            let na_h = model
                .sodium_rates(model.sodium.inactivation_half_voltage_mv - model.voltage_shift_mv)
                .unwrap()
                .inactivation
                .steady_state;
            let k_m = model
                .potassium_rates(
                    model.potassium.activation_half_voltage_mv - model.voltage_shift_mv,
                    0.5,
                )
                .unwrap()
                .activation
                .steady_state;
            let k_h = model
                .potassium_rates(
                    model.potassium.inactivation_half_voltage_mv - model.voltage_shift_mv,
                    0.5,
                )
                .unwrap()
                .fast_inactivation
                .steady_state;
    
            for steady_state in [na_m, na_h, k_m, k_h] {
                assert!((steady_state - 0.5).abs() < 1.0e-14);
            }
        }
    
        #[test]
        fn current_clamp_voltage_shift_and_initial_gates_match_hybrid_source() {
            let model = wilbers_model();
            assert_eq!(model.voltage_shift_mv, -10.0);
    
            // The deposited hybrid NMODL calls trates(v + vshift). With the
            // current-clamp helper's vshift=-10 mV, both channels evaluate gates
            // at V-10 mV (not V+10 mV).
            let mut unshifted_model = model;
            unshifted_model.voltage_shift_mv = 0.0;
            let voltage_mv = -70.0;
    
            let sodium_shifted = model.sodium_rates(voltage_mv).unwrap();
            let sodium_source_equivalent = unshifted_model.sodium_rates(voltage_mv - 10.0).unwrap();
            assert_eq!(sodium_shifted, sodium_source_equivalent);
    
            let potassium_shifted = model.potassium_rates(voltage_mv, 0.5).unwrap();
            let potassium_source_equivalent = unshifted_model
                .potassium_rates(voltage_mv - 10.0, 0.5)
                .unwrap();
            assert_eq!(potassium_shifted, potassium_source_equivalent);
    
            // The hybrid INITIAL blocks set m=minf, h=hinf, h1=hinf and h2=hinf.
            let initial_conditions = HumanL23SingleCompartmentInitialConditions::new(
                Volts::from_millivolts(voltage_mv).unwrap(),
            );
            let simulation =
                HumanL23SingleCompartmentSimulation::new(model, initial_conditions).unwrap();
            let state = simulation.state();
    
            assert_eq!(
                state.sodium_activation(),
                sodium_shifted.activation.steady_state
            );
            assert_eq!(
                state.sodium_inactivation(),
                sodium_shifted.inactivation.steady_state
            );
            assert_eq!(
                state.potassium_activation(),
                potassium_shifted.activation.steady_state
            );
            assert_eq!(
                state.potassium_fast_inactivation(),
                potassium_shifted.fast_inactivation.steady_state
            );
            assert_eq!(
                state.potassium_slow_inactivation(),
                potassium_shifted.fast_inactivation.steady_state
            );
        }
    
        #[test]
        fn channel_time_constants_are_finite_and_positive_across_source_voltage_range() {
            let model = wilbers_model();
            for voltage_mv in -120..=100 {
                let sodium = model.sodium_rates(voltage_mv as f64).unwrap();
                let potassium = model.potassium_rates(voltage_mv as f64, 0.5).unwrap();
                for tau in [
                    sodium.activation.time_constant_ms,
                    sodium.inactivation.time_constant_ms,
                    potassium.activation.time_constant_ms,
                    potassium.fast_inactivation.time_constant_ms,
                    potassium.slow_inactivation_time_constant_ms,
                ] {
                    assert!(tau.is_finite() && tau > 0.0);
                }
            }
        }
    
        #[test]
        fn na_voltage_clamp_command_sequence_replays_human_gates_at_25c() {
            // The deposited Na_IV / Na_IV_ss helper uses a pure voltage-clamp
            // cell at 25°C, dt=0.01 ms, 2 ms at -120 mV, then 10 ms at each
            // 5-mV test step from -80 to +10 mV. The voltage-clamp mechanism
            // uses its default zero voltage shift, not the -10-mV current-clamp
            // junction-potential correction.
            let mut model = wilbers_model();
            model.temperature_celsius = 25.0;
            model.voltage_shift_mv = 0.0;
            assert!((model.sodium_temperature_factor().unwrap() - 1.0).abs() < 1.0e-14);
    
            let parameters = model.sodium;
            let rate =
                |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                    let x = (voltage_mv - half_voltage_mv) / slope_mv;
                    let scale = prefactor.per_millivolt_per_ms * slope_mv;
                    if x == 0.0 {
                        scale
                    } else {
                        scale * x / -(-x).exp_m1()
                    }
                };
            let independent_rates = |voltage_mv: f64| {
                let alpha_m = rate(
                    voltage_mv,
                    parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                let beta_m = rate(
                    -voltage_mv,
                    -parameters.activation_rate_half_voltage_mv,
                    parameters.activation_rate,
                    parameters.activation_rate_slope_mv,
                );
                let alpha_h = rate(
                    voltage_mv,
                    parameters.inactivation_rate_half_voltage_mv,
                    parameters.inactivation_rate,
                    parameters.inactivation_rate_slope_mv,
                );
                let beta_h = rate(
                    -voltage_mv,
                    -parameters.recovery_rate_half_voltage_mv,
                    parameters.recovery_rate,
                    parameters.recovery_rate_slope_mv,
                );
                (
                    GateRates {
                        steady_state: super::sigmoid(
                            (voltage_mv - parameters.activation_half_voltage_mv)
                                / parameters.activation_slope_mv,
                        ),
                        time_constant_ms: 1.0 / (alpha_m + beta_m),
                    },
                    GateRates {
                        steady_state: super::sigmoid(
                            (parameters.inactivation_half_voltage_mv - voltage_mv)
                                / parameters.inactivation_slope_mv,
                        ),
                        time_constant_ms: 1.0 / (alpha_h + beta_h),
                    },
                )
            };
            let advance = |gate: f64, rates: GateRates, duration_ms: f64| {
                rates.steady_state
                    + (gate - rates.steady_state) * (-duration_ms / rates.time_constant_ms).exp()
            };
    
            // The source INITIAL state is at the -120-mV holding voltage. The
            // two-millisecond prepulse therefore leaves both gates at their
            // steady states before the ten-millisecond test command.
            let (hold_m, hold_h) = independent_rates(-120.0);
            let mut m = hold_m.steady_state;
            let mut h = hold_h.steady_state;
            m = advance(m, hold_m, 2.0);
            h = advance(h, hold_h, 2.0);
            assert!((m - hold_m.steady_state).abs() < 1.0e-14);
            assert!((h - hold_h.steady_state).abs() < 1.0e-14);
    
            for index in 0..=18 {
                let test_voltage_mv = -80.0 + index as f64 * 5.0;
                let (m_rates, h_rates) = independent_rates(test_voltage_mv);
                let expected_m = advance(m, m_rates, 10.0);
                let expected_h = advance(h, h_rates, 10.0);
    
                let model_rates = model.sodium_rates(test_voltage_mv).unwrap();
                let actual_m = advance(m, model_rates.activation, 10.0);
                let actual_h = advance(h, model_rates.inactivation, 10.0);
    
                assert!(
                    (actual_m - expected_m).abs() < 1.0e-13,
                    "Na m-gate voltage-clamp endpoint mismatch at {test_voltage_mv} mV"
                );
                assert!(
                    (actual_h - expected_h).abs() < 1.0e-13,
                    "Na h-gate voltage-clamp endpoint mismatch at {test_voltage_mv} mV"
                );
                assert_eq!(model_rates.activation.steady_state, m_rates.steady_state);
                assert_eq!(model_rates.inactivation.steady_state, h_rates.steady_state);
                assert!(
                    (model_rates.activation.time_constant_ms - m_rates.time_constant_ms).abs()
                        < 1.0e-12
                );
                assert!(
                    (model_rates.inactivation.time_constant_ms - h_rates.time_constant_ms).abs()
                        < 1.0e-12
                );
            }
        }
    
        #[test]
        fn na_voltage_clamp_inactivation_prepulse_replays_human_availability_at_25c() {
            // The deposited Na_IV_inact protocol uses 25°C, dt=0.005 ms:
            // 1 ms at -70 mV, 50 ms at a conditioning voltage (-105..-47 mV
            // in 2-mV steps), then a -10-mV test pulse. No -10-mV current-clamp
            // voltage-shift correction is used in this pure voltage-clamp path.
            let mut model = wilbers_model();
            model.temperature_celsius = 25.0;
            model.voltage_shift_mv = 0.0;
    
            let parameters = model.sodium;
            let source_rate =
                |voltage_mv: f64, half_voltage_mv: f64, prefactor: RatePrefactor, slope_mv: f64| {
                let x = (voltage_mv - half_voltage_mv) / slope_mv;
                let limit = prefactor.per_millivolt_per_ms * slope_mv;
                if x == 0.0 {
                    limit
                } else {
                    limit * x / -(-x).exp_m1()
                }
            };
        let source_rates = |voltage_mv: f64| {
            let alpha_m = source_rate(
                voltage_mv,
                parameters.activation_rate_half_voltage_mv,
                parameters.activation_rate,
                parameters.activation_rate_slope_mv,
            );
            let beta_m = source_rate(
                -voltage_mv,
                -parameters.activation_rate_half_voltage_mv,
                parameters.activation_rate,
                parameters.activation_rate_slope_mv,
            );
            let alpha_h = source_rate(
                voltage_mv,
                parameters.inactivation_rate_half_voltage_mv,
                parameters.inactivation_rate,
                parameters.inactivation_rate_slope_mv,
            );
            let beta_h = source_rate(
                -voltage_mv,
                -parameters.recovery_rate_half_voltage_mv,
                parameters.recovery_rate,
                parameters.recovery_rate_slope_mv,
            );
            (
                GateRates {
                    steady_state: super::sigmoid(
                        (voltage_mv - parameters.activation_half_voltage_mv)
                            / parameters.activation_slope_mv,
                    ),
                    time_constant_ms: 1.0 / (alpha_m + beta_m),
                },
                GateRates {
                    steady_state: super::sigmoid(
                        (parameters.inactivation_half_voltage_mv - voltage_mv)
                            / parameters.inactivation_slope_mv,
                    ),
                    time_constant_ms: 1.0 / (alpha_h + beta_h),
                },
            )
        };
        let advance = |gate: f64, rates: GateRates, duration_ms: f64| {
            rates.steady_state
                + (gate - rates.steady_state) * (-duration_ms / rates.time_constant_ms).exp()
        };

        let (initial_m_rates, initial_h_rates) = source_rates(-70.0);
        for index in 0..30 {
            let conditioning_voltage_mv = -105.0 + index as f64 * 2.0;
            let (conditioning_m_rates, conditioning_h_rates) =
                source_rates(conditioning_voltage_mv);
            let (test_m_rates, test_h_rates) = source_rates(-10.0);

            // Initial() places m/h at steady state at the -70-mV holding
            // potential. The 1-ms initial segment therefore preserves them.
            let mut expected_m = initial_m_rates.steady_state;
            let mut expected_h = initial_h_rates.steady_state;
            expected_m = advance(expected_m, initial_m_rates, 1.0);
            expected_h = advance(expected_h, initial_h_rates, 1.0);

            // Apply the 50-ms conditioning prepulse exactly, then evaluate
            // the source's 5-ms current-measurement window in the test step.
            expected_m = advance(expected_m, conditioning_m_rates, 50.0);
            expected_h = advance(expected_h, conditioning_h_rates, 50.0);
            expected_m = advance(expected_m, test_m_rates, 5.0);
            expected_h = advance(expected_h, test_h_rates, 5.0);

            let model_initial = model
                .initial_state(Volts::from_millivolts(-70.0).unwrap())
                .unwrap();
            let mut actual_m = model_initial.sodium_activation();
            let mut actual_h = model_initial.sodium_inactivation();
            let initial_rates = model.sodium_rates(-70.0).unwrap();
            actual_m = advance(actual_m, initial_rates.activation, 1.0);
            actual_h = advance(actual_h, initial_rates.inactivation, 1.0);
            let conditioning_rates = model.sodium_rates(conditioning_voltage_mv).unwrap();
            actual_m = advance(actual_m, conditioning_rates.activation, 50.0);
            actual_h = advance(actual_h, conditioning_rates.inactivation, 50.0);
            let test_rates = model.sodium_rates(-10.0).unwrap();
            actual_m = advance(actual_m, test_rates.activation, 5.0);
            actual_h = advance(actual_h, test_rates.inactivation, 5.0);

            assert!(
                (actual_m - expected_m).abs() < 1.0e-13,
                "Na m-gate inactivation-protocol endpoint mismatch after {conditioning_voltage_mv} mV"
            );
            assert!(
                (actual_h - expected_h).abs() < 1.0e-13,
                "Na h-gate inactivation-protocol endpoint mismatch after {conditioning_voltage_mv} mV"
            );
            assert_eq!(model.sodium_temperature_factor().unwrap(), 1.0);
        }
    }

    #[test]
    fn channel_temperature_scaling_matches_deposited_rate_contract() {
        let base_model = wilbers_model();
        let voltage_mv = -60.0;

        // The deposited pure Na mechanism uses temp=25°C and Q10=2.3.
        let mut sodium_reference_model = base_model;
        sodium_reference_model.temperature_celsius = 25.0;
        let sodium_reference = sodium_reference_model.sodium_rates(voltage_mv).unwrap();

        // The deposited pure K mechanism uses temp=34°C and Q10=2.3.
        let mut potassium_reference_model = base_model;
        potassium_reference_model.temperature_celsius = 34.0;
        let potassium_reference_recovery = potassium_reference_model
            .potassium_rates(voltage_mv, 0.0)
            .unwrap();
        let potassium_reference_inactivation = potassium_reference_model
            .potassium_rates(voltage_mv, 1.0)
            .unwrap();

        // This grid includes both channel-specific source reference temperatures
        // and the 34°C current-clamp operating point. It checks the deposited
        // Q10 equations; it is not evidence that the same Q10 is biologically
        // valid across this entire temperature interval.
        for temperature_celsius in [20.0, 25.0, 30.0, 34.0, 37.0] {
            let mut model = base_model;
            model.temperature_celsius = temperature_celsius;

            let sodium_factor = model.sodium_temperature_factor().unwrap();
            let potassium_factor = model.potassium_temperature_factor().unwrap();
            let expected_sodium_factor = 2.3_f64.powf((temperature_celsius - 25.0) / 10.0);
            let expected_potassium_factor = 2.3_f64.powf((temperature_celsius - 34.0) / 10.0);
            assert!(
                (sodium_factor - expected_sodium_factor).abs() < 1.0e-12,
                "Na Q10 factor mismatch at {temperature_celsius}°C"
            );
            assert!(
                (potassium_factor - expected_potassium_factor).abs() < 1.0e-12,
                "K Q10 factor mismatch at {temperature_celsius}°C"
            );

            let sodium = model.sodium_rates(voltage_mv).unwrap();
            assert!(
                (sodium.activation.time_constant_ms * sodium_factor
                    - sodium_reference.activation.time_constant_ms)
                    .abs()
                    < 1.0e-12,
                "Na activation tau did not scale inversely with Q10 at {temperature_celsius}°C"
            );
            assert!(
                (sodium.inactivation.time_constant_ms * sodium_factor
                    - sodium_reference.inactivation.time_constant_ms)
                    .abs()
                    < 1.0e-12,
                "Na inactivation tau did not scale inversely with Q10 at {temperature_celsius}°C"
            );
            assert_eq!(
                sodium.activation.steady_state,
                sodium_reference.activation.steady_state
            );
            assert_eq!(
                sodium.inactivation.steady_state,
                sodium_reference.inactivation.steady_state
            );

            let potassium_recovery = model.potassium_rates(voltage_mv, 0.0).unwrap();
            let potassium_inactivation = model.potassium_rates(voltage_mv, 1.0).unwrap();
            assert!(
                (potassium_recovery.activation.time_constant_ms * potassium_factor
                    - potassium_reference_recovery.activation.time_constant_ms)
                    .abs()
                    < 1.0e-12,
                "K activation tau did not scale inversely with Q10 at {temperature_celsius}°C"
            );
            assert!(
                (potassium_recovery.fast_inactivation.time_constant_ms * potassium_factor
                    - potassium_reference_recovery.fast_inactivation.time_constant_ms)
                    .abs()
                    < 1.0e-12,
                "K fast-inactivation tau did not scale inversely with Q10 at {temperature_celsius}°C"
            );
            assert!(
                (potassium_inactivation.fast_inactivation.time_constant_ms * potassium_factor
                    - potassium_reference_inactivation.fast_inactivation.time_constant_ms)
                    .abs()
                    < 1.0e-12,
                "K fast-inactivation tau in the inactivation branch did not scale at {temperature_celsius}°C"
            );
            assert_eq!(
                potassium_recovery.activation.steady_state,
                potassium_reference_recovery.activation.steady_state
            );
            assert_eq!(
                potassium_recovery.fast_inactivation.steady_state,
                potassium_reference_recovery.fast_inactivation.steady_state
            );
            assert_eq!(
                potassium_inactivation.slow_inactivation_time_constant_ms,
                450.0
            );
            assert_eq!(
                potassium_recovery.slow_inactivation_time_constant_ms,
                2789.7929428108187
            );
        }
    }

    #[test]
    fn temperature_adjustment_scales_sodium_conductance_but_not_potassium_or_leak() {
        let base_model = wilbers_model();
        let initial_conditions =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-60.0).unwrap());
        let zero_current = Amperes::from_amperes(0.0).unwrap();

        // Use the Na reference temperature as the conductance comparison point.
        // At identical voltage and gate state, the deposited Na equation has
        // gNa = T_adj * gbar * m^3 * h, whereas K has no T_adj multiplier on gbar.
        let mut reference_model = base_model;
        reference_model.temperature_celsius = 25.0;
        let reference_simulation =
            HumanL23SingleCompartmentSimulation::new(reference_model, initial_conditions).unwrap();
        let reference_state = reference_simulation.state();
        let reference_balance = reference_simulation.current_balance(zero_current).unwrap();

        assert!(reference_balance.sodium_current_density_a_per_m2().abs() > 1.0e-12);
        assert!(reference_balance.potassium_current_density_a_per_m2().abs() > 1.0e-12);
        assert!(reference_balance.leak_current_density_a_per_m2().abs() > 1.0e-12);

        for temperature_celsius in [20.0, 25.0, 30.0, 34.0, 37.0] {
            let mut model = base_model;
            model.temperature_celsius = temperature_celsius;
            let simulation =
                HumanL23SingleCompartmentSimulation::new(model, initial_conditions).unwrap();

            // Boltzmann steady states do not depend on temperature in these
            // deposited equations, so the initial gate vector is identical.
            assert_eq!(simulation.state(), reference_state);
            let balance = simulation.current_balance(zero_current).unwrap();
            let expected_sodium_factor = 2.3_f64.powf((temperature_celsius - 25.0) / 10.0);
            let observed_sodium_factor = balance.sodium_current_density_a_per_m2()
                / reference_balance.sodium_current_density_a_per_m2();

            assert!(
                (observed_sodium_factor - expected_sodium_factor).abs() < 1.0e-12,
                "Na maximal conductance/current did not scale by T_adj at {temperature_celsius}°C"
            );
            assert!(
                (balance.potassium_current_density_a_per_m2()
                    - reference_balance.potassium_current_density_a_per_m2())
                    .abs()
                    < 1.0e-12,
                "K maximal conductance was incorrectly temperature-scaled at {temperature_celsius}°C"
            );
            assert!(
                (balance.leak_current_density_a_per_m2()
                    - reference_balance.leak_current_density_a_per_m2())
                .abs()
                    < 1.0e-12,
                "Leak current changed with channel temperature at {temperature_celsius}°C"
            );
        }
    }

    #[test]
    fn author_current_clamp_rheobase_protocol_matches_neuron_reference_features() {
        let rheobase_pa = source_protocol_rheobase_pa();
        assert_eq!(rheobase_pa, 20.0);

        let (amplitude, source_features, crossings) = source_current_clamp_ap_features(rheobase_pa);
        assert_eq!(crossings, 1);

        let (threshold, upstroke, downstroke, ahp) = source_features
            .expect("the source 40-mV/ms threshold extractor is defined for this run");

        // Independent reference: unchanged Dataverse v3.0 current-clamp
        // NMODL and cc_tools.py, compiled/executed with NEURON 9.0.2.
        // These tolerances cover the measured RK4-vs-cnexp differences;
        // they are not biological uncertainty intervals.
        assert!((amplitude - 49.743_162_123_837_09).abs() <= 1.2);
        assert!((threshold - (-39.997_188_687_643_36)).abs() <= 0.2);
        assert!((upstroke - 414.571_518_695_368_8).abs() <= 8.0);
        assert!((downstroke - (-73.026_082_189_255_53)).abs() <= 3.0);
        assert!((ahp - (-69.604_161_439_013_38)).abs() <= 0.1);
    }

    #[test]
    fn current_clamp_fit_generates_one_spike_with_published_waveform_scale() {
        let model = wilbers_model();
        let mut simulation = HumanL23SingleCompartmentSimulation::new(
            model,
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap()),
        )
        .unwrap();
        let dt = SimDuration::from_microseconds(20).unwrap();
        let current = Amperes::from_picoamperes(25.0).unwrap();
        let zero = Amperes::from_amperes(0.0).unwrap();
        let mut trace = Vec::new();

        for index in 0..500 {
            let injected = if (50..200).contains(&index) {
                current
            } else {
                zero
            };
            let state = simulation.step(dt, injected).unwrap();
            trace.push(state.voltage().as_volts() * 1_000.0);
        }

        let peak_index = trace
            .iter()
            .enumerate()
            .max_by(|left, right| left.1.total_cmp(right.1))
            .unwrap()
            .0;
        let peak = trace[peak_index];
        let derivatives: Vec<f64> = trace
            .windows(2)
            .map(|pair| (pair[1] - pair[0]) / 0.02)
            .collect();
        let max_derivative_index = derivatives[..peak_index]
            .iter()
            .enumerate()
            .max_by(|left, right| left.1.total_cmp(right.1))
            .unwrap()
            .0;
        let threshold_index = derivatives[..max_derivative_index]
            .iter()
            .rposition(|rate| *rate < 40.0)
            .unwrap()
            + 1;
        let threshold = trace[threshold_index];
        let upstroke_30 = trace[..peak_index]
            .iter()
            .rposition(|voltage| *voltage < threshold + (peak - threshold) * 0.3)
            .unwrap()
            + 1;
        let upstroke_70 = trace[..peak_index]
            .iter()
            .rposition(|voltage| *voltage < threshold + (peak - threshold) * 0.7)
            .unwrap()
            + 1;
        let upstroke = derivatives[upstroke_30..upstroke_70].iter().sum::<f64>()
            / (upstroke_70 - upstroke_30) as f64;

        let downstroke_30 = trace[peak_index..]
            .iter()
            .rposition(|voltage| *voltage > threshold + (peak - threshold) * 0.7)
            .unwrap()
            + peak_index
            + 1;
        let downstroke_70 = trace[peak_index..]
            .iter()
            .rposition(|voltage| *voltage > threshold + (peak - threshold) * 0.3)
            .unwrap()
            + peak_index
            + 1;
        let downstroke = derivatives[downstroke_30..downstroke_70]
            .iter()
            .sum::<f64>()
            / (downstroke_70 - downstroke_30) as f64;

        let spike_crossings = trace
            .windows(2)
            .filter(|pair| pair[0] < 0.0 && pair[1] >= 0.0)
            .count();
        assert!((48.0..=53.0).contains(&peak));
        assert!((360.0..=480.0).contains(&upstroke));
        assert!((60.0..=90.0).contains(&downstroke.abs()));
        assert_eq!(spike_crossings, 1);
        assert!(trace.last().copied().unwrap() < -55.0);
    }

    #[test]
    fn smaller_integration_steps_converge_to_the_same_patch_response() {
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let coarse_model = wilbers_model();
        let fine_model =
            coarse_model.with_max_internal_step(SimDuration::from_microseconds(10).unwrap());
        let mut coarse = HumanL23SingleCompartmentSimulation::new(coarse_model, initial).unwrap();
        let mut fine = HumanL23SingleCompartmentSimulation::new(fine_model, initial).unwrap();
        let current = Amperes::from_picoamperes(25.0).unwrap();
        let zero = Amperes::from_amperes(0.0).unwrap();
        let coarse_dt = SimDuration::from_microseconds(20).unwrap();
        let fine_dt = SimDuration::from_microseconds(10).unwrap();
        let mut coarse_peak: f64 = -100.0;
        let mut fine_peak: f64 = -100.0;

        for index in 0..500 {
            let injected = if (50..200).contains(&index) {
                current
            } else {
                zero
            };
            coarse_peak = coarse_peak.max(
                coarse
                    .step(coarse_dt, injected)
                    .unwrap()
                    .voltage()
                    .as_volts(),
            );
            for _ in 0..2 {
                fine_peak =
                    fine_peak.max(fine.step(fine_dt, injected).unwrap().voltage().as_volts());
            }
        }

        assert!((coarse_peak - fine_peak).abs() < 5.0e-4);
        assert!(
            (coarse.state().voltage().as_volts() - fine.state().voltage().as_volts()).abs()
                < 5.0e-4
        );
    }

    #[test]
    fn oversized_step_and_numerical_failure_leave_state_unchanged() {
        let model = wilbers_model();
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial).unwrap();
        let before = simulation.state();

        let too_large = simulation.step(
            SimDuration::from_milliseconds(1).unwrap(),
            Amperes::from_amperes(0.0).unwrap(),
        );
        assert!(matches!(
            too_large,
            Err(SimulationError::OutOfRangeValue { .. })
        ));
        assert_eq!(simulation.state(), before);

        let overflow = simulation.step(
            SimDuration::from_microseconds(20).unwrap(),
            Amperes::from_amperes(1.0e308).unwrap(),
        );
        assert_eq!(overflow, Err(SimulationError::NumericalOverflow));
        assert_eq!(simulation.state(), before);
    }

    #[test]
    fn reset_restores_the_initial_voltage_gates_and_clock() {
        let model = wilbers_model();
        let initial =
            HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0).unwrap());
        let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial).unwrap();
        let before = simulation.state();
        simulation
            .step(
                SimDuration::from_microseconds(20).unwrap(),
                Amperes::from_picoamperes(25.0).unwrap(),
            )
            .unwrap();
        simulation.reset();
        assert_eq!(simulation.state(), before);
        assert_eq!(simulation.state().time(), SimTime::ZERO);
    }
}
