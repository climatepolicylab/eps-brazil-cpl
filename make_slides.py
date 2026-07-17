#!/usr/bin/env python3
"""
Generate a PPTX slide deck from chart images using Quarto.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def build_qmd(title: str, images: list[Path]) -> str:
    lines = [
        "---",
        f"title: \"{title}\"",
        "format:",
        "  pptx:",
        "    slide-level: 2",
        "---",
        "",
    ]

    for image in images:
        slide_title = image.stem.replace("_", " ")
        lines.append(f"## {slide_title}")
        lines.append("")
        lines.append(f"![]({image.as_posix()})")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a PPTX slide deck from PNG or SVG charts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--input-dir", default="graph_outputs", help="Directory containing chart images")
    parser.add_argument("--output", default="eps_slides.pptx", help="Output PPTX file")
    parser.add_argument("--title", default="EPS Results", help="Presentation title")
    parser.add_argument("--image-ext", choices=["png", "svg"], default="png", help="Image extension to include")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if shutil.which("quarto") is None:
        print("Error: 'quarto' not found in PATH")
        return 1

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: input directory not found: {input_dir}")
        return 1

    images = sorted(input_dir.rglob(f"*.{args.image_ext}"))
    if not images:
        print(f"Error: no *.{args.image_ext} images found in {input_dir}")
        return 1

    output_path = Path(args.output)
    output_dir = output_path.parent if output_path.parent.as_posix() != "." else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    qmd_path = output_dir / "eps_slides.qmd"
    qmd_path.write_text(build_qmd(args.title, images), encoding="utf-8")

    cmd = [
        "quarto",
        "render",
        qmd_path.as_posix(),
        "--to",
        "pptx",
        "--output",
        output_path.name,
    ]

    print(f"Rendering slides with: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False, cwd=output_dir)
    if result.returncode != 0:
        print(f"Error: Quarto render failed with exit code {result.returncode}")
        return 1

    print(f"Created slides: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
