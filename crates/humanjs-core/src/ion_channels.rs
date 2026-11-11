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

    /// Published human L2/L3 current-clamp fit from Wilbers et al. (2023).
    ///
    /// The conductance densities (114.48 and 29.05 pS/μm²) are fitted model
    /// values calibrated against cross-species mean AP features, not direct
    /// human nucleated-patch conductance measurements.
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

        let ionic_current_density = g_na * (voltage_v - self.sodium_reversal.as_volts())
            + g_k * (voltage_v - self.potassium_reversal.as_volts())
            + self.leak_conductance_density.as_siemens_per_square_meter()
                * (voltage_v - self.leak_reversal.as_volts());
        let injected_current_density =
            injected_current.as_amperes() / self.surface_area.as_square_meters();
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
        let k1 = self.model.derivatives(y, injected_current)?;
        let k2 = self
            .model
            .derivatives(add_scaled(y, k1, dt * 0.5), injected_current)?;
        let k3 = self
            .model
            .derivatives(add_scaled(y, k2, dt * 0.5), injected_current)?;
        let k4 = self
            .model
            .derivatives(add_scaled(y, k3, dt), injected_current)?;

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
        HumanL23SingleCompartmentModel, HumanL23SingleCompartmentSimulation, RatePrefactor,
    };
    use crate::{Amperes, SimDuration, SimTime, SimulationError, Volts};

    fn wilbers_model() -> super::HumanL23SingleCompartmentModel {
        super::HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit().unwrap()
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
        for step in 1..=5_000 {
            let conductance = advance_k_clamp_step(model, &mut gates, test_voltage_mv, 0.1);
            let time_ms = 20.0 + step as f64 * 0.1;
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
    fn channel_temperature_scaling_matches_the_deposited_mechanisms() {
        let model = wilbers_model();
        let sodium = model.sodium_temperature_factor().unwrap();
        let potassium = model.potassium_temperature_factor().unwrap();

        assert!((sodium - 2.3_f64.powf(0.9)).abs() < 1.0e-12);
        assert!((potassium - 1.0).abs() < 1.0e-12);
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
