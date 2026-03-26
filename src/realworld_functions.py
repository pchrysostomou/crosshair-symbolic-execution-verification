from __future__ import annotations

"""
Self-contained, minimally adapted real-world Python functions for CrossHair analysis.

Selected functions and sources:
1. secure_filename_ascii_domain:
   Adapted from werkzeug.utils.secure_filename
   Source (Werkzeug main branch):
   https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/utils.py

2. parse_list_header:
   Adapted from werkzeug.http.parse_list_header
   Source (Werkzeug main branch):
   https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/http.py

3. parse_dict_header:
   Adapted from werkzeug.http.parse_dict_header
   Source (Werkzeug main branch):
   https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/http.py

4. canonicalize_name:
   Adapted from packaging.utils.canonicalize_name
   Source (packaging main branch):
   https://raw.githubusercontent.com/pypa/packaging/main/src/packaging/utils.py

Important adaptation note:
- secure_filename_ascii_domain intentionally restricts the input domain to ASCII.
  Over that domain, Werkzeug's unicode normalization and ascii encode/decode steps
  are semantic no-ops, so they are omitted to keep symbolic execution tractable.
"""

import os
import re
from typing import Any, Dict, Iterable, List, Mapping, NewType, Optional, Union, cast
from urllib.parse import unquote
from urllib.request import parse_http_list as _parse_list_header


# ---------------------------------------------------------------------------
# Shared helpers copied or derived from the original projects
# ---------------------------------------------------------------------------

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = {
    "AUX",
    "CON",
    "CONIN$",
    "CONOUT$",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
    "NUL",
    "PRN",
}

_token_chars = frozenset(
    "!#$%&'*+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~"
)

_charset_value_re = re.compile(
    r"""
    ([\w!#$%&*+\-.^`|~]*)'      # charset part, could be empty
    [\w!#$%&*+\-.^`|~]*'        # language part, usually empty
    ([\w!#$%&'*+\-.^`|~]+)      # token chars, maybe percent-encoded
    """,
    re.ASCII | re.VERBOSE,
)

_validate_regex = re.compile(
    r"[A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9]",
    re.IGNORECASE,
)
_normalized_regex = re.compile(r"[a-z0-9]|[a-z0-9]([a-z0-9-](?!--))*[a-z0-9]")

NormalizedName = NewType("NormalizedName", str)


class InvalidName(ValueError):
    """Invalid distribution/package name."""


# ---------------------------------------------------------------------------
# Selected real-world functions
# ---------------------------------------------------------------------------


def secure_filename_ascii_domain(filename: str) -> str:
    """
    ASCII-domain adaptation of Werkzeug's secure_filename.

    Preconditions for the operational CrossHair analysis:
    - input is ASCII only

    Why the adaptation is faithful on this domain:
    - unicodedata.normalize("NFKD", filename) is the identity for ASCII strings
    - encode("ascii", "ignore").decode("ascii") is also the identity for ASCII
      strings
    """
    assert filename.isascii(), "Operational domain: ASCII-only filenames."

    for sep in (os.sep, os.path.altsep):
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename



def quote_header_value(value: Any, allow_token: bool = True) -> str:
    """Helper adapted from Werkzeug's quote_header_value."""
    value_str = str(value)

    if not value_str:
        return '""'

    if allow_token and _token_chars.issuperset(value_str):
        return value_str

    value_str = value_str.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value_str}"'



def dump_header(iterable: Union[Mapping[str, Any], Iterable[Any]]) -> str:
    """Helper adapted from Werkzeug's dump_header."""
    if isinstance(iterable, dict):
        items: List[str] = []
        for key, value in iterable.items():
            if value is None:
                items.append(key)
            elif key[-1] == "*":
                items.append(f"{key}={value}")
            else:
                items.append(f"{key}={quote_header_value(value)}")
    else:
        items = [quote_header_value(x) for x in iterable]
    return ", ".join(items)



def parse_list_header(value: str) -> List[str]:
    """
    Adapted from Werkzeug's parse_list_header.

    This removes surrounding double quotes from list items.
    """
    assert "\r" not in value and "\n" not in value, "Header value must be one line."

    result: List[str] = []
    for item in _parse_list_header(value):
        if len(item) >= 2 and item[0] == item[-1] == '"':
            item = item[1:-1]
        result.append(item)
    return result



def parse_dict_header(value: str) -> Dict[str, Optional[str]]:
    """
    Adapted from Werkzeug's parse_dict_header.

    For operational contracts we mostly exercise the non-RFC2231 path, but the
    implementation still includes the charset branch from Werkzeug.
    """
    assert "\r" not in value and "\n" not in value, "Header value must be one line."

    result: Dict[str, Optional[str]] = {}

    for item in parse_list_header(value):
        key, has_value, item_value = item.partition("=")
        key = key.strip()

        if not key:
            continue

        if not has_value:
            result[key] = None
            continue

        item_value = item_value.strip()
        encoding: Optional[str] = None

        if key[-1] == "*":
            key = key[:-1]
            match = _charset_value_re.match(item_value)
            if match:
                encoding, item_value = match.groups()
                encoding = encoding.lower()
                if encoding in {"ascii", "us-ascii", "utf-8", "iso-8859-1"}:
                    item_value = unquote(item_value, encoding=encoding)

        if len(item_value) >= 2 and item_value[0] == item_value[-1] == '"':
            item_value = item_value[1:-1]

        result[key] = item_value

    return result



def canonicalize_name(name: str, validate: bool = False) -> NormalizedName:
    """
    Adapted from packaging.utils.canonicalize_name.

    Replaces runs of '-', '_' and '.' with a single '-', and lowercases the name.
    """
    assert len(name) <= 40, "Operational bound to reduce path explosion."

    if validate and not _validate_regex.fullmatch(name):
        raise InvalidName(f"name is invalid: {name!r}")

    value = name.lower().replace("_", "-").replace(".", "-")

    while "--" in value:
        value = value.replace("--", "-")

    return cast("NormalizedName", value)


# ---------------------------------------------------------------------------
# Tiny predicates/helpers used by the CrossHair harnesses
# ---------------------------------------------------------------------------


def is_http_token(text: str) -> bool:
    return text != "" and _token_chars.issuperset(text)



def is_normalized_name(text: str) -> bool:
    return _normalized_regex.fullmatch(text) is not None



def has_no_path_separators(text: str) -> bool:
    return "/" not in text and "\\" not in text



def has_clean_edges(text: str) -> bool:
    return text == "" or (
        not text.startswith(".")
        and not text.endswith(".")
        and not text.startswith("_")
        and not text.endswith("_")
    )



def is_ascii_filename_char(ch: str) -> bool:
    return len(ch) == 1 and ch.isascii() and (ch.isalnum() or ch in "._-")



def is_already_safe_ascii_filename(text: str) -> bool:
    return (
        text != ""
        and text.isascii()
        and has_no_path_separators(text)
        and has_clean_edges(text)
        and all(is_ascii_filename_char(ch) for ch in text)
    )



def contains_ascii_alnum(text: str) -> bool:
    return any(ch.isascii() and ch.isalnum() for ch in text)
