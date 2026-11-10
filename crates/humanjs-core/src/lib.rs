#![forbid(unsafe_code)]

//! The native HumanJS simulation core.
//!
//! The first CPU implementation provides a passive membrane compartment
//! and a bounded glutamatergic synaptic conductance model. These components
//! are explicit computational abstractions, not a complete neuron or brain.

mod error;
mod membrane;
mod synapse;
mod time;
mod units;

pub use error::SimulationError;
pub use membrane::{
    MembranePatchInitialConditions, MembranePatchRuntimeState, PassiveMembraneModel,
    PassiveMembraneSimulation,
};
pub use synapse::{
    GlutamatergicSynapseInitialConditions, GlutamatergicSynapseModel,
    GlutamatergicSynapseRuntimeState, NmdaMagnesiumBlock, PresynapticDepressionModel,
    SynapticConductances, SynapticReceptorKinetics,
};
pub use time::{SimDuration, SimTime};
pub use units::{Amperes, Farads, Ohms, Siemens, TimeConstant, Volts};
