from __future__ import annotations

"""
Deliberately too-strong properties.

These are useful in the report because CrossHair should be able to find concrete
counterexamples, after which the report can explain how the property was refined
into a weaker but defensible operational contract.

Run with:
    `crosshair check src/counterexample_harnesses.py --analysis_kind=asserts`
"""

from src.realworld_functions import canonicalize_name, parse_dict_header, secure_filename_ascii_domain



def too_strong_secure_filename_never_empty(filename: str) -> None:
    assert filename.isascii()
    assert len(filename) <= 8

    result = secure_filename_ascii_domain(filename)

    # Counterexample: strings like "\x01", ".", or "///" can become empty.
    assert result != ""



def too_strong_canonicalize_name_never_changes_length(name: str) -> None:
    assert len(name) <= 12
    assert name != ""

    normalized = canonicalize_name(name)

    # Counterexample: repeated separators collapse, and some Unicode lowercase
    # conversions can also change length.
    assert len(normalized) == len(name)



def too_strong_parse_dict_header_never_contains_none(key: str) -> None:
    assert len(key) <= 8
    assert key != ""
    assert "=" not in key
    assert "," not in key

    parsed = parse_dict_header(key)

    # Counterexample: a bare token becomes {key: None}.
    assert parsed[key] is not None
