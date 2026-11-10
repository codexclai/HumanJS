use std::fmt;

/// Errors returned by validated model construction and simulation operations.
#[derive(Debug, Clone, PartialEq)]
pub enum SimulationError {
    NonFiniteValue { field: &'static str, value: f64 },
    NonPositiveValue { field: &'static str, value: f64 },
    OutOfRangeValue {
        field: &'static str,
        value: f64,
        minimum: f64,
        maximum: f64,
    },
    InvalidKineticOrdering {
        rise_seconds: f64,
        decay_seconds: f64,
    },
    ZeroDuration,
    TimeOverflow,
    NumericalOverflow,
}

impl fmt::Display for SimulationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NonFiniteValue { field, value } => {
                write!(formatter, "{field} must be finite; received {value}")
            }
            Self::NonPositiveValue { field, value } => {
                write!(formatter, "{field} must be positive; received {value}")
            }
            Self::OutOfRangeValue {
                field,
                value,
                minimum,
                maximum,
            } => write!(
                formatter,
                "{field} must be between {minimum} and {maximum}; received {value}"
            ),
            Self::InvalidKineticOrdering {
                rise_seconds,
                decay_seconds,
            } => write!(
                formatter,
                "synaptic decay time ({decay_seconds} s) must exceed rise time ({rise_seconds} s)"
            ),
            Self::ZeroDuration => formatter.write_str("simulation duration must be positive"),
            Self::TimeOverflow => formatter.write_str("simulation clock overflowed"),
            Self::NumericalOverflow => {
                formatter.write_str("simulation step produced a non-finite result")
            }
        }
    }
}

impl std::error::Error for SimulationError {}

pub(crate) fn require_finite(field: &'static str, value: f64) -> Result<(), SimulationError> {
    if value.is_finite() {
        Ok(())
    } else {
        Err(SimulationError::NonFiniteValue { field, value })
    }
}

pub(crate) fn require_positive(field: &'static str, value: f64) -> Result<(), SimulationError> {
    require_finite(field, value)?;
    if value > 0.0 {
        Ok(())
    } else {
        Err(SimulationError::NonPositiveValue { field, value })
    }
}
