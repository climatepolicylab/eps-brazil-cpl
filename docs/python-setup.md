---
layout: page
title:  "Python Setup for Repository Contributors"
---

This repository uses [`uv`](https://docs.astral.sh/uv/) to manage Python installation, the local virtual environment, and Python package dependencies.  The standard interpreter for this repository is Python 3.14.

## Why `uv`

Using `uv` keeps repository setup short and reproducible:

1. `uv` can install the required Python version if it is not already present.
2. `uv sync` creates the local virtual environment and installs the Python dependencies declared by the repository.
3. `uv run ...` executes a command using that managed environment, so contributors do not need separate `venv` and `pip` setup steps.

## Install `uv`

Install `uv` using the package manager appropriate for your operating system.  For example:

- macOS (Homebrew): `brew install uv`
- Windows (winget): `winget install --id=astral-sh.uv -e`

If you prefer another installation method, see the official `uv` documentation.

## Windows Onboarding

If you are setting up the repository on Windows, use this sequence:

1. Install Git for Windows if you do not already have Git.
2. Install `uv` with `winget install --id=astral-sh.uv -e`.
3. Clone the repository.
4. Open the cloned repository in PowerShell or Windows Terminal.
5. From the repository root, run:

   ```powershell
   uv python install 3.14
   uv sync
   ```

6. Verify the environment:

   ```powershell
   uv run python --version
   uv run python -c "import pandas, matplotlib, openpyxl"
   uv run python csv_grapher.py --help
   ```

The repository includes a Windows-only dependency for `windows-curses`, so `uv sync` should install everything needed for `export-csv-files.py` automatically.

## Repository Setup

From the repository root:

1. Install Python 3.14 if your machine does not already have it:

   ```sh
   uv python install 3.14
   ```

2. Create the local virtual environment and install dependencies:

   ```sh
   uv sync
   ```

This creates a local environment in `.venv/`.

## Verify the Setup

Run the following checks from the repository root:

```sh
uv run python --version
uv run python -c "import pandas, matplotlib, openpyxl"
uv run python csv_grapher.py --help
```

If these commands succeed, the Python-side repository setup is working.

## Running Repository Scripts

Run Python utilities through `uv run` so they use the repository-managed environment.

Examples:

```sh
uv run python export-csv-files.py
uv run python csv_grapher.py --help
uv run python CreateDataLoggingScript.py
```

## Vensim DSS

The repository's Python scripts do not run the EPS directly.  Instead, several of them generate Vensim command scripts that are then opened in Vensim DSS.  `uv` solves Python setup only; it does not install or replace Vensim DSS.

For the broader workflow, see [Automated Analysis with Python Scripts](automated-analysis.html) and [Download and Installation Instructions](download.html).