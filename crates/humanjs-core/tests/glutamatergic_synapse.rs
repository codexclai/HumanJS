use humanjs_core::{
    Amperes, Farads, GlutamatergicSynapseInitialConditions, GlutamatergicSynapseModel,
    GlutamatergicSynapseRuntimeState, MembranePatchInitialConditions, NmdaMagnesiumBlock,
    Ohms, PassiveMembraneModel, PassiveMembraneSimulation, PresynapticDepressionModel,
    SimDuration, Siemens, SimulationError, SynapticReceptorKinetics, TimeConstant, Volts,
};

fn human_l23_synapse_model() -> GlutamatergicSynapseModel {
    // Published fitted values for the Eyal et al. human L2/L3 model example.
    // These are explicit test parameters, not universal defaults.
    let ampa = SynapticReceptorKinetics::new(
        Siemens::from_nanosiemens(0.73).unwrap(),
        TimeConstant::from_milliseconds(0.3).unwrap(),
        TimeConstant::from_milliseconds(1.8).unwrap(),
    )
    .unwrap();
    let nmda = SynapticReceptorKinetics::new(
        Siemens::from_nanosiemens(1.31).unwrap(),
        TimeConstant::from_milliseconds(8.02).unwrap(),
        TimeConstant::from_milliseconds(34.99).unwrap(),
    )
    .unwrap();
    let magnesium = NmdaMagnesiumBlock::new(0.077, 1.0, 0.28).unwrap();
    let depression = PresynapticDepressionModel::new(
        0.45,
        TimeConstant::from_milliseconds(144.0).unwrap(),
    )
    .unwrap();

    GlutamatergicSynapseModel::new(
        ampa,
        nmda,
        magnesium,
        depression,
        Volts::from_millivolts(0.0).unwrap(),
    )
}

fn passive_membrane() -> PassiveMembraneSimulation {
    let membrane = PassiveMembraneModel::from_input_resistance_and_time_constant(
        Volts::from_millivolts(-68.0).unwrap(),
        Ohms::from_megohms(100.0).unwrap(),
        TimeConstant::from_milliseconds(20.0).unwrap(),
    )
    .unwrap();
    PassiveMembraneSimulation::new(
        membrane,
        MembranePatchInitialConditions::new(Volts::from_millivolts(-68.0).unwrap()),
    )
}

fn rested_synapse() -> GlutamatergicSynapseRuntimeState {
    GlutamatergicSynapseRuntimeState::from_initial_conditions(
        GlutamatergicSynapseInitialConditions::fully_recovered(),
    )
}

#[test]
fn single_glutamatergic_release_depolarizes_the_passive_membrane() {
    let model = human_l23_synapse_model();
    let mut synapse = rested_synapse();
    let release_scale = synapse.trigger_presynaptic_spike(model).unwrap();
    assert_eq!(release_scale, 1.0);

    let mut membrane = passive_membrane();
    let result = membrane
        .step_with_glutamatergic_synapse(
            SimDuration::from_milliseconds(1).unwrap(),
            Amperes::from_picoamperes(0.0).unwrap(),
            model,
            &mut synapse,
        )
        .unwrap();

    assert!(result.voltage().as_volts() > -0.068);
    assert!(synapse.available_resources() < 1.0);
    assert_eq!(result.time().as_nanoseconds(), 1_000_000);
}

#[test]
fn continuous_and_partitioned_synaptic_steps_converge() {
    let model = human_l23_synapse_model();
    let mut one_step = passive_membrane();
    let mut partitioned = passive_membrane();
    let mut one_synapse = rested_synapse();
    let mut many_synapse = rested_synapse();
    one_synapse.trigger_presynaptic_spike(model).unwrap();
    many_synapse.trigger_presynaptic_spike(model).unwrap();

    let one = one_step
        .step_with_glutamatergic_synapse(
            SimDuration::from_milliseconds(1).unwrap(),
            Amperes::from_picoamperes(0.0).unwrap(),
            model,
            &mut one_synapse,
        )
        .unwrap();

    let small_step = SimDuration::from_microseconds(100).unwrap();
    for _ in 0..10 {
        partitioned
            .step_with_glutamatergic_synapse(
                small_step,
                Amperes::from_picoamperes(0.0).unwrap(),
                model,
                &mut many_synapse,
            )
            .unwrap();
    }

    // The held interval-mean conductance and midpoint NMDA block are
    // approximations; reducing the integration interval must approach the
    // same response without assuming exact semigroup equivalence.
    assert!(
        (one.voltage().as_volts() - partitioned.state().voltage().as_volts()).abs()
            < 3.0e-4
    );
    assert!(
        (one_synapse.available_resources() - many_synapse.available_resources()).abs()
            < 1.0e-12
    );
}

#[test]
fn failed_coupled_step_does_not_partially_update_either_live_state() {
    let synapse_model = human_l23_synapse_model();
    let membrane_model = PassiveMembraneModel::new(
        Farads::from_farads(1.0e-300).unwrap(),
        Siemens::from_siemens(1.0e-300).unwrap(),
        Volts::from_volts(0.0).unwrap(),
    );
    let mut membrane = PassiveMembraneSimulation::new(
        membrane_model,
        MembranePatchInitialConditions::new(Volts::from_volts(0.0).unwrap()),
    );
    let mut synapse = rested_synapse();
    synapse.trigger_presynaptic_spike(synapse_model).unwrap();

    let membrane_before = membrane.state();
    let synapse_before = synapse;

    let result = membrane.step_with_glutamatergic_synapse(
        SimDuration::from_nanoseconds(1).unwrap(),
        Amperes::from_amperes(1.0e308).unwrap(),
        synapse_model,
        &mut synapse,
    );

    assert_eq!(result, Err(SimulationError::NumericalOverflow));
    assert_eq!(membrane.state(), membrane_before);
    assert_eq!(synapse, synapse_before);
}
