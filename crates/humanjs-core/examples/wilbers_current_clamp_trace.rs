use std::error::Error;

use humanjs_core::{
    Amperes, HumanL23SingleCompartmentInitialConditions, HumanL23SingleCompartmentModel,
    HumanL23SingleCompartmentSimulation, SimDuration, Volts,
};

fn voltage_crosses_threshold(current_pa: f64) -> Result<bool, Box<dyn Error>> {
    let dt = SimDuration::from_microseconds(100)?;
    let model = HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit()?
        .with_max_internal_step(dt);
    let initial = HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0)?);
    let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial)?;
    let current = Amperes::from_picoamperes(current_pa)?;
    let zero = Amperes::from_amperes(0.0)?;
    let threshold = Volts::from_millivolts(-20.0)?;

    // Deposited getrheo protocol: 7 ms total, 3-ms pulse after a 2-ms delay.
    for index in 0..70 {
        let before = simulation.state().voltage();
        let injected = if (20..50).contains(&index) {
            current
        } else {
            zero
        };
        let after = simulation.step(dt, injected)?.voltage();
        if before.as_volts() < threshold.as_volts() && after.as_volts() >= threshold.as_volts() {
            return Ok(true);
        }
    }
    Ok(false)
}

fn source_protocol_rheobase_pa() -> Result<f64, Box<dyn Error>> {
    // The first 100-pA trial is explicit in cc_tools.getrheo.
    let mut current_pa = 100.0;
    let mut found = voltage_crosses_threshold(current_pa)?;

    for increment_pa in [100.0, 10.0, 1.0] {
        let mut attempts = 0;
        while !found && attempts < 200 {
            current_pa += increment_pa;
            if current_pa > 20_000.0 {
                return Err("source rheobase search exceeded the 20-nA safety bound".into());
            }
            found = voltage_crosses_threshold(current_pa)?;
            attempts += 1;
        }
        if !found {
            return Err("source rheobase search did not converge".into());
        }
        if increment_pa > 1.0 {
            current_pa -= increment_pa;
            found = false;
        }
    }
    Ok(current_pa.round())
}

fn main() -> Result<(), Box<dyn Error>> {
    let mut arguments = std::env::args().skip(1);
    let mut step_us = 20;
    while let Some(argument) = arguments.next() {
        let value = if argument == "--step-us" {
            arguments.next()
        } else {
            argument.strip_prefix("--step-us=").map(str::to_owned)
        };
        if let Some(value) = value {
            step_us = value.parse::<u64>()?;
        } else {
            return Err(format!("unknown argument: {argument}").into());
        }
    }
    if step_us == 0 || 1_000 % step_us != 0 || 29_000 % step_us != 0 {
        return Err("--step-us must be positive and divide 1,000 and 29,000 microseconds".into());
    }

    let rheobase_pa = source_protocol_rheobase_pa()?;
    let dt = SimDuration::from_microseconds(step_us)?;
    let model = HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit()?
        .with_max_internal_step(dt);
    let initial = HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0)?);
    let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial)?;
    let current = Amperes::from_picoamperes(rheobase_pa * 1.5)?;
    let zero = Amperes::from_amperes(0.0)?;

    eprintln!(
        "# HumanJS Wilbers current-clamp trace: rheobase={rheobase_pa:.1} pA,          AP1 current={:.1} pA, dt={:.6} ms",
        rheobase_pa * 1.5,
        step_us as f64 / 1_000.0
    );
    println!("time_ms,voltage_mv");
    for index in 0..(29_000 / step_us) {
        let time_us = index * step_us;
        let injected = if (1_000..4_000).contains(&time_us) {
            current
        } else {
            zero
        };
        let state = simulation.step(dt, injected)?;
        let time_ms = (index + 1) as f64 * step_us as f64 / 1_000.0;
        println!("{time_ms:.6},{:.12}", state.voltage().as_volts() * 1_000.0);
    }
    Ok(())
}
