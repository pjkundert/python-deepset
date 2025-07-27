# deepset - Recursive Subset Comparison for Python

[![PyPI version](https://img.shields.io/pypi/v/deepset.svg)](https://pypi.org/project/deepset/)
[![Python versions](https://img.shields.io/pypi/pyversions/deepset.svg)](https://pypi.org/project/deepset/)
[![License](https://img.shields.io/github/license/pjkundert/python-deepset.svg)](https://github.com/pjkundert/python-deepset/blob/master/LICENSE)

Recursive subset comparison for complex nested Python data structures. Express relationships like "this nested structure is contained within that one" naturally.

## Quick Start

```python
from deepset import deepset

# Set subsets
assert deepset({1, 2}) <= {1, 2, 3}  # True

# Nested structures  
assert deepset({('a', frozenset({2}))}) <= {('a', frozenset({2, 3}))}  # True

# Sequential lists (order matters, gaps allowed)
assert deepset([1, 3]) <= [1, 2, 3, 4]  # True

# Dictionary subsets
assert deepset({'a': 1}) <= {'a': 1, 'b': 2}  # True

# Mixed nested
data1 = {'sets': {frozenset({1, 2})}, 'lists': [[1, 2]]}
data2 = {'sets': {frozenset({1, 2, 3})}, 'lists': [[1, 2, 3]]}
assert deepset(data1) <= data2  # True
```

## Installation

```bash
pip install deepset
```

## Comparison Types

**Sets**: Traditional subset semantics
```python
assert deepset({1, 2}) < {1, 2, 3}  # True (strict subset)
assert deepset({frozenset({1, 2})}) <= {frozenset({1, 2, 3})}  # Recursive
```

**Lists/Tuples**: Sequential subset (order preserved, gaps allowed)
```python
assert deepset([1, 3]) <= [1, 2, 3, 4]  # True
assert not deepset([1, 3]) <= [3, 1]    # False (wrong order)
```

**Dictionaries**: Key subset + recursive value comparison
```python
assert deepset({'a': 1}) <= {'a': 1, 'b': 2}       # True (extra key)
assert deepset({'a': [1, 2]}) <= {'a': [1, 2, 3]}  # True (recursive)
```

**All Operators**: `<`, `<=`, `==`, `>=`, `>` supported

## Development

```bash
git clone https://github.com/pjkundert/python-deepset.git
cd python-deepset

# Standard development (with user provided Python, package installation)
make install-dev   # Install dev dependencies
make test          # Run tests
make style         # Format code (autopep8, black, isort)
make build         # Build package

# Nix environment (recommended for reproducible builds)
make nix-venv                   # Enter Nix + venv environment
make nix-venv-test              # Run tests in Nix environment
make nix-venv-unit-test_name    # Run specific test class

# Multi-version testing
TARGET=py310 make nix-venv-test # Test with Python 3.10
TARGET=py312 make nix-venv-test # Test with Python 3.12
```

## License

MIT License - Perry Kundert <perry@dominionrnd.com>
