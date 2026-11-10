use crate::SimulationError;

/// Integer simulation timestamp in nanoseconds.
///
/// Integer clock storage avoids cumulative floating-point time drift. Physical
/// differential equations convert a step duration to seconds at integration.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct SimTime(u64);

impl SimTime {
    pub const ZERO: Self = Self(0);

    pub const fn from_nanoseconds(nanoseconds: u64) -> Self {
        Self(nanoseconds)
    }

    pub const fn as_nanoseconds(self) -> u64 {
        self.0
    }

    pub fn checked_add(self, duration: SimDuration) -> Result<Self, SimulationError> {
        self.0
            .checked_add(duration.0)
            .map(Self)
            .ok_or(SimulationError::TimeOverflow)
    }
}

/// Positive fixed-step duration represented as an integer number of nanoseconds.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct SimDuration(u64);

impl SimDuration {
    pub fn from_nanoseconds(nanoseconds: u64) -> Result<Self, SimulationError> {
        if nanoseconds == 0 {
            return Err(SimulationError::ZeroDuration);
        }
        Ok(Self(nanoseconds))
    }

    pub fn from_microseconds(microseconds: u64) -> Result<Self, SimulationError> {
        let nanoseconds = microseconds
            .checked_mul(1_000)
            .ok_or(SimulationError::TimeOverflow)?;
        Self::from_nanoseconds(nanoseconds)
    }

    pub fn from_milliseconds(milliseconds: u64) -> Result<Self, SimulationError> {
        let nanoseconds = milliseconds
            .checked_mul(1_000_000)
            .ok_or(SimulationError::TimeOverflow)?;
        Self::from_nanoseconds(nanoseconds)
    }

    pub const fn as_nanoseconds(self) -> u64 {
        self.0
    }

    pub fn as_seconds(self) -> f64 {
        self.0 as f64 * 1.0e-9
    }
}

#[cfg(test)]
mod tests {
    use super::{SimDuration, SimTime};
    use crate::SimulationError;

    #[test]
    fn duration_conversions_preserve_integer_clock_units() {
        let duration = SimDuration::from_milliseconds(2).unwrap();
        assert_eq!(duration.as_nanoseconds(), 2_000_000);
        assert!((duration.as_seconds() - 0.002).abs() < f64::EPSILON);
    }

    #[test]
    fn zero_duration_is_rejected() {
        assert_eq!(
            SimDuration::from_nanoseconds(0),
            Err(SimulationError::ZeroDuration)
        );
    }

    #[test]
    fn clock_overflow_is_reported() {
        let time = SimTime::from_nanoseconds(u64::MAX);
        let duration = SimDuration::from_nanoseconds(1).unwrap();
        assert_eq!(
            time.checked_add(duration),
            Err(SimulationError::TimeOverflow)
        );
    }
}
