from __future__ import annotations

import argparse
from pathlib import Path

from src.mechanism_assignment import (
    animate_mechanism,
    find_extremes,
    load_scenarios,
    plot_comparison_grid,
    plot_single_curve,
    simulate_all,
    write_engineering_insight,
    write_metrics_csv,
)


def parse_args() -> argparse.Namespace:
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
        "--animation-cycles",
        type=int,
        default=1,
        help="How many full mechanism cycles to include in each GIF.",
    )
    parser.add_argument(
        "--animation-fps",
        type=int,
        default=25,
        help="Frame rate for saved GIF animations.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenario_path = Path(args.scenarios).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    geometries, motions = load_scenarios(scenario_path)
    results = simulate_all(geometries=geometries, motions=motions, num_steps=args.steps)

    max_tension_result, max_compression_result = find_extremes(results)

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

    plot_comparison_grid(
        results=results,
        geometries=geometries,
        motions=motions,
        output_path=output_dir / "all_combinations_grid.png",
        max_tension_id=max_tension_result.combo_id,
        max_compression_id=max_compression_result.combo_id,
    )

    write_metrics_csv(results, output_path=output_dir / "summary_metrics.csv")
    write_engineering_insight(results, output_path=output_dir / "engineering_insight.md")

    animations_dir = output_dir / "animations"
    animate_mechanism(
        result=max_tension_result,
        output_path=animations_dir / f"{max_tension_result.combo_id}_max_tension_long.gif",
        title=f"Max tension case: {max_tension_result.combo_id}",
        cycles=args.animation_cycles,
        fps=args.animation_fps,
    )
    if max_compression_result.combo_id != max_tension_result.combo_id:
        animate_mechanism(
            result=max_compression_result,
            output_path=animations_dir
            / f"{max_compression_result.combo_id}_max_compression_long.gif",
            title=f"Max compression case: {max_compression_result.combo_id}",
            cycles=args.animation_cycles,
            fps=args.animation_fps,
        )

    print(f"Completed {len(results)} simulations.")
    print(f"Output directory: {output_dir}")
    print(
        "Highest tensile case:",
        max_tension_result.combo_id,
        f"(max force = {max_tension_result.axial_force_ab.max():.3f} N)",
    )
    print(
        "Highest compressive case:",
        max_compression_result.combo_id,
        f"(min force = {max_compression_result.axial_force_ab.min():.3f} N)",
    )


if __name__ == "__main__":
    main()
