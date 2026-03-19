from __future__ import annotations

"""Command-line entry point for the full assignment workflow.

This script orchestrates:
1) Loading scenarios.
2) Running all simulations.
3) Creating plots, summary files, and animations.
4) Printing a compact terminal summary.
"""

import argparse
from pathlib import Path

from src.mechanism_assignment import (
    animate_mechanism,
    find_extremes,
    format_gravity_state,
    load_scenarios,
    plot_comparison_grid,
    plot_single_curve,
    simulate_all,
    write_engineering_insight,
    write_metrics_csv,
)


def parse_args() -> argparse.Namespace:
    """Define and parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Amertat short technical assignment solver."
    )
    parser.add_argument(
        "--scenarios",
        default="scenarios.json",
        help="Path to JSON file containing geometry and motion scenarios.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where plots, animations, and summary files are generated.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=721,
        help="Number of simulation steps over 0-360 deg of AB.",
    )
    parser.add_argument(
        "--gravity",
        type=float,
        default=None,
        help=(
            "Optional global gravity override in m/s^2. "
            "If omitted, the run uses the top-level JSON gravity settings. "
            "Use 0 to force gravity off for all scenarios."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run the end-to-end simulation and reporting pipeline."""

    # Parse user-provided CLI options (or defaults).
    args = parse_args()
    if args.gravity is not None and args.gravity < 0.0:
        raise ValueError("--gravity must be >= 0.")

    # Resolve absolute paths for robustness across working directories.
    scenario_path = Path(args.scenarios).resolve()
    output_dir = Path(args.output_dir).resolve()

    # Ensure output directory exists before writing files.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all geometry and motion inputs from JSON.
    geometries, motions, gravity = load_scenarios(scenario_path)

    applied_gravity_m_s2 = gravity.applied_gravity_m_s2
    if args.gravity is not None:
        applied_gravity_m_s2 = args.gravity

    # Simulate every geometry-motion combination.
    results = simulate_all(
        geometries=geometries,
        motions=motions,
        num_steps=args.steps,
        gravity_m_s2=applied_gravity_m_s2,
    )

    # Find global tension/compression extreme cases across all combinations.
    max_tension_result, max_compression_result = find_extremes(results)

    # Generate one plot per combination, highlighting extremes with distinct colors.
    plots_dir = output_dir / "plots"
    for result in results:
        color = "steelblue"
        if result.combo_id == max_tension_result.combo_id:
            color = "crimson"
        elif result.combo_id == max_compression_result.combo_id:
            color = "royalblue"
        plot_single_curve(
            result=result,
            output_path=plots_dir / f"{result.combo_id}.png",
            color=color,
        )

    # Generate a compact grid figure with all combinations together.
    plot_comparison_grid(
        results=results,
        geometries=geometries,
        motions=motions,
        output_path=output_dir / "all_combinations_grid.png",
        max_tension_id=max_tension_result.combo_id,
        max_compression_id=max_compression_result.combo_id,
    )

    # Write machine-readable metrics and a short engineering narrative.
    write_metrics_csv(results, output_path=output_dir / "summary_metrics.csv")
    write_engineering_insight(results, output_path=output_dir / "engineering_insight.md")

    # Animate the max-tension case (always required).
    animations_dir = output_dir / "animations"
    animate_mechanism(
        result=max_tension_result,
        output_path=animations_dir / f"{max_tension_result.combo_id}_max_tension.gif",
        title=(
            f"Max tension case: {max_tension_result.combo_id}\n"
            f"Gravity {max_tension_result.gravity_label}"
        ),
    )

    # Animate max-compression only if it is a different case.
    if max_compression_result.combo_id != max_tension_result.combo_id:
        animate_mechanism(
            result=max_compression_result,
            output_path=animations_dir
            / f"{max_compression_result.combo_id}_max_compression.gif",
            title=(
                f"Max compression case: {max_compression_result.combo_id}\n"
                f"Gravity {max_compression_result.gravity_label}"
            ),
        )

    # Print quick run summary in terminal.
    print(f"Completed {len(results)} simulations.")
    print(f"Output directory: {output_dir}")
    if args.gravity is None:
        print(f"Gravity from scenarios.json: {format_gravity_state(applied_gravity_m_s2)}")
    else:
        print(f"Gravity override: {format_gravity_state(args.gravity)}")
    print(
        "Highest tensile case:",
        max_tension_result.combo_id,
        f"(max force = {max_tension_result.axial_force_ab.max():.3f} N, "
        f"gravity {max_tension_result.gravity_label})",
    )
    print(
        "Highest compressive case:",
        max_compression_result.combo_id,
        f"(min force = {max_compression_result.axial_force_ab.min():.3f} N, "
        f"gravity {max_compression_result.gravity_label})",
    )


if __name__ == "__main__":
    # Standard Python entry-point guard.
    main()
