# COMP0103 Coursework: CrossHair Analysis

This repository contains the code, harnesses, and scripts used for formal verification experiments with CrossHair.

The accompanying PDF report explains the methodology, design decisions, and results.

---

## Project structure

```text
crosshair_coursework_zip/
├── README.md
├── requirements.txt
├── SOURCES.md
├── results/
│   ├── observed_counterexamples.txt
│   └── observed_verified.txt
├── scripts/
│   ├── run_verified.bat
│   ├── run_counterexamples.bat
│   ├── run_verified.sh
│   └── run_counterexamples.sh
└── src/
    ├── __init__.py
    ├── realworld_functions.py
    ├── verified_harnesses.py
    └── counterexample_harnesses.py
```

---

## Installation

Python 3.13 was used for this analysis. Python 3.10+ should also be compatible.

### Ubuntu / Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x scripts/*.sh
```

### Windows

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running CrossHair

### Verified harnesses

```bash
./scripts/run_verified.sh
```

### Counterexample harnesses

```bash
./scripts/run_counterexamples.sh
```

The scripts configure `PYTHONPATH` automatically and run CrossHair with:

```bash
crosshair check --analysis_kind=asserts
```

---

## Expected outcomes

- **Verified harnesses** should complete without reported violations.
- **Counterexample harnesses** should produce `AssertionError` examples demonstrating why intentionally too-strong specifications do not hold.

---

## Results directory

The `results/` directory contains example observed outputs from CrossHair runs for reproducibility reference.

---

## Sources

Details about selected real-world functions and adaptation decisions are provided in `SOURCES.md`.