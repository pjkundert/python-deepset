# deepset - Recursive Subset Comparison for Python

<p align="center">
  <img src="https://img.shields.io/pypi/v/deepset.svg" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/deepset.svg" alt="Python versions">
  <img src="https://img.shields.io/github/license/perry-kundert/python-deepset.svg" alt="License">
</p>

**deepset** provides recursive subset comparison for complex nested Python data structures. It implements intuitive subset/superset semantics for sets, lists, dictionaries, and tuples, allowing you to express relationships like "this nested structure is contained within that one" naturally.

## Features

- 🔍 **Recursive comparison** of deeply nested data structures
- 📊 **Subset semantics** for sets, lists, dictionaries, and tuples  
- 🔗 **Automatic conversion** of regular Python objects for comparison
- 🚫 **Zero dependencies** - uses only Python standard library
- ✅ **Comprehensive test suite** with 100% coverage

## Quick Start

```python
from deepset import deepset

# Set subset comparison
assert deepset({1, 2}) <= deepset({1, 2, 3})

# Nested structure comparison  
assert deepset({('a', frozenset({2}))}) <= deepset({('a', frozenset({2, 3}))})

# List sequential matching (order matters, intervening items allowed)
assert deepset([1, 3]) <= deepset([1, 2, 3, 4])

# Dictionary key-value subset
assert deepset({'a': 1}) <= deepset({'a': 1, 'b': 2})

# Mixed nested structures
data1 = {'sets': {frozenset({1, 2})}, 'lists': [[1, 2]]}
data2 = {'sets': {frozenset({1, 2, 3})}, 'lists': [[1, 2, 3]]}
assert deepset(data1) <= deepset(data2)
```

## Installation

```bash
pip install deepset
```

## Comparison Semantics

### Sets and Frozensets
Traditional subset comparison with recursive element matching:

```python
# Simple subset
deepset({1, 2}) <= deepset({1, 2, 3})  # True

# Nested sets - recursive comparison  
deepset({frozenset({1, 2})}) <= deepset({frozenset({1, 2, 3})})  # True
```

### Lists and Tuples  
Sequential subset matching where items from the first must appear in order in the second, but the second can have intervening items:

```python
# Sequential matching with intervening items
deepset([1, 3]) <= deepset([1, 2, 3, 4])  # True
deepset([1, 3]) <= deepset([3, 1])        # False (wrong order)

# Nested lists
deepset([[1, 2]]) <= deepset([[1, 2, 3]])  # True
```

### Dictionaries
Key subset with recursive value comparison:

```python
# Key subset + value comparison
deepset({'a': 1}) <= deepset({'a': 1, 'b': 2})          # True  
deepset({'a': [1, 2]}) <= deepset({'a': [1, 2, 3]})     # True
deepset({'a': 1, 'c': 1}) <= deepset({'a': 1, 'b': 2})  # False (missing key 'c')
```

### Operators

All standard comparison operators are supported:

```python
deepset({1, 2}) < deepset({1, 2, 3})   # True (strict subset)
deepset({1, 2}) <= deepset({1, 2})     # True (subset or equal)
deepset({1, 2}) == deepset({1, 2})     # True (equal)
deepset({1, 2, 3}) >= deepset({1, 2})  # True (superset or equal)
deepset({1, 2, 3}) > deepset({1, 2})   # True (strict superset)
```

## Development

```bash
# Clone repository
git clone https://github.com/perry-kundert/python-deepset.git
cd python-deepset

# Use Nix supplied Python, Virtual Env
make nix-venv       # Provides dev environment shell
make nix-venv-test  # Runs Makefile 'test' target in Nix dev venv

# Install development dependencies
make install-dev

# Run tests
make test

# Check code style
make style_check

# Build package
make build
```

## License

MIT License. See LICENSE file for details.

## Author

Perry Kundert <perry@dominionrnd.com>