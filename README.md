# EPS Brazil CPL

This repository contains the Energy Policy Simulator (EPS) Brazil model files, supporting documentation, and several Python utilities used to generate Vensim command scripts or work with model data exports.

## Python Setup

This repository uses `uv` for Python setup and dependency management. The standard development interpreter is Python 3.14.

1. Install `uv`.
   - macOS: `brew install uv`
   - Windows (PowerShell with winget): `winget install --id=astral-sh.uv -e`
   - Other platforms: see the official `uv` installation instructions.
2. Clone the repository.
3. From the repository root, install Python 3.14 if needed: `uv python install 3.14`
4. Create the local environment and install dependencies: `uv sync`

This creates a local virtual environment at `.venv/`.

### Windows Notes

- Open the repository in PowerShell or Windows Terminal before running the `uv` commands.
- If Git is not installed yet, install Git for Windows so you can clone the repository and run the commands from the repo root.
- The repository automatically installs `windows-curses` on Windows when you run `uv sync`, which is needed by `export-csv-files.py`.
- Run the same verification commands shown below from the repository root after `uv sync` completes.

## Common Commands

- Check the selected interpreter: `uv run python --version`
- Verify Python dependencies: `uv run python -c "import pandas, matplotlib, openpyxl"`
- Show help for the CSV graphing utility: `uv run python csv_grapher.py --help`
- Run the Excel-to-CSV export utility: `uv run python export-csv-files.py`
- Generate a Vensim command script: `uv run python CreateDataLoggingScript.py`

## Vensim Requirement

`uv` handles Python setup for this repository, but it does not replace Vensim. The main EPS automation scripts generate Vensim command scripts (`.cmd` files). Running those command scripts still requires Vensim DSS.

For more details, see [docs/python-setup.md](docs/python-setup.md) and [docs/automated-analysis.md](docs/automated-analysis.md).