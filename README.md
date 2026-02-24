# Amertat Short Technical Assignment

This repository simulates a planar two-link rotating mechanism and computes the signed axial force in link `AB` for all geometry-motion combinations.

## What is included
- `run_assignment.py`: entry-point script.
- `src/mechanism_assignment.py`: kinematics, dynamics, plotting, animation, and reporting.
- `scenarios.json`: example input with 5 geometry and 5 motion sets (25 combinations).
- `MODEL_APPROACH.md`: concise derivation and sign convention.

## Setup
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python run_assignment.py --scenarios scenarios.json --output-dir output --steps 721
```

Flags:
- `--scenarios`: path to the JSON input file that defines geometry and motion scenarios. Default: `scenarios.json`
- `--output-dir`: directory where plots, CSV, insight report, and animations are written. Default: `output`
- `--steps`: number of simulation samples over one full `AB` rotation (`0-360 deg`). Default: `721`

## Generated outputs
- `output/plots/*.png`: one line plot per combination.
- `output/all_combinations_grid.png`: comparison grid for all combinations.
- `output/summary_metrics.csv`: max tension/compression per combination.
- `output/engineering_insight.md`: extreme cases and primary parameter driver.
- `output/animations/*.gif`: mechanism animation for extreme case(s).

## Notes
- Units expected in `scenarios.json`: meters, kilograms, radians/second.
- `omega_bc_clockwise_rad_s` is a positive magnitude, internally applied as clockwise rotation.
