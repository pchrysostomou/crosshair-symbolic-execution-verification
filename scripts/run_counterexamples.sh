#!/usr/bin/env bash
export PYTHONPATH="$(pwd)"
crosshair check src/counterexample_harnesses.py --analysis_kind=asserts
