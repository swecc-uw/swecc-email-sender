# SWECC pypi template

Get up and running quickly with a new python package.

1. Rename [`./swecc_pypi_template`](./swecc_pypi_template) to whatever your package is named
2. Find and replace `swecc_pypi_template` and `swecc-pypi-template`
3. Optionally change the python versions in [`./pyproject.toml`](./pyproject.toml) and [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

### Dev Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Commands

```bash
# lint
ruff check swecc_pypi_template

# format
black swecc_pypi_template

# type check
mypy swecc_pypi_template

# test
pytest
```

