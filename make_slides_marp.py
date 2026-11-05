#!/usr/bin/env -S uv run --script
"""
Convert Marp markdown files to PPTX, PDF, or HTML.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Constants
DEFAULT_OUTPUT_FORMATS = ["pptx"]
SUPPORTED_FORMATS = ["pptx", "pdf", "html"]
MARP_COMMAND = "marp"

def convert_marp(input_path: Path, output_path: Path) -> None:
    """Calls the marp command line tool to convert the file."""
    # marp <input> --allow-local-files -o <output>
    command = [
        MARP_COMMAND,
        str(input_path),
        "--allow-local-files",
        "--output",
        str(output_path),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        raise RuntimeError(
            f"The '{MARP_COMMAND}' command was not found. "
            "Please install marp-cli (e.g., 'npm install -g @marp-team/marp-cli')."
        )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="make_slides_marp.py",
        description="Convert Marp markdown files to PPTX, PDF, or HTML.",
        epilog="""
EXAMPLES:
# Default: creates slides.marp.pptx
  python make_slides_marp.py -i slides.marp.md

# Create PDF version
  python make_slides_marp.py -i slides.marp.md -f pdf

# Create PDF, PPTX, and HTML versions
  python make_slides_marp.py -i slides.marp.md -f pptx pdf html

# Output to a specific directory
  python make_slides_marp.py -i slides.marp.md -o ./exports/
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-i", "--input", required=True, help="Input Marp markdown file")
    parser.add_argument("-o", "--output", help="Output path (file or directory)")
    parser.add_argument(
        "-f", "--format",
        metavar="FORMAT",
        choices=SUPPORTED_FORMATS,
        nargs="+",
        default=DEFAULT_OUTPUT_FORMATS,
        help=f"Output format(s) ({', '.join(SUPPORTED_FORMATS)}) (default: pptx)"
    )

    return parser.parse_args()

def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    formats = args.format
    success_count = 0

    for fmt in formats:
        # Determine output path for this format
        if args.output:
            out_dir = Path(args.output)
            if out_dir.is_dir():
                output_path = out_dir / input_path.with_suffix(f".{fmt}").name
            else:
                # User provided a filename, replace its extension
                output_path = out_dir.with_suffix(f".{fmt}")
        else:
            # Derive output path from input path
            output_path = input_path.with_suffix(f".{fmt}")

        try:
            convert_marp(input_path, output_path)
            print(f"Successfully converted {input_path} to {output_path}")
            success_count += 1
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print(f"Error converting to {fmt}: {e}", file=sys.stderr)

    return 0 if success_count == len(formats) else 1

if __name__ == "__main__":
    sys.exit(main())
