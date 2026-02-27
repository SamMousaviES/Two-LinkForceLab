from __future__ import annotations

"""Core mechanics, simulation, and reporting utilities for the assignment.

This module does four jobs:
1) Parse geometry/motion scenarios from JSON.
2) Simulate one full AB rotation for every geometry-motion combination.
3) Produce plots, CSV summaries, and text insight.
4) Create GIF animations for selected extreme cases.

Modeling assumptions match the assignment statement:
- Planar rigid links.
- Lumped masses at B and C.
- Constant angular velocities.
- No gravity/aerodynamic/deformation effects.
"""

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np


@dataclass(frozen=True)
class GeometryScenario:
    """One geometry case (lengths and masses)."""

    name: str
    length_ab: float
    length_bc: float
    mass_b: float
    mass_c: float


@dataclass(frozen=True)
class MotionScenario:
    """One motion case (angular speeds)."""

    name: str
    omega_ab: float
    omega_bc_clockwise: float


@dataclass
class SimulationResult:
    """Stores all time-history outputs for a single geometry-motion combination."""

    geometry_name: str
    motion_name: str
    length_ab: float
    length_bc: float
    mass_b: float
    mass_c: float
    omega_ab: float
    omega_bc_clockwise: float
    time: np.ndarray
    theta_deg: np.ndarray
    r_b: np.ndarray
    v_b: np.ndarray
    a_b: np.ndarray
    r_c: np.ndarray
    v_c: np.ndarray
    a_c: np.ndarray
    axial_force_ab: np.ndarray

    @property
    def combo_id(self) -> str:
        """Stable ID used in filenames/tables, e.g., G3__M2."""
        return f"{self.geometry_name}__{self.motion_name}"


def load_scenarios(path: Path) -> tuple[list[GeometryScenario], list[MotionScenario]]:
    """Read and validate scenario inputs from JSON.

    Expected JSON keys:
    - geometry_scenarios: list of geometry dictionaries
    - motion_scenarios: list of motion dictionaries
    """

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    # Pull arrays (fallback to empty list so we can raise explicit errors below).
    geometry_items = payload.get("geometry_scenarios", [])
    motion_items = payload.get("motion_scenarios", [])

    if not geometry_items:
        raise ValueError("No geometry scenarios found in scenarios file.")
    if not motion_items:
        raise ValueError("No motion scenarios found in scenarios file.")

    geometries: list[GeometryScenario] = []
    motions: list[MotionScenario] = []

    # Convert raw JSON rows into typed dataclasses and validate values.
    for item in geometry_items:
        scenario = GeometryScenario(
            name=item["name"],
            length_ab=float(item["length_ab_m"]),
            length_bc=float(item["length_bc_m"]),
            mass_b=float(item["mass_b_kg"]),
            mass_c=float(item["mass_c_kg"]),
        )
        _validate_geometry(scenario)
        geometries.append(scenario)

    for item in motion_items:
        scenario = MotionScenario(
            name=item["name"],
            omega_ab=float(item["omega_ab_rad_s"]),
            omega_bc_clockwise=float(item["omega_bc_clockwise_rad_s"]),
        )
        _validate_motion(scenario)
        motions.append(scenario)

    return geometries, motions


def simulate_all(
    geometries: Iterable[GeometryScenario],
    motions: Iterable[MotionScenario],
    num_steps: int = 721,
) -> list[SimulationResult]:
    """Run all Cartesian combinations of geometry and motion scenarios."""

    results: list[SimulationResult] = []
    for geometry in geometries:
        for motion in motions:
            results.append(
                simulate_one_rotation(
                    geometry=geometry,
                    motion=motion,
                    num_steps=num_steps,
                )
            )
    return results


