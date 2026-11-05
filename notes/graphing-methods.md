# How Graphs Are Made in This Project

Summary of the distinct graphing paths in the `eps-brazil-cpl` repository — from the Vensim
model itself, through the Python post-processing, to the web-app outputs that are documented
here but rendered elsewhere.

## 1. Vensim-native graphs (built into the model)

The most "native" graphs live inside Vensim itself and are defined in
[`GraphDefinitions.vgd`](../GraphDefinitions.vgd) and embedded in the model files
([`EPS.mdl`](../EPS.mdl), [`CPL_Additions.mdl`](../CPL_Additions.mdl)). Each `:GRAPH` block
declares a title, one `:VAR` per line, plus `:LINE-COLOR`, `:LINE-WIDTH`, `:DATASET`,
`:SCALE`, and `:NO-LEGEND` directives. Vensim renders these directly (~20 built-in line /
stacked-area graphs) — no Python involved. Per
[`visualizing-output.md`](../docs/visualizing-output.md) these are pre-styled and read-only
in Model Reader.

## 2. `make_graphs.py` — matplotlib + seaborn (the main custom grapher)

[`make_graphs.py`](../make_graphs.py) reads a Vensim run's TSV (default `ScriptRunData1.tsv`),
where each row is a series with meta columns (`series`, `source`, `unit`, `tag`) and time steps
across the trailing columns. It:

- Groups rows by the fixed configs in
  [`get_graph_configs()`](../make_graphs.py#L75) (4 graphs: CO₂e by sector, process emissions
  by industry, total CO₂e, electricity capacity).
- Styles via **seaborn** `whitegrid` / `talk` context and the `husl` palette
  ([`configure_style()`](../make_graphs.py#L61)).
- Emits **both PNG (dpi 300) and SVG** per graph.

This is wired into the pipeline as the `--graphs` stage of
[`run_eps.py:33`](../run_eps.py#L33).

## 3. `csv_grapher.py` — plain matplotlib (directory-wide, transposed CSVs)

[`csv_grapher.py`](../csv_grapher.py) is a second, more general grapher that walks a directory
tree (default `InputData/`) and makes one line graph per CSV. It handles a **different input
format** — *transposed* CSVs where time runs across the first row and series labels down the
first column (first cell = y-axis label). It uses matplotlib only (a hardcoded 20-color
palette), mirrors the folder structure into the output dir, pulls the title from a sibling
`.xlsx` filename, and writes PNG or SVG.

So the two Python graphers split the work: **`make_graphs.py` = curated, seaborn-styled,
TSV-in; `csv_grapher.py` = arbitrary, bulk, transposed-CSV-in.**

## 4. `make_slides.py` — Quarto → PPTX (wraps the images, doesn't plot)

[`make_slides.py`](../make_slides.py) isn't a plotter — it collects the PNG/SVG output from
`make_graphs.py` and generates a slide deck by writing a Quarto `.qmd` and calling
`quarto render --to pptx`. One slide per image. Invoked as the `--slides` stage of
[`run_eps.py:57`](../run_eps.py#L57).

## How the data reaches these graphers (the pipeline)

- [`run_eps.py`](../run_eps.py) orchestrates the stages: `--pre` (placeholder) → `--run` →
  `--graphs` → `--slides`.
- `--run` calls [`time_model_run.sh`](../time_model_run.sh), which executes a Vensim `.cmd`
  and logs timing.
- The four [`Create*Script.py`](../CreateCombinationsScript.py) files (by Jeffrey Rissman)
  **generate those Vensim `.cmd` scripts** — Python can't call Vensim directly, so they write
  Vensim's command-script language. Vensim then emits the TSV that `make_graphs.py` consumes.
- [`export-csv-files.py`](../export-csv-files.py) is a separate converter (Excel input tabs →
  CSV), not a grapher.

## Documented here but rendered *outside* this repo

Two graph types described in `docs/` are **not** produced by any code in this folder:

- **Wedge diagrams & policy cost curves** — rendered by the separate EPS web application. This
  repo holds the *inputs* that drive them:
  [`CreateContributionTestScript.py`](../CreateContributionTestScript.py) (which uses
  [`OutputVarsForWedgeDiagram.lst`](../OutputVarsForWedgeDiagram.lst)) generates the multi-run
  data; [`WebAppData.xlsx`](../WebAppData.xlsx) configures the groupings. The actual
  stacked-wedge rendering lives in the web app. See
  [`calculating-wedge-diagrams-and-cost-curves.md`](../docs/calculating-wedge-diagrams-and-cost-curves.md).
- **The web interface's 174 graphs / 600+ series** — again the web app, per
  [`web-interface-graphs.md`](../docs/web-interface-graphs.md).
  [`web_assets/`](../web_assets/) here contains only logos/images, no charting JS.

## TL;DR

Four in-repo rendering paths: Vensim-native (`.vgd`/`.mdl`), `make_graphs.py`
(matplotlib+seaborn), `csv_grapher.py` (matplotlib), and `make_slides.py` (Quarto/PPTX
wrapper); plus wedge diagrams and the web-interface graphs, which are configured here but drawn
by the external web app.
