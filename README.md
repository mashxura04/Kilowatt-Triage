# Kilowatt Triage

A research prototype exploring how public schools in Uzbekistan could prioritize energy-efficiency retrofits under limited budgets.

Kilowatt Triage evaluates potential energy-efficiency measures using climate-zone data, school characteristics, estimated energy savings, and historical investment costs.

The project uses a representative public-school model based on the World Bank's 2021 study of energy efficiency in Uzbekistan's public buildings.

## Current Features

- Loads retrofit data from CSV datasets.
- Validates dataset structure and numerical values.
- Supports four climate zones.
- Collects school-specific information, including floor area, heating system, available fuels, and electrical capacity.
- Estimates annual baseline energy demand for heating, lighting, and equipment.
- Scales eligible energy-saving estimates proportionally to school floor area.
- Evaluates intervention compatibility with the school's existing heating system.
- Keeps thermal and electrical savings separate.
- Evaluates a sequential retrofit package consisting of insulation, a compatible conventional boiler upgrade where applicable, and LED lighting.
- Identifies fuel-switch options whose net energy savings cannot yet be calculated reliably.
- Reports historical reference investment costs.
- Selects the savings-maximizing package within a stated budget from a small, fixed set of candidate packages (thermal and electrical scenarios are optimized separately).
- Serves assessments through a JSON API (`api/evaluate.py`) and a static project website with an assessment form (`kilowatt-triage/`).

## Methodological Approach

### Reference School

The model uses a 4,000 m² reference school based on the World Bank's standard-school assumptions.

Baseline energy consumption is estimated using the reported specific energy consumption values for each climate zone.

These calculations represent a modelled reference school, not measured consumption from an actual school.

### Energy Savings

Eligible intervention savings are scaled proportionally according to school floor area.

This is an estimation assumption, not a verified relationship for every individual school.

Thermal and electrical savings are reported separately and are not combined into one total.

### Retrofit Packages

The prototype evaluates a conservative retrofit package that includes insulation, a compatible conventional boiler upgrade where applicable, and LED lighting.

Boiler savings are treated as post-insulation savings based on numerical consistency with the World Bank's reference-school calculations. The exact calculation sequence in the original source is not independently confirmed.

Fuel-switch options are excluded from calculated package savings until their complete energy balances can be established.

### Budget Optimization

`src/budget_optimizer.py` selects, for the entered budget, the package with the largest estimated saving. Thermal and electrical scenarios are optimized separately and each uses the full budget independently; they are not one combined allocation.

The candidate set is deliberately small: no thermal measure, insulation, or insulation plus the compatible conventional boiler upgrade (thermal); and LED lighting (electrical). A boiler is never offered on its own, because boiler savings are only estimated after insulation. Fuel-switch options are excluded. Costs are the unscaled 2021 reference-school costs, so a small school's budget is compared against full reference-school prices.

### Investment Costs

Investment costs are historical 2021 USD reference values from the World Bank study.

They are not current supplier quotations or verified school-specific project budgets.

## Project Structure

```
Kilowatt-Triage/
├── .github/
│   └── workflows/
│       └── tests.yml          runs the unit tests on Python 3.9 to 3.12
├── api/
│   └── evaluate.py            Vercel Python function: POST /api/evaluate (GET = health check)
├── data/
│   ├── retrofit_data.csv
│   └── source_register.csv
├── kilowatt-triage/           static website (HTML/CSS/JS) incl. the assessment form
├── research/
│   ├── validation_notes.md
│   └── validation_plan.md
├── src/
│   ├── baseline.py
│   ├── budget_optimizer.py
│   ├── compatibility.py
│   ├── data_loader.py
│   ├── evaluation.py
│   ├── main.py
│   ├── package_evaluation.py
│   ├── scaling.py
│   └── school_profile.py
├── tests/                     unit tests incl. API handler and budget optimizer
├── check_boiler_percentages.py
├── vercel.json                serves kilowatt-triage/ as the site; api/ as the function
├── README.md
└── .gitignore
```

## Requirements

- Python 3.9 or newer. The code uses no syntax or libraries newer than 3.9 (static check). The test suite has been run locally on Python 3.12; `.github/workflows/tests.yml` runs it on Python 3.9 to 3.12 for every pull request.
- No third-party Python packages are currently required.

The prototype uses Python's standard library.

## Running the Prototype

Open the project folder in VS Code and open the integrated terminal.

Run:

```bash
python -m src.main
```

Follow the prompts to enter the school's characteristics and generate an evaluation report.

## Website and API

The deployed site is the repository root on Vercel: the root `vercel.json` sets `outputDirectory` to `kilowatt-triage`, and `api/evaluate.py` is detected as a Python function. The Vercel project's Root Directory must therefore be the repository root (not `kilowatt-triage/`), otherwise `/api/evaluate` will not exist and the form will fail.

Opening `/api/evaluate` in a browser (GET) returns a small health check, for example `{"success": true, "status": "alive", "imports_ok": true}`.

## Running the Tests

Run the complete automated test suite:

```bash
python -m unittest discover -s tests -v
```

The latest recorded test run (Python 3.12.3) completed with **203 passing tests and no failures**. Earlier versions of this README reported 161.

## Data Source

World Bank (2021). *Uzbekistan: Deploying Energy Efficiency and Distributed Solar in the Public Buildings*. Report No. AUS0002052.

https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099062325113547753

The dataset contains historical energy-saving and investment estimates for a modelled standard school across four climate zones.

Reported values should be distinguished from school-specific estimates generated by the prototype.

## Limitations

- The reference-school model does not represent measured consumption from a particular school.
- Proportional floor-area scaling is an assumption and requires further validation.
- Boiler savings are treated as sequential post-insulation savings, but the exact source calculation sequence remains uncertain.
- Fuel-switch options require additional information about fuel savings and electricity consumption before net savings can be calculated.
- Electrical conversion options require further technical assessment, even when electricity is available.
- Investment costs are historical reference values, not current quotations.
- Maintenance costs, equipment lifetimes, current energy tariffs, financing, and verified emissions factors are not yet incorporated.
- The budget optimizer chooses from a small fixed set of candidate packages using unscaled reference-school costs; it is not a general optimizer.
- The heating-system condition is validated and displayed but does not currently change any estimate; no supported adjustment factor has been identified.
- The prototype does not yet perform sensitivity analysis.
- Estimates have not been validated against actual school energy bills or measurements. A plan for doing so is in `research/validation_plan.md`.

## Development Status

Kilowatt Triage is an evolving research prototype.

Current development focuses on source-to-model verification, scientific validation, sensitivity analysis, improved documentation, and assessing the assumptions behind the model.

The goal is to develop a transparent decision-support tool that helps schools compare potential retrofit measures while clearly distinguishing published evidence, modelled estimates, and unresolved information.