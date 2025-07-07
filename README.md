# PyRegularExpression

A collection of reusable, well‑tested regular‑expression patterns for everyday text‑processing tasks.

## Quick start

```bash
pip install pyregularexpression
```

```python
from pyregularexpression import Patterns

email = Patterns.EMAIL.fullmatch("info@example.com")
```

The `Patterns` alias is provided for convenience and mirrors the `pyregularexpression.patterns` sub‑module.

## Project layout

```text
.
├── src/
│   └── pyregularexpression/
│       ├── __init__.py
│       ├── patterns.py
│       └── med_cohort.py
└── pyproject.toml
```

## License
Apache‑2.0 (see LICENSE for details)
