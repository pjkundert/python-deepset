# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**deepset** provides recursive subset comparison for complex nested Python data structures. Single-module library implementing intuitive subset semantics for sets, lists, dictionaries, and tuples.

## Structure

```
├── deepset.py           # Main implementation (~300 lines)
├── test_deepset.py      # Test suite (38 tests)
├── pyproject.toml       # Modern Python packaging
├── Makefile            # Development automation
└── README.md           # User documentation
```

## Core Architecture

**Main Components:**
- `DeepSet` class: Wrapper with comparison operators
- `ComparisonResult` enum: Ordered relationship strength (FALSE < LT < LE < EQ)
- `recursive_compare()`: Public API mapping operators to boolean results
- `_get_comparison_strength()`: Internal enum-based comparison engine

**Key Innovation:** 
Uses ordered enum with `min()` aggregation instead of complex operator-passing recursion. Each comparison returns the strongest valid relationship, then maps to requested operator.

**Comparison Semantics:**
- **Sets**: Traditional subset with recursive element matching
- **Lists/Tuples**: Sequential subset (order preserved, gaps allowed)
- **Dicts**: Key subset + recursive value comparison  
- **Literals**: Equality only

## Development Commands

```bash
# Essential commands
make install-dev          # Install dev dependencies
make test                 # Run all tests
make nix-venv-test        # Run tests in Nix environment
make build                # Build package

# Testing specific patterns
make nix-venv-unit-TestComparisonStrength  # Run enum tests
python -m pytest test_deepset.py::TestZipCompare -v

# Code quality
make style_check          # Check formatting
make style                # Apply formatting
```

## Testing Structure

**38 tests across 8 test classes:**
- Core comparison logic for each data type
- Operator overloading (`<`, `<=`, `==`, `>=`, `>`)
- Edge cases and error conditions
- New enum-based comparison strength tests

**Key test pattern:**
```python
# Remove unnecessary deepset() calls on RHS
assert deepset({1, 2}) <= {1, 2, 3}  # Auto-converts RHS
assert deepset([1, 3]) <= [1, 2, 3, 4]  # Sequential subset
assert deepset({'a': 1}) <= {'a': 1, 'b': 2}  # Key subset
```

## Nix Environment

**Multi-version testing:**
```bash
make nix-venv-test         # Python 3.13 (default)
TARGET=py310 make nix-test # Python 3.10
TARGET=py312 make nix-test # Python 3.12
```

## Key Implementation Details

**ComparisonResult enum ordering enables `min()` aggregation:**
```python
result = ComparisonResult.EQ  # Start optimistic
for child in nested_items:
    child_result = _get_comparison_strength(child_a, child_b)
    result = min(result, child_result)  # Weakest relationship wins
```

**Error handling:**
- `ZipCompareError` for sequential matching failures with ordinal positioning
- Detailed error messages show which item failed and where

**No runtime dependencies** - pure Python stdlib implementation.