def simulate_one_rotation(
    geometry: GeometryScenario,
    motion: MotionScenario,
    num_steps: int = 721,
) -> SimulationResult:
    """Simulate one full 0-360 deg rotation of AB for one geometry-motion pair.

    Steps:
    1) Build angular/time arrays.
    2) Compute kinematics of B and C.
    3) Compute dynamic force required for lumped masses.
    4) Project onto AB axis to get signed axial force in AB.
    """

    # AB angle sampled over one full turn.
    theta = np.linspace(0.0, 2.0 * np.pi, num_steps)
    theta_deg = np.rad2deg(theta)

    # Convert angle samples to time. With constant omega_ab, time is directly obtained from theta = omega * t.
    time = theta / motion.omega_ab

    # Assignment says BC rotates clockwise.
    # Using CCW-positive math convention => clockwise speed is negative signed omega.
    psi = -motion.omega_bc_clockwise * time

    # Unit vectors along each link direction.
    u_ab = _unit_from_vertical(theta)
    u_bc = _unit_from_vertical(psi)

    # Position vectors.
    r_b = geometry.length_ab * u_ab
    r_c = r_b + geometry.length_bc * u_bc

    # Velocity vectors (time derivative of position).
    v_b = geometry.length_ab * _unit_time_derivative(theta, motion.omega_ab)
    v_c = v_b + geometry.length_bc * _unit_time_derivative(psi, -motion.omega_bc_clockwise)

    # Acceleration vectors (second time derivative of position).
    a_b = geometry.length_ab * _unit_second_time_derivative(theta, motion.omega_ab)
    a_c = a_b + geometry.length_bc * _unit_second_time_derivative(psi, -motion.omega_bc_clockwise)

    # Net dynamic force required to accelerate masses at B and C.
    dynamic_force = geometry.mass_b * a_b + geometry.mass_c * a_c

    # Positive axial force means tension in AB.
    # Dynamic projection gives force on masses along AB, so sign is reversed.
    # np.einsum("ij,ij->i", ...) computes row-wise dot products efficiently.
    axial_force_ab = -np.einsum("ij,ij->i", dynamic_force, u_ab)

    return SimulationResult(
        geometry_name=geometry.name,
        motion_name=motion.name,
        length_ab=geometry.length_ab,
        length_bc=geometry.length_bc,
        mass_b=geometry.mass_b,
        mass_c=geometry.mass_c,
        omega_ab=motion.omega_ab,
        omega_bc_clockwise=motion.omega_bc_clockwise,
        time=time,
        theta_deg=theta_deg,
        r_b=r_b,
        v_b=v_b,
        a_b=a_b,
        r_c=r_c,
        v_c=v_c,
        a_c=a_c,
        axial_force_ab=axial_force_ab,
    )


def find_extremes(results: list[SimulationResult]) -> tuple[SimulationResult, SimulationResult]:
    """Find the combination with highest tension and highest compression."""

    if not results:
        raise ValueError("No simulation results to analyze.")

    # Highest tension = largest positive value anywhere in each curve.
    max_tension_result = max(results, key=lambda result: float(np.max(result.axial_force_ab)))

    # Highest compression = most negative value anywhere in each curve.
    max_compression_result = min(results, key=lambda result: float(np.min(result.axial_force_ab)))
    return max_tension_result, max_compression_result


