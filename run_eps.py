#!/usr/bin/env python3
"""
Run EPS pipeline stages: pre-processing, model run, and post-processing.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_TSV = "ScriptRunData1.tsv"
DEFAULT_GRAPHS_DIR = "graph_outputs"
DEFAULT_SLIDES_PPTX = "eps_slides.pptx"


def run_preprocessing() -> None:
    print("[pre] Placeholder: no pre-processing steps are implemented yet.")


def run_model() -> None:
    cmd = ["bash", "time_model_run.sh"]
    print(f"[run] Running model: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Model run failed with exit code {result.returncode}")


def run_graphs(input_tsv: str, output_dir: str, start_year: int | None, step: float) -> None:
    cmd = [
        sys.executable,
        "make_graphs.py",
        "--input",
        input_tsv,
        "--output",
        output_dir,
        "--step",
        str(step),
    ]
    if start_year is not None:
        cmd.extend(["--start-year", str(start_year)])

    print(f"[post] Generating graphs: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Graph generation failed with exit code {result.returncode}")


def run_slides(graphs_dir: str, output_pptx: str, title: str) -> None:
    cmd = [
        sys.executable,
        "make_slides.py",
        "--input-dir",
        graphs_dir,
        "--output",
        output_pptx,
        "--title",
        title,
    ]

    print(f"[post] Generating slides: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Slide generation failed with exit code {result.returncode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run EPS model pipeline stages",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--pre", action="store_true", help="Run pre-processing stage")
    parser.add_argument("--run", action="store_true", help="Run the model stage")
    parser.add_argument("--graphs", action="store_true", help="Generate graphs in post-processing")
    parser.add_argument("--slides", action="store_true", help="Generate slides in post-processing")

    parser.add_argument("--tsv", default=DEFAULT_TSV, help="Input TSV for graph generation")
    parser.add_argument("--graphs-dir", default=DEFAULT_GRAPHS_DIR, help="Output directory for graphs")
    parser.add_argument("--slides-output", default=DEFAULT_SLIDES_PPTX, help="Output PPTX file")
    parser.add_argument("--slides-title", default="EPS Results", help="Presentation title")

    parser.add_argument("--start-year", type=int, default=None, help="Starting year for time axis")
    parser.add_argument("--step", type=float, default=1.0, help="Time step between data points")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    run_pre = args.pre
    run_model_stage = args.run
    run_graphs_stage = args.graphs
    run_slides_stage = args.slides

    if not any([run_pre, run_model_stage, run_graphs_stage, run_slides_stage]):
        run_pre = True
        run_model_stage = True

    try:
        if run_pre:
            run_preprocessing()
        if run_model_stage:
            run_model()
        if run_graphs_stage:
            run_graphs(args.tsv, args.graphs_dir, args.start_year, args.step)
        if run_slides_stage:
            run_slides(args.graphs_dir, args.slides_output, args.slides_title)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
