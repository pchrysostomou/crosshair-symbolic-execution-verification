# Source Attributions

## CrossHair documentation

- Contracts and assert-based contracts:
  - https://crosshair.readthedocs.io/en/latest/contracts.html
  - https://crosshair.readthedocs.io/en/latest/kinds_of_contracts.html
- Getting started:
  - https://crosshair.readthedocs.io/en/latest/get_started.html
- PyPI package:
  - https://pypi.org/project/crosshair-tool/

## Real-world function sources used for adaptation

### Werkzeug

- `secure_filename` from:
  - https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/utils.py
- `_windows_device_files` from:
  - https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/security.py
- `parse_list_header`, `parse_dict_header`, `quote_header_value`, `dump_header` from:
  - https://raw.githubusercontent.com/pallets/werkzeug/main/src/werkzeug/http.py

### Packaging

- `canonicalize_name` from:
  - https://raw.githubusercontent.com/pypa/packaging/main/src/packaging/utils.py

## Adaptation policy

The copied code was turned into a self-contained coursework corpus with minimal,
explicit changes for symbolic execution:

- added type hints already present or compatible with the original code style
- added assert-based operational preconditions for CrossHair
- isolated a narrower ASCII-only analysis domain for `secure_filename`
- added harnesses that express operational postconditions
- kept the core logic of each selected real-world function recognizable
