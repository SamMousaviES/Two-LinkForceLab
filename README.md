# Two-LinkForceLab

This repository simulates a planar two-link rotating mechanism and computes the signed axial force in link `AB` for all geometry-motion combinations. It now supports a global gravity setting in `scenarios.json`, explicit gravity on/off labeling in all reports, and saved comparison exports for both gravity states.

## What Is Included
- `run_assignment.py`: command-line entry point for the full workflow.
- `src/mechanism_assignment.py`: scenario parsing, simulation, plotting, animation, and reporting.
- `scenarios.json`: example input with 5 geometry sets and 5 motion sets.
- `MODEL_APPROACH.md`: derivation, sign convention, and gravity-force model.
- `output/`: current generated outputs for the active `scenarios.json`.
- `output_gravity_on/`: saved reference export with gravity on.
- `output_gravity_off/`: saved reference export with gravity off.

## Setup
```bash
python -m pip install -r requirements.txt
```

## Input Schema
The input file is split into:
- `gravity`: one global gravity configuration for the full run
- `geometry_scenarios`: link lengths and point masses
- `motion_scenarios`: angular velocities for `AB` and `BC`

Example:
```json
{
  "gravity": {
    "enabled": false,
    "gravity_m_s2": 9.81
  },
  "geometry_scenarios": [
    {
      "name": "G1",
      "length_ab_m": 1.0,
      "length_bc_m": 0.6,
      "mass_b_kg": 3.0,
      "mass_c_kg": 1.0
    }
  ],
  "motion_scenarios": [
    {
      "name": "M1",
      "omega_ab_rad_s": 2.0,
      "omega_bc_clockwise_rad_s": 4.0
    }
  ]
}
```

Notes:
- `gravity.enabled: false` turns gravity off for the full scenario set.
- `gravity.gravity_m_s2` sets the gravity magnitude when gravity is enabled.
- Gravity acts in the `-y` direction.
- `omega_bc_clockwise_rad_s` is provided as a positive clockwise magnitude and is applied internally with clockwise sign.

## Run
Default run:
```bash
python run_assignment.py --scenarios scenarios.json --output-dir output --steps 721
```

Useful overrides:
```bash
python run_assignment.py --scenarios scenarios.json --output-dir output_gravity_off --steps 721 --gravity 0
python run_assignment.py --scenarios scenarios.json --output-dir output_gravity_on --steps 721 --gravity 9.81
```

Flags:
- `--scenarios`: path to the JSON input file. Default: `scenarios.json`
- `--output-dir`: destination folder for plots, animations, and reports. Default: `output`
- `--steps`: number of samples over one full `AB` rotation. Default: `721`
- `--gravity`: optional global gravity override in `m/s^2`. If omitted, the run uses the top-level JSON gravity setting. Use `0` to force gravity off.

## Generated Outputs
Each run produces:
- `plots/*.png`: one force-vs-angle plot per geometry-motion combination
- `all_combinations_grid.png`: a compact comparison grid across all cases
- `summary_metrics.csv`: peak tension/compression per case, including `gravity_status` and `gravity_m_s2`
- `engineering_insight.md`: global extremes, gravity state, and a simple driver ranking
- `animations/*.gif`: GIFs for the highest-tension and highest-compression cases

Gravity state is made explicit in:
- plot titles
- grid subplot titles
- GIF titles and overlays
- `summary_metrics.csv`
- `engineering_insight.md`
- terminal run summary

## Included Result Sets
The repository currently includes three output folders:
- `output/`: generated from the current `scenarios.json`
- `output_gravity_on/`: saved comparison export with gravity `ON (9.810 m/s^2)`
- `output_gravity_off/`: saved comparison export with gravity `OFF`

At the moment, the committed `scenarios.json` has:
```json
"gravity": {
  "enabled": false,
  "gravity_m_s2": 9.81
}
```

So the tracked `output/` folder currently corresponds to the gravity-off case.

## Modeling Notes
- Positive axial force means tension in link `AB`.
- Negative axial force means compression in link `AB`.
- The code applies gravity as a downward force vector `[0, -m g]`.
- With gravity toggled on, the axial-force result differs from the gravity-off case by the projection of that downward load onto the current `AB` direction.

## Quick File Guide
- `output/engineering_insight.md`: fastest high-level summary of the current run
- `output/summary_metrics.csv`: best machine-readable summary of all 25 cases
- `output_gravity_on/engineering_insight.md`: saved high-level summary for gravity on
- `output_gravity_off/engineering_insight.md`: saved high-level summary for gravity off

## Units
- length: meters
- mass: kilograms
- angular velocity: radians/second
- gravity: meters/second^2
