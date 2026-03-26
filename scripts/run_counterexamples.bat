@echo off
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%.."
set PYTHONPATH=%cd%
crosshair check src\counterexample_harnesses.py --analysis_kind=asserts
popd
