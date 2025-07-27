SHELL		:= /bin/bash

PYTHON		?= $(shell python3 --version >/dev/null 2>&1 && echo python3 || echo python )

# Ensure $(PYTHON), $(VENV) are re-evaluated at time of expansion, when target 'python' and 'venv' are known to be available
PYTHON_V	= $(shell $(PYTHON) -c "import sys; print('-'.join((('venv' if sys.prefix != sys.base_prefix else next(iter(filter(None,sys.base_prefix.split('/'))))),sys.platform,sys.implementation.cache_tag)))" 2>/dev/null )

VERSION		= $(shell sed -n 's/^version = "\([^"]*\)"/\1/p' pyproject.toml)
VENV_OPTS	=
VENV		= $(CURDIR)-$(VERSION)-$(PYTHON_V)

PYTEST		?= pytest
PYTEST_OPTS	= # -vv --capture=no

build:
	$(PYTHON) -m build

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

test:
	$(PYTEST) $(PYTEST_OPTS)

# Run all tests with names matching the target string
unit-%:
	$(PYTEST) $(PYTEST_OPTS) -k $*

style_check:
	isort --check-only deepset.py *.py
	black deepset.py *.py --check

style:
	autopep8 --in-place --select=W291,W293 deepset.py *.py
	black deepset.py *.py
	isort deepset.py *.py

# 
# Nix and VirtualEnv build, install and activate
#
#     Create, start and run commands in "interactive" shell with a python venv's activate init-file.
# Doesn't allow recursive creation of a venv with a venv-supplied python.  Alters the bin/activate
# to include the user's .bashrc (eg. Git prompts, aliases, ...).  Use to run Makefile targets in a
# proper context, for example to obtain a Nix environment containing the proper Python version,
# create a python venv with the current Python environment.
#
#     make nix-venv-build
#
nix-%:
	@if [ -r flake.nix ]; then \
	    nix develop $(NIX_OPTS) --command make $*; \
        else \
	    nix-shell $(NIX_OPTS) --run "make $*"; \
	fi

venv-%:			$(VENV)
	@echo; echo "*** Running in $< VirtualEnv: make $*"
	@bash --init-file $</bin/activate -ic "make $*"

venv:			$(VENV)
	@echo; echo "*** Activating $< VirtualEnv for Interactive $(SHELL)"
	@bash --init-file $</bin/activate -i

$(VENV):
	@[[ "$(PYTHON_V)" =~ "^venv" ]] && ( echo -e "\n\n!!! $@ Cannot start a venv within a venv"; false ) || true
	@echo; echo "*** Building $@ VirtualEnv..."
	@rm -rf $@ && $(PYTHON) -m venv $(VENV_OPTS) $@ && sed -i -e '1s:^:. $$HOME/.bashrc\n:' $@/bin/activate \
	    && source $@/bin/activate \
	    && make install-dev

print-%:
	@echo $* = $($*)
	@echo $*\'s origin is $(origin $*)


.PHONY: clean clean-build clean-pyc clean-test test style_check style venv
