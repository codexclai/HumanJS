use crate::error::{require_finite, require_positive};
use crate::SimulationError;

/// Membrane potential or reversal potential, in volts.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Volts(f64);

impl Volts {
    pub fn from_volts(value: f64) -> Result<Self, SimulationError> {
        require_finite("voltage (V)", value)?;
        Ok(Self(value))
    }
    pub fn from_millivolts(value: f64) -> Result<Self, SimulationError> {
        Self::from_volts(value * 1.0e-3)
    }
    pub const fn as_volts(self) -> f64 {
        self.0
    }
}

/// Injected electrical current, in amperes. Negative current is permitted.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Amperes(f64);

impl Amperes {
    pub fn from_amperes(value: f64) -> Result<Self, SimulationError> {
        require_finite("current (A)", value)?;
        Ok(Self(value))
    }
    pub fn from_picoamperes(value: f64) -> Result<Self, SimulationError> {
        Self::from_amperes(value * 1.0e-12)
    }
    pub const fn as_amperes(self) -> f64 {
        self.0
    }
}

/// Total membrane capacitance, in farads.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Farads(f64);

impl Farads {
    pub fn from_farads(value: f64) -> Result<Self, SimulationError> {
        require_positive("capacitance (F)", value)?;
        Ok(Self(value))
    }
    pub fn from_picofarads(value: f64) -> Result<Self, SimulationError> {
        Self::from_farads(value * 1.0e-12)
    }
    pub const fn as_farads(self) -> f64 {
        self.0
    }
}

/// Total leak conductance, in siemens.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Siemens(f64);

impl Siemens {
    pub fn from_siemens(value: f64) -> Result<Self, SimulationError> {
        require_positive("conductance (S)", value)?;
        Ok(Self(value))
    }
    pub fn from_nanosiemens(value: f64) -> Result<Self, SimulationError> {
        Self::from_siemens(value * 1.0e-9)
    }
    pub const fn as_siemens(self) -> f64 {
        self.0
    }
}

/// Input resistance, in ohms.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Ohms(f64);

impl Ohms {
    pub fn from_ohms(value: f64) -> Result<Self, SimulationError> {
        require_positive("input resistance (ohm)", value)?;
        Ok(Self(value))
    }
    pub fn from_megohms(value: f64) -> Result<Self, SimulationError> {
        Self::from_ohms(value * 1.0e6)
    }
    pub const fn as_ohms(self) -> f64 {
        self.0
    }
}

/// Passive membrane time constant, in seconds.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TimeConstant(f64);

impl TimeConstant {
    pub fn from_seconds(value: f64) -> Result<Self, SimulationError> {
        require_positive("membrane time constant (s)", value)?;
        Ok(Self(value))
    }
    pub fn from_milliseconds(value: f64) -> Result<Self, SimulationError> {
        Self::from_seconds(value * 1.0e-3)
    }
    pub const fn as_seconds(self) -> f64 {
        self.0
    }
}

#[cfg(test)]
mod tests {
    use super::{Amperes, Farads, Ohms, Siemens, TimeConstant, Volts};
    use crate::SimulationError;

    #[test]
    fn membrane_density_units_convert_consistently_to_si() {
        use super::{FaradsPerSquareMeter, SiemensPerSquareMeter, SquareMeters};

        assert_eq!(
            SquareMeters::from_square_micrometers(314.0)
                .unwrap()
                .as_square_meters(),
            314.0e-12
        );
        assert_eq!(
            SiemensPerSquareMeter::from_picosiemens_per_square_micrometer(114.48)
                .unwrap()
                .as_siemens_per_square_meter(),
            114.48
        );
        assert_eq!(
            FaradsPerSquareMeter::from_microfarads_per_square_centimeter(1.0)
                .unwrap()
                .as_farads_per_square_meter(),
            0.01
        );
    }

    #[test]
    fn unit_conversions_are_consistent_with_si() {
        assert_eq!(Volts::from_millivolts(-70.0).unwrap().as_volts(), -0.07);
        assert_eq!(
            Amperes::from_picoamperes(250.0).unwrap().as_amperes(),
            250.0e-12
        );
        assert_eq!(
            Farads::from_picofarads(125.0).unwrap().as_farads(),
            125.0e-12
        );
        assert_eq!(Siemens::from_nanosiemens(4.0).unwrap().as_siemens(), 4.0e-9);
        assert_eq!(Ohms::from_megohms(2.0).unwrap().as_ohms(), 2.0e6);
        assert_eq!(
            TimeConstant::from_milliseconds(5.0).unwrap().as_seconds(),
            0.005
        );
    }

    #[test]
    fn positive_physical_parameters_reject_zero_and_negative_values() {
        assert_eq!(
            Farads::from_farads(0.0),
            Err(SimulationError::NonPositiveValue {
                field: "capacitance (F)",
                value: 0.0,
            })
        );
        assert!(Siemens::from_siemens(-1.0).is_err());
        assert!(Ohms::from_ohms(0.0).is_err());
        assert!(TimeConstant::from_seconds(-0.1).is_err());
    }

    #[test]
    fn quantities_reject_non_finite_values() {
        assert!(Volts::from_volts(f64::NAN).is_err());
        assert!(Amperes::from_amperes(f64::INFINITY).is_err());
        assert!(Farads::from_farads(f64::INFINITY).is_err());
    }
}


/// Surface area, in square metres.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SquareMeters(f64);

impl SquareMeters {
    pub fn from_square_meters(value: f64) -> Result<Self, SimulationError> {
        require_positive("surface area (m^2)", value)?;
        Ok(Self(value))
    }

    pub fn from_square_micrometers(value: f64) -> Result<Self, SimulationError> {
        Self::from_square_meters(value * 1.0e-12)
    }

    pub const fn as_square_meters(self) -> f64 {
        self.0
    }
}

/// Specific conductance, in siemens per square metre.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SiemensPerSquareMeter(f64);

impl SiemensPerSquareMeter {
    pub fn from_siemens_per_square_meter(value: f64) -> Result<Self, SimulationError> {
        require_positive("specific conductance (S/m^2)", value)?;
        Ok(Self(value))
    }

    /// Convert picosiemens per square micrometre to S/m^2.
    ///
    /// The numerical value is unchanged because 1 pS/μm² equals 1 S/m².
    pub fn from_picosiemens_per_square_micrometer(
        value: f64,
    ) -> Result<Self, SimulationError> {
        Self::from_siemens_per_square_meter(value)
    }

    pub const fn as_siemens_per_square_meter(self) -> f64 {
        self.0
    }
}

/// Specific membrane capacitance, in farads per square metre.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FaradsPerSquareMeter(f64);

impl FaradsPerSquareMeter {
    pub fn from_farads_per_square_meter(value: f64) -> Result<Self, SimulationError> {
        require_positive("specific capacitance (F/m^2)", value)?;
        Ok(Self(value))
    }

    /// Convert microfarads per square centimetre to F/m^2.
    pub fn from_microfarads_per_square_centimeter(
        value: f64,
    ) -> Result<Self, SimulationError> {
        Self::from_farads_per_square_meter(value * 1.0e-2)
    }

    pub const fn as_farads_per_square_meter(self) -> f64 {
        self.0
    }
}
