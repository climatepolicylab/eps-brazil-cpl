#!/usr/bin/env python3
"""
CSV Line Graph Generator

Traverses directories to find CSV files and generates line graphs.
Handles transposed CSV format where time runs across columns (first row)
and labels are in the first column. Automatically extracts and applies units
to Y-axis labels based on detected CSV structure patterns.
"""

import os
import sys
import argparse
import re
import csv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
plt.matplotlib.use('Agg')  # Non-interactive backend

GREEN = '\033[92m'
RED = '\033[91m'
DARK_YELLOW = '\033[33m'
RESET = '\033[0m'

# Terms to exclude from warning report (warnings still printed immediately)
WARNING_EXCLUSIONS = [
    'FoPITY',
    'ESUfRaLCD',
    'PERAC',
    'PEAAC',
]


def parse_transposed_csv(csv_path, report=None):
    """
    Parse a CSV file where time is in the first row and labels in first column.

    Returns:
        y_axis_label: label from first cell (top-left corner)
        time_values: list of time values
        data_series: dict of {label: [values]}
    """
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) < 2:
        return None, None, None

    # First cell is the y-axis label
    y_axis_label = rows[0][0].strip() if rows[0][0] else "Value"

    # First row contains time values (skip first cell which is header)
    time_values = rows[0][1:]

    # Convert time values to floats if possible
    try:
        time_values = [float(t) for t in time_values if t.strip()]
    except ValueError:
        # If not numeric, keep as strings
        pass

    # Remaining rows: first column is label, rest are data values
    # Stop when we encounter a row with no label or no values
    data_series = {}
    for row in rows[1:]:
        if not row or not row[0].strip():
            break

        label = row[0].strip()
        values = row[1:len(time_values)+1]

        # Check if this row has any actual data values
        has_data = any(v.strip() for v in values if v)
        if not has_data:
            break

        # Convert values to floats
        try:
            values = [float(v) if v.strip() else None for v in values]
            data_series[label] = values
        except ValueError:
            warning_message = f"Could not convert values for label '{label}' in {csv_path}"
            print(f"{DARK_YELLOW}Warning:{RESET} {warning_message}")
            if report is not None and not any(term in csv_path for term in WARNING_EXCLUSIONS):
                report['warnings'].append(warning_message)
            continue

    return y_axis_label, time_values, data_series


def create_line_graph(time_values, data_series, output_path, title=None, y_label="Value"):
    """
    Create a line graph with time on x-axis.

    Args:
        time_values: list of time points
        data_series: dict of {label: [values]}
        output_path: path to save the graph
        title: optional title for the graph
        y_label: label for y-axis
    """
    # Define 20 distinct colors for up to 20 different lines
    colors = [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # olive
        '#17becf',  # cyan
        '#aec7e8',  # light blue
        '#ffbb78',  # light orange
        '#98df8a',  # light green
        '#ff9896',  # light red
        '#c5b0d5',  # light purple
        '#c49c94',  # light brown
        '#f7b6d2',  # light pink
        '#c7c7c7',  # light gray
        '#dbdb8d',  # light olive
        '#9edae5',  # light cyan
    ]

    plt.figure(figsize=(10, 6))

    for i, (label, values) in enumerate(data_series.items()):
        color = colors[i % len(colors)]  # Cycle through colors if more than 20 lines
        plt.plot(time_values, values, marker='o', label=label, linewidth=2, markersize=4, color=color)

    plt.xlabel('Time', fontsize=12)
    plt.ylabel(y_label, fontsize=12)

    if title:
        plt.title(title, fontsize=14)

    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def process_csv_file(csv_path, input_root, output_root, output_format='png', report=None):
    """
    Process a single CSV file and generate graph.

    Args:
        csv_path: path to CSV file
        input_root: root directory of input CSV files
        output_root: root directory to save output graphs
        output_format: 'png' or 'svg'
    """
    try:
        y_axis_label, time_values, data_series = parse_transposed_csv(csv_path, report=report)

        if not time_values or not data_series:
            skipped_message = f"{csv_path}: insufficient data"
            print(f"{DARK_YELLOW}Skipping:{RESET} {skipped_message}")
            if report is not None:
                report['skipped'].append(skipped_message)
            return False

        # Get relative path from input root
        csv_path_obj = Path(csv_path)
        input_root_obj = Path(input_root)
        relative_path = csv_path_obj.relative_to(input_root_obj)

        # Create mirrored directory structure in output
        relative_dir = relative_path.parent
        output_subdir = os.path.join(output_root, relative_dir)
        os.makedirs(output_subdir, exist_ok=True)

        # Create output filename
        csv_name = csv_path_obj.stem
        output_filename = f"{csv_name}_graph.{output_format}"
        output_path = os.path.join(output_subdir, output_filename)

        # Find XLSX file in the same directory
        xlsx_name = None
        csv_dir = csv_path_obj.parent
        for file in csv_dir.glob('*.xlsx'):
            xlsx_name = file.stem
            break

        # Create title using XLSX name (if found) and CSV name
        if xlsx_name:
            title = f"{xlsx_name} - {csv_name}"
        else:
            title = csv_name

        # Create graph
        create_line_graph(time_values, data_series, output_path, title=title, y_label=y_axis_label)

        print(f"{GREEN}✓{RESET} Created graph: {output_path}")
        return True

    except Exception as e:
        error_message = f"Error processing {csv_path}: {e}"
        print(f"{RED}✗{RESET} {error_message}")
        if report is not None:
            report['errors'].append(error_message)
        return False


