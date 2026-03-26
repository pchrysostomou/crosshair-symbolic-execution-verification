from __future__ import annotations

"""
CrossHair harnesses aimed at operational contracts that are plausible, non-vacuous,
and stronger than basic hygiene checks.

Run with:
    `crosshair check src/verified_harnesses.py --analysis_kind=asserts`
"""

from src.realworld_functions import (
    canonicalize_name,
    contains_ascii_alnum,
    dump_header,
    has_clean_edges,
    has_no_path_separators,
    is_already_safe_ascii_filename,
    is_http_token,
    is_normalized_name,
    parse_dict_header,
    parse_list_header,
    secure_filename_ascii_domain,
)


# ---------------------------------------------------------------------------
# secure_filename_ascii_domain
# ---------------------------------------------------------------------------


def harness_secure_filename_idempotent(filename: str) -> None:
    assert filename.isascii()
    assert len(filename) <= 20

    once = secure_filename_ascii_domain(filename)
    twice = secure_filename_ascii_domain(once)

    assert twice == once
    assert has_clean_edges(once)



def harness_secure_filename_preserves_already_safe_ascii(filename: str) -> None:
    """
    Stronger semantic claim: inside a realistic operational subdomain of already
    safe ASCII filenames, sanitization should preserve the filename exactly.
    """
    assert len(filename) <= 20
    assert is_already_safe_ascii_filename(filename)

    result = secure_filename_ascii_domain(filename)

    assert result == filename



def harness_secure_filename_refined_nonempty(filename: str) -> None:
    """
    Refinement of the too-strong counterexample goal "never empty".

    On an ASCII subdomain that excludes path separators and preserves at least one
    alphanumeric signal, sanitization should still leave at least one ASCII
    alphanumeric character in the result.
    """
    assert filename.isascii()
    assert len(filename) <= 20
    assert has_no_path_separators(filename)
    assert all(ch.isalnum() or ch in " ._-" for ch in filename)
    assert contains_ascii_alnum(filename)

    result = secure_filename_ascii_domain(filename)

    assert result != ""
    assert contains_ascii_alnum(result)


# ---------------------------------------------------------------------------
# parse_list_header
# ---------------------------------------------------------------------------


def harness_parse_list_header_roundtrip(a: str, b: str) -> None:
    assert len(a) <= 8 and len(b) <= 8
    assert is_http_token(a)
    assert is_http_token(b)

    header = dump_header([a, b])
    parsed = parse_list_header(header)

    assert parsed == [a, b]



def harness_parse_list_header_three_token_roundtrip(a: str, b: str, c: str) -> None:
    """
    Stronger structural claim: order and multiplicity are preserved for a small
    token-only list language generated via dump_header.
    """
    assert len(a) <= 6 and len(b) <= 6 and len(c) <= 6
    assert is_http_token(a) and is_http_token(b) and is_http_token(c)

    header = dump_header([a, b, c])
    parsed = parse_list_header(header)

    assert parsed == [a, b, c]



# ---------------------------------------------------------------------------
# parse_dict_header
# ---------------------------------------------------------------------------


def harness_parse_dict_header_two_pairs(k1: str, v1: str, k2: str, v2: str) -> None:
    """
    Semantic roundtrip claim over a clean two-pair operational sublanguage:
    the whole parsed mapping should match the mapping that was dumped.
    """
    assert len(k1) <= 6 and len(v1) <= 6 and len(k2) <= 6 and len(v2) <= 6
    assert is_http_token(k1) and is_http_token(v1)
    assert is_http_token(k2) and is_http_token(v2)
    assert not k1.endswith("*") and not k2.endswith("*")
    assert k1 != k2

    expected = {k1: v1, k2: v2}
    header = dump_header(expected)
    parsed = parse_dict_header(header)

    assert parsed == expected



def harness_parse_dict_header_bare_key(key: str) -> None:
    assert len(key) <= 8
    assert is_http_token(key)
    assert not key.endswith("*")

    parsed = parse_dict_header(key)

    assert parsed == {key: None}



def harness_parse_dict_header_mixed_roundtrip(key1: str, key2: str, value2: str) -> None:
    """
    Stronger representative behavior for a common mixed case: one bare directive
    plus one explicit scalar assignment.
    """
    assert len(key1) <= 6 and len(key2) <= 6 and len(value2) <= 6
    assert is_http_token(key1) and is_http_token(key2) and is_http_token(value2)
    assert not key1.endswith("*") and not key2.endswith("*")
    assert key1 != key2

    expected = {key1: None, key2: value2}
    header = dump_header(expected)
    parsed = parse_dict_header(header)

    assert parsed == expected


# ---------------------------------------------------------------------------
# canonicalize_name
# ---------------------------------------------------------------------------


def harness_canonicalize_name_idempotent(name: str) -> None:
    assert len(name) <= 20
    assert name != ""

    once = canonicalize_name(name)
    twice = canonicalize_name(once)

    assert twice == once



def harness_canonicalize_name_normalized_shape(name: str) -> None:
    assert len(name) <= 20
    assert name != ""
    assert name.isascii()
    assert name[0].isalnum() and name[-1].isalnum()
    assert all(ch.isalnum() or ch in "._-" for ch in name)

    normalized = canonicalize_name(name, validate=True)

    assert normalized == normalized.lower()
    assert "_" not in normalized
    assert "." not in normalized
    assert "--" not in normalized
    assert is_normalized_name(normalized)



def harness_canonicalize_name_equivalent_forms(
    left: str, right: str, sep1: str, sep2: str
) -> None:
    """
    Stronger semantic property: names that differ only by case and the choice of
    internal separator belong to the same normalization equivalence class.
    """
    assert 0 < len(left) <= 6
    assert 0 < len(right) <= 6
    assert left.isascii() and right.isascii()
    assert left.isalnum() and right.isalnum()
    assert len(sep1) == 1 and len(sep2) == 1
    assert sep1 in "._-" and sep2 in "._-"

    name1 = left + sep1 + right
    name2 = left.upper() + sep2 + right.upper()

    normalized1 = canonicalize_name(name1, validate=True)
    normalized2 = canonicalize_name(name2, validate=True)
    expected = left.lower() + "-" + right.lower()

    assert normalized1 == expected
    assert normalized2 == expected
    assert normalized1 == normalized2
