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
    // In the source expression, (V - th) / (1 - exp(-(V - th) / q))
    // is dimensionless because both numerator and denominator are voltages.
    // Therefore the published NMODL prefactor retains its declared ms^-1
    // dimension; no extra inverse-millivolt factor is introduced.
    per_ms: f64,
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
            per_ms: 0.2139849270413559,
        },
        inactivation_half_voltage_mv: -64.48,
        inactivation_slope_mv: 11.02,
        inactivation_rate_half_voltage_mv: -39.298676911255,
        recovery_rate_half_voltage_mv: -77.16674532461128,
        inactivation_rate_slope_mv: 7.21636386592805,
        recovery_rate_slope_mv: 4.749450048393884,
        inactivation_rate: RatePrefactor {
            per_ms: 0.0476391878313753,
        },
        recovery_rate: RatePrefactor {
            per_ms: 0.011951655023359499,
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
            per_ms: 0.018459250585411965,
        },
        inactivation_half_voltage_mv: -52.61,
        inactivation_slope_mv: 13.09,
        inactivation_rate_half_voltage_mv: 40.5659148938157,
        recovery_rate_half_voltage_mv: -75.93822659307075,
        inactivation_rate_slope_mv: 26.773929244740913,
        recovery_rate_slope_mv: 0.40183382749400054,
        inactivation_rate: RatePrefactor {
            per_ms: 0.0016901435659310753,
        },
        recovery_rate: RatePrefactor {
            per_ms: 0.0004968791312639546,
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
        "trap0 rate prefactor (/mV/ms)",
        prefactor.per_ms,
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
    let rate = prefactor.per_ms * slope_mv * ratio;
    require_positive("trap0 transition rate (ms^-1)", rate)
        .map_err(|_| SimulationError::NumericalOverflow)?;
    Ok(rate)
}

#[cfg(test)]
mod tests {
    use super::{
        trap0, HumanL23SingleCompartmentInitialConditions, HumanL23SingleCompartmentSimulation,
        RatePrefactor,
    };
    use crate::{Amperes, SimDuration, SimTime, SimulationError, Volts};

    fn wilbers_model() -> super::HumanL23SingleCompartmentModel {
        super::HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit().unwrap()
    }

    #[test]
    fn trap0_uses_the_analytic_limit_and_is_continuous() {
        let prefactor = RatePrefactor {
            per_ms: 0.2,
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
