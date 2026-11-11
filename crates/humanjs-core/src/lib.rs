#![forbid(unsafe_code)]

//! The native HumanJS simulation core.
//!
//! The CPU implementation provides passive membrane, glutamatergic synapse,
//! and human L2/L3 single-compartment mechanisms. These are explicit
//! computational abstractions, not a complete neuron or brain.

mod error;
mod ion_channels;
mod membrane;
mod synapse;
mod time;
mod units;

pub use error::SimulationError;
pub use ion_channels::{
    HumanL23SingleCompartmentInitialConditions, HumanL23SingleCompartmentModel,
    HumanL23SingleCompartmentRuntimeState, HumanL23SingleCompartmentSimulation,
};
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
pub use units::{
    Amperes, Farads, FaradsPerSquareMeter, Ohms, Siemens, SiemensPerSquareMeter,
    SquareMeters, TimeConstant, Volts,
};
