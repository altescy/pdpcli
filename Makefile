PWD      := $(shell pwd)
PYTHON   := poetry run python
PYTEST   := poetry run pytest
MYPY     := poetry run mypy
PYLINT   := poetry run pylint
PYLINTRC := $(PWD)/.pylintrc
MODULE   := pdpcli

.PHONY: all
all: mypy lint test

.PHONY: test
test:
	PYTHONPATH=$(PWD) $(PYTEST)

.PHONY: mypy
mypy:
	PYTHONPATH=$(PWD) $(MYPY) $(MODULE)

.PHONY: lint
lint:
	$(PYLINT) --rcfile=$(PYLINTRC) $(MODULE)

.PHONY: clean
clean: clean-pyc clean-build

.PHONY: clean-pyc
clean-pyc:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf $(MODULE).egg-info/
	rm -rf pip-wheel-metadata/
