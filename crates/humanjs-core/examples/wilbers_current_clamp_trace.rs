use std::error::Error;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::PathBuf;

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
    let mut step_ns = 20_000_u64;
    let mut gates_output: Option<PathBuf> = None;
    let mut stages_output: Option<PathBuf> = None;
    let mut currents_output: Option<PathBuf> = None;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--step-us" => {
                let microseconds = arguments
                    .next()
                    .ok_or("--step-us requires a microsecond value")?
                    .parse::<u64>()?;
                step_ns = microseconds
                    .checked_mul(1_000)
                    .ok_or("the --step-us value overflows nanoseconds")?;
            }
            "--step-ns" => {
                step_ns = arguments
                    .next()
                    .ok_or("--step-ns requires a nanosecond value")?
                    .parse::<u64>()?;
            }
            "--gates-output" => {
                gates_output = Some(PathBuf::from(
                    arguments
                        .next()
                        .ok_or("--gates-output requires a file path")?,
                ));
            }
            "--stages-output" => {
                stages_output = Some(PathBuf::from(
                    arguments
                        .next()
                        .ok_or("--stages-output requires a file path")?,
                ));
            }
            "--currents-output" => {
                currents_output = Some(PathBuf::from(
                    arguments
                        .next()
                        .ok_or("--currents-output requires a file path")?,
                ));
            }
            _ => {
                if let Some(value) = argument.strip_prefix("--step-us=") {
                    let microseconds = value.parse::<u64>()?;
                    step_ns = microseconds
                        .checked_mul(1_000)
                        .ok_or("the --step-us value overflows nanoseconds")?;
                } else if let Some(value) = argument.strip_prefix("--step-ns=") {
                    step_ns = value.parse::<u64>()?;
                } else if let Some(path) = argument.strip_prefix("--gates-output=") {
                    gates_output = Some(PathBuf::from(path));
                } else if let Some(path) = argument.strip_prefix("--stages-output=") {
                    stages_output = Some(PathBuf::from(path));
                } else if let Some(path) = argument.strip_prefix("--currents-output=") {
                    currents_output = Some(PathBuf::from(path));
                } else {
                    return Err(format!("unknown argument: {argument}").into());
                }
            }
        }
    }
    const PULSE_START_NS: u64 = 1_000_000;
    const PULSE_END_NS: u64 = 4_000_000;
    const PROTOCOL_DURATION_NS: u64 = 29_000_000;
    if step_ns == 0
        || PULSE_START_NS % step_ns != 0
        || PULSE_END_NS % step_ns != 0
        || PROTOCOL_DURATION_NS % step_ns != 0
    {
        return Err(
            "--step-ns must be positive and divide the 1-ms pulse onset, 4-ms pulse offset, and 29-ms protocol duration".into(),
        );
    }

    let rheobase_pa = source_protocol_rheobase_pa()?;
    let dt = SimDuration::from_nanoseconds(step_ns)?;
    let model = HumanL23SingleCompartmentModel::wilbers_2023_human_l23_current_clamp_fit()?
        .with_max_internal_step(dt);
    let initial = HumanL23SingleCompartmentInitialConditions::new(Volts::from_millivolts(-70.0)?);
    let mut simulation = HumanL23SingleCompartmentSimulation::new(model, initial)?;
    let current = Amperes::from_picoamperes(rheobase_pa * 1.5)?;
    let zero = Amperes::from_amperes(0.0)?;
    let mut gates_writer = gates_output
        .map(File::create)
        .transpose()?
        .map(BufWriter::new);
    let mut stages_writer = stages_output
        .map(File::create)
        .transpose()?
        .map(BufWriter::new);
    let mut currents_writer = currents_output
        .map(File::create)
        .transpose()?
        .map(BufWriter::new);
    if let Some(writer) = gates_writer.as_mut() {
        writeln!(
            writer,
            "time_ms,sodium_activation,sodium_inactivation,potassium_activation,potassium_fast_inactivation,potassium_slow_inactivation"
        )?;
    }
    if let Some(writer) = stages_writer.as_mut() {
        writeln!(
            writer,
            "time_ms,stage_1_voltage_mv,stage_2_voltage_mv,stage_3_voltage_mv,stage_4_voltage_mv"
        )?;
    }
    if let Some(writer) = currents_writer.as_mut() {
        writeln!(writer, "time_ms,stage_1_na_a_per_m2,stage_1_k_a_per_m2,stage_1_leak_a_per_m2,stage_1_injected_a_per_m2,stage_1_dvdt_v_per_s,stage_2_na_a_per_m2,stage_2_k_a_per_m2,stage_2_leak_a_per_m2,stage_2_injected_a_per_m2,stage_2_dvdt_v_per_s,stage_3_na_a_per_m2,stage_3_k_a_per_m2,stage_3_leak_a_per_m2,stage_3_injected_a_per_m2,stage_3_dvdt_v_per_s,stage_4_na_a_per_m2,stage_4_k_a_per_m2,stage_4_leak_a_per_m2,stage_4_injected_a_per_m2,stage_4_dvdt_v_per_s,endpoint_na_a_per_m2,endpoint_k_a_per_m2,endpoint_leak_a_per_m2,endpoint_injected_a_per_m2,endpoint_dvdt_v_per_s")?;
    }

    eprintln!(
        "# HumanJS Wilbers current-clamp trace: rheobase={rheobase_pa:.1} pA, AP1 current={:.1} pA, dt={:.6} ms",
        rheobase_pa * 1.5,
        step_ns as f64 / 1_000_000.0
    );
    println!("time_ms,voltage_mv");
    for index in 0..(PROTOCOL_DURATION_NS / step_ns) {
        let interval_start_ns = index * step_ns;
        let injected = if (PULSE_START_NS..PULSE_END_NS).contains(&interval_start_ns) {
            current
        } else {
            zero
        };
        let (state, voltage_stages, current_stages) = if stages_writer.is_some()
            && currents_writer.is_some()
        {
            let (state, voltages, currents) =
                simulation.step_with_voltage_and_current_stages(dt, injected)?;
            (state, Some(voltages), Some(currents))
        } else if stages_writer.is_some() {
            let (state, voltages) = simulation.step_with_voltage_stages(dt, injected)?;
            (state, Some(voltages), None)
        } else if currents_writer.is_some() {
            let (state, currents) = simulation.step_with_current_balance_stages(dt, injected)?;
            (state, None, Some(currents))
        } else {
            (simulation.step(dt, injected)?, None, None)
        };
        let time_ms = (index + 1) as f64 * step_ns as f64 / 1_000_000.0;
        println!("{time_ms:.6},{:.12}", state.voltage().as_volts() * 1_000.0);
        if let Some(writer) = gates_writer.as_mut() {
            writeln!(
                writer,
                "{time_ms:.6},{:.12},{:.12},{:.12},{:.12},{:.12}",
                state.sodium_activation(),
                state.sodium_inactivation(),
                state.potassium_activation(),
                state.potassium_fast_inactivation(),
                state.potassium_slow_inactivation(),
            )?;
        }
        if let (Some(writer), Some(stages)) = (stages_writer.as_mut(), voltage_stages) {
            writeln!(
                writer,
                "{time_ms:.6},{:.12},{:.12},{:.12},{:.12}",
                stages[0].as_volts() * 1_000.0,
                stages[1].as_volts() * 1_000.0,
                stages[2].as_volts() * 1_000.0,
                stages[3].as_volts() * 1_000.0,
            )?;
        }
        if let (Some(writer), Some(stages)) = (currents_writer.as_mut(), current_stages) {
            write!(writer, "{time_ms:.6}")?;
            for stage in stages {
                write!(
                    writer,
                    ",{:.12},{:.12},{:.12},{:.12},{:.12}",
                    stage.sodium_current_density_a_per_m2(),
                    stage.potassium_current_density_a_per_m2(),
                    stage.leak_current_density_a_per_m2(),
                    stage.injected_current_density_a_per_m2(),
                    stage.voltage_derivative_v_per_s(),
                )?;
            }
            let endpoint = simulation.current_balance(injected)?;
            write!(
                writer,
                ",{:.12},{:.12},{:.12},{:.12},{:.12}",
                endpoint.sodium_current_density_a_per_m2(),
                endpoint.potassium_current_density_a_per_m2(),
                endpoint.leak_current_density_a_per_m2(),
                endpoint.injected_current_density_a_per_m2(),
                endpoint.voltage_derivative_v_per_s(),
            )?;
            writeln!(writer)?;
        }
    }
    if let Some(writer) = gates_writer.as_mut() {
        writer.flush()?;
    }
    if let Some(writer) = stages_writer.as_mut() {
        writer.flush()?;
    }
    if let Some(writer) = currents_writer.as_mut() {
        writer.flush()?;
    }
    Ok(())
}
