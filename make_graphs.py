#!/usr/bin/env python3
"""
Generate bright, modern graphs from EPS TSV output.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")  # Non-interactive backend


def parse_tsv(tsv_path: Path) -> pd.DataFrame:
    rows: list[list[str]] = []
    max_cols = 0

    with tsv_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.rstrip("\n")
            if not stripped:
                continue
            parts = stripped.split("\t")
            rows.append(parts)
            if len(parts) > max_cols:
                max_cols = len(parts)

    if max_cols < 6:
        raise ValueError("TSV has too few columns to parse")

    padded_rows = [row + [""] * (max_cols - len(row)) for row in rows]
    data = pd.DataFrame(padded_rows)

    meta_cols = ["series", "source", "unit", "tag"]
    value_cols = [f"v{i}" for i in range(1, max_cols - len(meta_cols) + 1)]
    data.columns = meta_cols + value_cols
    return data


def build_time_index(count: int, start_year: int | None, step: float) -> list[float]:
    if count <= 0:
        return []

    if start_year is None:
        return list(range(1, count + 1))

    return [start_year + step * i for i in range(count)]


def sanitize_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
    return cleaned.strip("_") or "series"


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="talk", font_scale=0.9)
    sns.set_palette("husl")
    plt.rcParams.update({
        "figure.figsize": (11, 6.5),
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.alpha": 0.25,
        "lines.linewidth": 2.5,
        "lines.markersize": 4,
    })


def get_graph_configs() -> list[dict]:
    """Define which graphs to create and how to group series."""
    return [
        {
            "title": "Total CO2e Emissions by Sector",
            "filename": "total_co2e_by_sector",
            "filter_pattern": "Output Total CO2e Emissions by Sector",
        },
        {
            "title": "Process Emissions in CO2e by Industry",
            "filename": "process_emissions_by_industry",
            "filter_pattern": "Output Process Emissions in CO2e by Industry",
        },
        {
            "title": "Total CO2e Emissions",
            "filename": "total_co2e_emissions",
            "filter_pattern": "Output Total CO2e Emissions",
            "exact_match": True,
        },
        {
            "title": "Electricity Generation Capacity",
            "filename": "electricity_generation_capacity",
            "filter_pattern": "Output Electricity Generation Capacity",
        },
    ]


def extract_series_label(series: str) -> str:
    """Extract label from series name. If format is 'Name[label]', return 'label'."""
    if "[" in series and "]" in series:
        start = series.rfind("[")
        end = series.rfind("]")
        if start < end:
            return series[start + 1:end]
    return series


def create_graphs(data: pd.DataFrame, output_dir: Path, start_year: int | None, step: float) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_style()

    created = 0
    value_cols = data.columns[4:]
    time_values = build_time_index(len(value_cols), start_year, step)

    configs = get_graph_configs()

    for config in configs:
        pattern = config["filter_pattern"]
        exact_match = config.get("exact_match", False)

        # Filter rows matching the pattern
        if exact_match:
            matching_rows = data[data["series"] == pattern]
        else:
            matching_rows = data[data["series"].str.contains(pattern, na=False, case=False)]

        if matching_rows.empty:
            continue

        fig, ax = plt.subplots()

        # Get unit from first matching row
        unit = str(matching_rows.iloc[0]["unit"]).strip() if not pd.isna(matching_rows.iloc[0]["unit"]) else ""

        # Plot all matching series on one graph
        for _, row in matching_rows.iterrows():
            series = str(row["series"]).strip()
            values = pd.to_numeric(row[value_cols], errors="coerce").tolist()

            if not all(pd.isna(v) for v in values):
                label = extract_series_label(series)
                ax.plot(time_values, values, marker="o", label=label)

        ax.set_xlabel("Year" if start_year is not None else "Time Step")
        ax.set_ylabel(unit if unit else "Value")
        ax.set_title(config["title"])
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize="small")

        fig.tight_layout()

        png_path = output_dir / f"{config['filename']}.png"
        svg_path = output_dir / f"{config['filename']}.svg"

        fig.savefig(png_path, dpi=300)
        fig.savefig(svg_path)
        plt.close(fig)

        created += 1

    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create PNG and SVG charts from EPS TSV output",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--input", required=True, help="Input TSV file")
    parser.add_argument("--output", default="graph_outputs", help="Output directory for charts")
    parser.add_argument("--start-year", type=int, default=None, help="Starting year for x-axis")
    parser.add_argument("--step", type=float, default=1.0, help="Time step between data points")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: TSV not found at {input_path}")
        return 1

    if math.isclose(args.step, 0.0, abs_tol=0.0):
        print("Error: --step must be non-zero")
        return 1

    try:
        data = parse_tsv(input_path)
        output_dir = Path(args.output)
        created = create_graphs(data, output_dir, args.start_year, args.step)
        print(f"Created {created} chart(s) in {output_dir}")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