def traverse_and_process(root_dir, output_dir, output_format='png', recursive=True):
    """
    Traverse directory structure and process all CSV files.

    Args:
        root_dir: root directory to start traversal
        output_dir: directory to save output graphs
        output_format: 'png' or 'svg'
        recursive: whether to traverse subdirectories
    """
    csv_files = []

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.lower().endswith('.csv'):
                    csv_files.append(os.path.join(dirpath, filename))
    else:
        for filename in os.listdir(root_dir):
            if filename.lower().endswith('.csv'):
                csv_files.append(os.path.join(root_dir, filename))

    if not csv_files:
        print(f"No CSV files found in {root_dir}")
        return

    print(f"Found {len(csv_files)} CSV file(s)")
    print(f"Output directory: {output_dir}")
    print(f"Output format: {output_format.upper()}")
    print("-" * 60)

    report = {
        'warnings': [],
        'errors': [],
        'skipped': [],
    }

    success_count = 0
    for csv_file in csv_files:
        if process_csv_file(csv_file, root_dir, output_dir, output_format, report=report):
            success_count += 1

    print("-" * 60)

    if report['skipped']:
        print(f"\n{DARK_YELLOW}Skipping:{RESET} details")
        for message in report['skipped']:
            print(f"- {DARK_YELLOW}Skipping:{RESET} {message}")

    if report['errors']:
        print(f"\n{RED}Errors:{RESET}")
        for message in report['errors']:
            print(f"- {message}")

    if report['warnings']:
        print(f"\n{DARK_YELLOW}Warning:{RESET} details")
        for message in report['warnings']:
            print(f"- {DARK_YELLOW}Warning:{RESET} {message}")

    print(f"\nSuccessfully processed {success_count}/{len(csv_files)} file(s)")
    print(f"Skipped: {len(report['skipped'])}")
    print(f"Errors: {len(report['errors'])}")
    print(f"Warnings (w/ exclusions): {len(report['warnings'])}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate line graphs from transposed CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Use default directory (./data)
  %(prog)s -d /path/to/csvs             # Process specific directory
  %(prog)s -d ./data -o ./graphs        # Custom output directory
  %(prog)s -f svg                       # Output as SVG instead of PNG
  %(prog)s -d ./data --no-recursive     # Only process top-level directory
        """
    )

    parser.add_argument(
        '-d', '--directory',
        # default="InputData/add-outputs",
        default="InputData/",
        help='Directory to search for CSV files (default: InputData)'
    )

    parser.add_argument(
        '-o', '--output',
        default='./csv_graphs',
        help='Directory to save nested folder structure of output graphs (default: ./csv_graphs)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['png', 'svg'],
        default='png',
        help='Output format for graphs (default: png)'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not traverse subdirectories'
    )

    args = parser.parse_args()

    # Validate input directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory")
        sys.exit(1)

    # Simple approach: remove any leading path segment "InputData/" (case-insensitive)
    # from the provided directory string and use the remainder as the namespace.
    # If nothing remains, use the output root directly; otherwise join the tail.
    # Remove the first occurrence of 'InputData/' (case-insensitive)
    tail = re.sub(r'(?i)inputdata[\/]+', '', args.directory, count=1)
    tail = tail.strip('/')

    if tail:
        # Use the tail as the namespace under the output dir
        run_output = os.path.join(args.output, os.path.normpath(tail))
    else:
        # If nothing remains (e.g. directory was exactly 'InputData'), use output root
        run_output = args.output

    # Create output directory if it doesn't exist
    os.makedirs(run_output, exist_ok=True)

    # Process files
    traverse_and_process(
        args.directory,
        run_output,
        args.format,
        recursive=not args.no_recursive
    )


if __name__ == '__main__':
    main()
