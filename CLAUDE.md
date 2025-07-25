# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**deepset** is a Python library that provides recursive comparison for nested Python data structures. It implements a `DeepSet` class that allows comparing complex nested data structures (sets, lists, dictionaries, tuples) using subset/superset semantics rather than simple equality.

### Key Features
- Recursive comparison of nested data structures
- Support for sets, frozensets, lists, tuples, and dictionaries
- Subset/superset comparison operators (`<=`, `<`, `>=`, `>`, `==`, `!=`)
- Automatic conversion of regular Python objects to DeepSet objects for comparison

## Project Structure

```
├── deepset.py           # Main library implementation (single module)
├── test_deepset.py      # Comprehensive test suite  
├── pyproject.toml       # Modern Python packaging configuration
├── Makefile            # Build automation and development tasks
├── shell.nix           # Nix development environment
├── default.nix         # Nix build definitions for multiple Python versions
└── nixpkgs.nix         # Nix package source configuration
```

## Core Components

### Main Module: `deepset.py`

**Key Classes:**
- `DeepSet`: Main class implementing recursive comparison operators
- `ZipCompareError`: Exception for comparison failures

**Key Functions:**
- `deepset(data)`: Convenience function to create DeepSet instances
- `recursive_compare(a, b, op)`: Core recursive comparison logic
- `zip_compare(a, b, op)`: Sequential iterable comparison with ordered subset matching
- `ordinal(num)`: Utility for generating ordinal numbers (1st, 2nd, etc.)

**Comparison Logic:**
- **Mappings (dicts)**: Key-based subset comparison, recursive value comparison
- **Sets**: Element-wise subset matching with recursive comparison for complex elements
- **Iterables**: Sequential matching where each element in first must match some element at same or later position in second
- **Literals**: Fall back to standard Python comparison operators

## Build System & Development

### Package Configuration: `pyproject.toml`
- **Build System**: Uses modern `setuptools` with `build` backend
- **Python Support**: 3.6+ (3.6 through 3.12)
- **License**: MIT
- **Author**: Perry Kundert <perry@dominionrnd.com>

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "build",
    "setuptools", 
    "wheel",
    "pytest>=6.0",
    "black>=20.0",
    "flake8",
    "isort>=5.0",
]
```

### Makefile Commands

**Essential Commands:**
```bash
# Package building
make build                # Build distribution packages
make install              # Install in development mode
make install-dev          # Install with dev dependencies

# Testing
make test                 # Run all tests with pytest
make unit-<pattern>       # Run tests matching pattern

# Code quality
make style_check          # Check code formatting (black, isort)
make style                # Apply code formatting

# Cleanup
make clean                # Remove all build artifacts
make clean-build          # Remove build artifacts only
make clean-pyc            # Remove Python cache files
make clean-test           # Remove test artifacts

# Development environments
make venv                 # Create and activate virtual environment
make venv-<target>        # Run target in virtual environment
make nix-<target>         # Run target in Nix environment
```

### Nix Development Environment

The project includes sophisticated Nix configuration for reproducible development:

**Files:**
- `shell.nix`: Development shell with configurable Python versions
- `default.nix`: Build definitions for Python 3.10-3.13
- `nixpkgs.nix`: Pinned nixpkgs version (25.05)

**Usage:**
```bash
# Enter default Python 3.13 environment
nix-shell

# Use specific Python version
TARGET=py312 nix-shell

# Run commands in Nix environment
make nix-test
make nix-build
```

## Testing

**Test Organization:**
- `TestDeepSetSets`: Set and frozenset comparison tests
- `TestDeepSetLists`: List and tuple comparison tests  
- `TestDeepSetDicts`: Dictionary comparison tests
- `TestDeepSetMixed`: Complex nested structure tests
- `TestDeepSetOperators`: Operator overloading tests
- `TestDeepSetEdgeCases`: Edge cases and error conditions
- `TestDeepSetInitialization`: Object creation tests
- `TestZipCompare`: Low-level zip_compare function tests

**Key Test Patterns:**
```python
# Basic subset comparison
assert deepset({1, 2}) <= deepset({1, 2, 3})

# Nested structure comparison
assert deepset({("a", frozenset({2}))}) <= deepset({("a", frozenset({2, 3}))})

# Sequential matching in lists
assert deepset([1, 2]) <= deepset([0, 1, 'a', 2, 3])

# Dictionary key-value subset
assert deepset({"a": 1}) <= deepset({"a": 1, "b": 2})
```

## Development Workflow

### Quick Start
```bash
# Setup development environment
make install-dev

# Run tests  
make test

# Run specific test class
python -m pytest test_deepset.py::TestZipCompare -v

# Check code style
make style_check

# Build package
make build
```

### Using Nix (Recommended for Reproducibility)
```bash
# Enter development environment
nix-shell

# Run tests in clean environment
make nix-test

# Test against multiple Python versions
TARGET=py310 make nix-test
TARGET=py311 make nix-test
TARGET=py312 make nix-test
TARGET=py313 make nix-test
```

### Code Style
- **Formatter**: Black (line length: 88)
- **Import Sorting**: isort (black profile)
- **Linting**: flake8

## Common Development Tasks

### Adding New Comparison Logic
1. Modify `recursive_compare()` function in `deepset.py`
2. Add corresponding test cases in `test_deepset.py`
3. Run `make test` to verify
4. Run `make style` to format code

### Debugging Comparison Issues
- Use `zip_compare()` function directly to understand sequential matching
- Check `ZipCompareError` messages for detailed failure information
- Add debug prints in `recursive_compare()` to trace comparison paths

### Performance Considerations
- The library prioritizes correctness over performance
- Recursive comparison can be expensive for deeply nested structures
- Consider caching strategies for repeated comparisons of large data structures

## Key Architecture Details

**Comparison Semantics:**
- For iterables (lists/tuples): Sequential subset matching where items from first must appear in order in second, but second can have intervening items
- For sets: Element-wise subset matching with recursive comparison for nested structures  
- For mappings: Key subset + recursive value comparison for shared keys
- For literals: Standard Python equality/comparison

**Error Handling:**
- `ZipCompareError` provides detailed error messages with ordinal positioning
- `recursive_compare()` returns `False` on comparison failure, `zip_compare()` raises exceptions

## Dependencies
- **Runtime**: None (uses only Python standard library)
- **Development**: pytest, black, flake8, isort, build tools
- **Python Versions**: 3.6+ supported, 3.10-3.13 tested in Nix

This library is designed as a lightweight, dependency-free solution for complex data structure comparison with intuitive subset semantics.