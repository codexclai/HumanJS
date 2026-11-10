use humanjs_core::{
    Amperes, MembranePatchInitialConditions, Ohms, PassiveMembraneModel,
    PassiveMembraneSimulation, SimDuration, SimTime, TimeConstant, Volts,
};

fn example_model() -> PassiveMembraneModel {
    // Explicit numerical fixture for equation tests, not a calibrated human default.
    PassiveMembraneModel::from_input_resistance_and_time_constant(
        Volts::from_millivolts(-68.0).unwrap(),
        Ohms::from_megohms(100.0).unwrap(),
        TimeConstant::from_milliseconds(20.0).unwrap(),
    )
    .unwrap()
}

fn simulation(initial_voltage_mv: f64) -> PassiveMembraneSimulation {
    PassiveMembraneSimulation::new(
        example_model(),
        MembranePatchInitialConditions::new(
            Volts::from_millivolts(initial_voltage_mv).unwrap(),
        ),
    )
}

#[test]
fn constant_current_step_matches_the_analytic_rc_solution() {
    let mut simulation = simulation(-68.0);
    let state = simulation
        .step(
            SimDuration::from_milliseconds(20).unwrap(),
            Amperes::from_picoamperes(100.0).unwrap(),
        )
        .unwrap();

    let expected_voltage = -0.068 + 0.010 * (1.0 - (-1.0_f64).exp());
    assert!((state.voltage().as_volts() - expected_voltage).abs() < 1.0e-12);
    assert_eq!(state.time(), SimTime::from_nanoseconds(20_000_000));
}

#[test]
fn voltage_relaxes_toward_zero_current_equilibrium() {
    let mut simulation = simulation(-50.0);
    let state = simulation
        .step(
            SimDuration::from_milliseconds(1_000).unwrap(),
            Amperes::from_picoamperes(0.0).unwrap(),
        )
        .unwrap();

    assert!((state.voltage().as_volts() - (-0.068)).abs() < 1.0e-10);
}

#[test]
fn constant_current_solution_is_consistent_across_step_partitioning() {
    let mut one_step = simulation(-68.0);
    let mut many_steps = simulation(-68.0);
    let current = Amperes::from_picoamperes(75.0).unwrap();

    let one_step_state = one_step
        .step(SimDuration::from_milliseconds(20).unwrap(), current)
        .unwrap();

    let small_step = SimDuration::from_milliseconds(1).unwrap();
    for _ in 0..20 {
        many_steps.step(small_step, current).unwrap();
    }

    assert!(
        (one_step_state.voltage().as_volts()
            - many_steps.state().voltage().as_volts())
            .abs()
            < 1.0e-12
    );
    assert_eq!(one_step.state().time(), many_steps.state().time());
}

#[test]
fn negative_current_hyperpolarizes_the_membrane() {
    let mut simulation = simulation(-68.0);
    let state = simulation
        .step(
            SimDuration::from_milliseconds(20).unwrap(),
            Amperes::from_picoamperes(-100.0).unwrap(),
        )
        .unwrap();

    assert!(state.voltage().as_volts() < -0.068);
}

#[test]
fn reset_restores_initial_conditions_and_clock() {
    let mut simulation = simulation(-68.0);
    simulation
        .step(
            SimDuration::from_milliseconds(5).unwrap(),
            Amperes::from_picoamperes(100.0).unwrap(),
        )
        .unwrap();

    simulation.reset();

    assert_eq!(
        simulation.state().voltage(),
        Volts::from_millivolts(-68.0).unwrap()
    );
    assert_eq!(simulation.state().time(), SimTime::ZERO);
}

#[test]
fn numerical_failure_does_not_partially_update_runtime_state() {
    use humanjs_core::{Farads, Siemens, SimulationError};

    let model = PassiveMembraneModel::new(
        Farads::from_farads(1.0e-300).unwrap(),
        Siemens::from_siemens(1.0e-300).unwrap(),
        Volts::from_volts(0.0).unwrap(),
    );
    let mut simulation = PassiveMembraneSimulation::new(
        model,
        MembranePatchInitialConditions::new(Volts::from_volts(0.0).unwrap()),
    );
    let before = simulation.state();

    let result = simulation.step(
        SimDuration::from_nanoseconds(1).unwrap(),
        Amperes::from_amperes(1.0e308).unwrap(),
    );

    assert_eq!(result, Err(SimulationError::NumericalOverflow));
    assert_eq!(simulation.state(), before);
}
