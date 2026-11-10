#![forbid(unsafe_code)]

//! The native HumanJS simulation core.
//!
//! The first implemented mechanism is deliberately narrow: a single passive
//! membrane patch driven by a piecewise-constant injected current. It is a
//! computational building block, not a complete neuron or brain model.

mod error;
mod membrane;
mod time;
mod units;

pub use error::SimulationError;
pub use membrane::{
    MembranePatchInitialConditions, MembranePatchRuntimeState, PassiveMembraneModel,
    PassiveMembraneSimulation,
};
pub use time::{SimDuration, SimTime};
pub use units::{Amperes, Farads, Ohms, Siemens, TimeConstant, Volts};
