#!/usr/bin/env bash
export PYTHONPATH="$(pwd)"
crosshair check src/verified_harnesses.py --analysis_kind=asserts