def plot_single_curve(result: SimulationResult, output_path: Path, color: str = "steelblue") -> None:
    """Save one force-vs-angle plot for one simulation result."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axis = plt.subplots(figsize=(8.0, 4.5))
    axis.plot(result.theta_deg, result.axial_force_ab, color=color, linewidth=2.0)
    # Zero line helps visually separate tension/compression regions.
    axis.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    axis.set_xlabel("Rotation angle of AB (deg)")
    axis.set_ylabel("Axial force in AB (N)")
    axis.set_title(f"{result.geometry_name} x {result.motion_name}")
    axis.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_comparison_grid(
    results: list[SimulationResult],
    geometries: list[GeometryScenario],
    motions: list[MotionScenario],
    output_path: Path,
    max_tension_id: str,
    max_compression_id: str,
) -> None:
    """Save a matrix plot comparing all geometry-motion force curves."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build fast lookup by case ID.
    result_by_id = {result.combo_id: result for result in results}
    row_count = len(geometries)
    col_count = len(motions)

    fig, axes = plt.subplots(
        row_count,
        col_count,
        figsize=(3.4 * col_count, 2.4 * row_count),
        sharex=True,
        sharey=True,
    )

    # Normalize output shape so indexing works for 1x1, 1xN, Nx1, and NxN.
    if row_count == 1 and col_count == 1:
        axes_grid = np.array([[axes]])
    elif row_count == 1:
        axes_grid = np.array([axes])
    elif col_count == 1:
        axes_grid = np.array([[axis] for axis in axes])
    else:
        axes_grid = axes

    for row_index, geometry in enumerate(geometries):
        for col_index, motion in enumerate(motions):
            axis = axes_grid[row_index, col_index]
            combo_id = f"{geometry.name}__{motion.name}"
            result = result_by_id[combo_id]
            color = "steelblue"
            # Highlight extreme cases in distinct colors.
            if combo_id == max_tension_id:
                color = "crimson"
            if combo_id == max_compression_id:
                color = "royalblue"
            axis.plot(result.theta_deg, result.axial_force_ab, color=color, linewidth=1.5)
            axis.axhline(0.0, color="black", linewidth=0.5, linestyle="--")
            axis.grid(True, alpha=0.20)
            axis.set_title(f"{geometry.name}/{motion.name}", fontsize=8)

    for axis in axes_grid[-1, :]:
        axis.set_xlabel("AB angle (deg)")
    for axis in axes_grid[:, 0]:
        axis.set_ylabel("Force (N)")

    fig.suptitle("Axial force in AB for all geometry-motion combinations", y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_metrics_csv(results: list[SimulationResult], output_path: Path) -> None:
    """Write per-case peak tension/compression metrics to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "combo_id",
                "geometry",
                "motion",
                "max_tension_N",
                "angle_at_max_tension_deg",
                "max_compression_N",
                "angle_at_max_compression_deg",
            ]
        )
        for result in results:
            # Indices of global max/min for this case.
            max_tension_idx = int(np.argmax(result.axial_force_ab))
            max_compression_idx = int(np.argmin(result.axial_force_ab))
            writer.writerow(
                [
                    result.combo_id,
                    result.geometry_name,
                    result.motion_name,
                    float(result.axial_force_ab[max_tension_idx]),
                    float(result.theta_deg[max_tension_idx]),
                    float(result.axial_force_ab[max_compression_idx]),
                    float(result.theta_deg[max_compression_idx]),
                ]
            )


def write_engineering_insight(results: list[SimulationResult], output_path: Path) -> None:
    """Create a compact markdown report with extremes and simple sensitivity insight."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    max_tension_result, max_compression_result = find_extremes(results)

    max_tension_value = float(np.max(max_tension_result.axial_force_ab))
    max_tension_angle = float(max_tension_result.theta_deg[np.argmax(max_tension_result.axial_force_ab)])

    max_compression_value = float(np.min(max_compression_result.axial_force_ab))
    max_compression_angle = float(
        max_compression_result.theta_deg[np.argmin(max_compression_result.axial_force_ab)]
    )

    primary_driver, correlations = infer_primary_driver(results)

    correlation_lines = "\n".join(
        f"- `{name}`: correlation = {value:+.3f}" for name, value in correlations.items()
    )

    text = (
        "# Engineering Insight\n\n"
        f"- Highest tensile load: `{max_tension_result.combo_id}` with `F = {max_tension_value:.3f} N` "
        f"at `AB angle = {max_tension_angle:.1f} deg`\n"
        f"- Highest compressive load: `{max_compression_result.combo_id}` with "
        f"`F = {max_compression_value:.3f} N` at `AB angle = {max_compression_angle:.1f} deg`\n"
        f"- Primary load driver in this scenario set: `{primary_driver}`\n\n"
        "## Correlation Snapshot\n"
        f"{correlation_lines}\n"
    )

    output_path.write_text(text, encoding="utf-8")


def infer_primary_driver(results: list[SimulationResult]) -> tuple[str, dict[str, float]]:
    """Estimate the strongest driver of peak loading using linear correlation.

    Note: Correlation is only a quick ranking aid here; it is not causality proof.
    """

    if len(results) < 2:
        return "not enough combinations", {}

    # Use absolute peak force per case as the response metric.
    max_abs_force = np.array([np.max(np.abs(result.axial_force_ab)) for result in results], dtype=float)
    features = {
        "length_ab": np.array([result.length_ab for result in results], dtype=float),
        "length_bc": np.array([result.length_bc for result in results], dtype=float),
        "mass_b": np.array([result.mass_b for result in results], dtype=float),
        "mass_c": np.array([result.mass_c for result in results], dtype=float),
        "omega_ab": np.array([result.omega_ab for result in results], dtype=float),
        "omega_bc_clockwise": np.array([result.omega_bc_clockwise for result in results], dtype=float),
    }

    correlations: dict[str, float] = {}
    for feature_name, values in features.items():
        # If a feature is constant across scenarios, its linear correlation is undefined.
        if np.allclose(values, values[0]):
            correlations[feature_name] = 0.0
            continue
        matrix = np.corrcoef(values, max_abs_force)
        corr = float(matrix[0, 1])
        if np.isnan(corr):
            corr = 0.0
        correlations[feature_name] = corr

    # Driver = feature with largest absolute correlation magnitude.
    primary_driver = max(correlations, key=lambda key: abs(correlations[key]))
    return primary_driver, correlations


def animate_mechanism(result: SimulationResult, output_path: Path, title: str) -> None:
    """Create a GIF animation of mechanism motion for one case."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_length = result.length_ab + result.length_bc
    half_size = 1.2 * total_length
    # Downsample frames to keep GIF size/runtime reasonable.
    step = max(1, len(result.theta_deg) // 180)
    frame_indices = np.arange(0, len(result.theta_deg), step, dtype=int)

    fig, axis = plt.subplots(figsize=(6.0, 6.0))
    axis.set_xlim(-half_size, half_size)
    axis.set_ylim(-half_size, half_size)
    axis.set_aspect("equal")
    axis.grid(True, alpha=0.2)
    axis.set_title(title)
    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")

    axis.plot(0.0, 0.0, marker="o", color="black")
    line, = axis.plot([], [], "-o", color="black", linewidth=2.0, markersize=5.0)
    trace, = axis.plot([], [], color="orange", linewidth=1.0, alpha=0.7)
    info_text = axis.text(
        0.02,
        0.98,
        "",
        transform=axis.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )

    trace_x: list[float] = []
    trace_y: list[float] = []

    def update(frame_index: int):
        # Current B and C points at this frame.
        b_point = result.r_b[frame_index]
        c_point = result.r_c[frame_index]
        line.set_data([0.0, b_point[0], c_point[0]], [0.0, b_point[1], c_point[1]])

        # Keep trajectory history of point C.
        trace_x.append(float(c_point[0]))
        trace_y.append(float(c_point[1]))
        trace.set_data(trace_x, trace_y)

        # Overlay current angle and axial force.
        force_value = float(result.axial_force_ab[frame_index])
        angle_value = float(result.theta_deg[frame_index])
        info_text.set_text(
            f"AB angle: {angle_value:6.1f} deg\n"
            f"Axial force: {force_value:8.2f} N"
        )
        return line, trace, info_text

    animation = FuncAnimation(
        fig,
        update,
        frames=frame_indices,
        interval=35,
        blit=True,
        repeat=True,
    )
    animation.save(output_path, writer=PillowWriter(fps=25))
    plt.close(fig)


def _unit_from_vertical(angle_rad: np.ndarray) -> np.ndarray:
    """Unit vector for angle measured from vertical-up (not from +x)."""

    return np.column_stack((-np.sin(angle_rad), np.cos(angle_rad)))


def _unit_time_derivative(angle_rad: np.ndarray, omega: float) -> np.ndarray:
    """Time derivative of _unit_from_vertical for constant angular speed omega."""

    return omega * np.column_stack((-np.cos(angle_rad), -np.sin(angle_rad)))


def _unit_second_time_derivative(angle_rad: np.ndarray, omega: float) -> np.ndarray:
    """Second time derivative of _unit_from_vertical for constant angular speed omega."""

    return (omega**2) * np.column_stack((np.sin(angle_rad), -np.cos(angle_rad)))


def _validate_geometry(scenario: GeometryScenario) -> None:
    """Basic physical sanity checks for geometry inputs."""

    if scenario.length_ab <= 0.0:
        raise ValueError(f"Geometry '{scenario.name}' has invalid AB length.")
    if scenario.length_bc <= 0.0:
        raise ValueError(f"Geometry '{scenario.name}' has invalid BC length.")
    if scenario.mass_b < 0.0:
        raise ValueError(f"Geometry '{scenario.name}' has invalid mass at B.")
    if scenario.mass_c < 0.0:
        raise ValueError(f"Geometry '{scenario.name}' has invalid mass at C.")


def _validate_motion(scenario: MotionScenario) -> None:
    """Basic physical sanity checks for motion inputs."""

    if scenario.omega_ab <= 0.0:
        raise ValueError(f"Motion '{scenario.name}' requires omega_ab > 0.")
    if scenario.omega_bc_clockwise < 0.0:
        raise ValueError(f"Motion '{scenario.name}' requires omega_bc_clockwise >= 0.")
