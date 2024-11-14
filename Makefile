.PHONY: venv install dev test lint clean help test-unit test-integration test-coverage

# Variables
VENV_DIR = .venv
PYTHON = python3
SHELL := /bin/bash
PYTEST_FLAGS = -v
COVERAGE_FLAGS = --cov=court_rules_search --cov-report=term-missing --cov-report=html
TEST_DIR = tests

.ONESHELL:

define activate_venv
	. $(VENV_DIR)/bin/activate && \
	pip install --upgrade pip && \
	$(1)
endef

help:
	@echo "Available commands:"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install package and dependencies"
	@echo "  make dev        - Set up complete development environment"
	@echo "  make test       - Run tests"
	@echo "  make test-unit  - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-crawler - Run only crawler tests"
	@echo "  make test-smoke - Run smoke tests"
	@echo "  make test-coverage - Run test coverage report"
	@echo "  make lint       - Run code quality checks"
	@echo "  make clean      - Remove build artifacts and cache files"
	@echo "  make clean-venv - Remove virtual environment"

venv:
	@echo "Creating virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install: venv
	@echo "Installing dependencies..."
	@source $(VENV_DIR)/bin/activate && \
	pip install --upgrade pip && \
	pip install -e ".[dev,nlp,vector]"

dev: venv install
	@echo "Setting up development environment..."
	@source $(VENV_DIR)/bin/activate && \
	pip install pre-commit && \
	pre-commit install

test: venv
	@echo "Running tests..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) $(TEST_DIR)

test-unit: venv
	@echo "Running unit tests..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "not integration" $(TEST_DIR)

test-integration: venv
	@echo "Running integration tests..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "integration" $(TEST_DIR)

test-crawler: venv
	@echo "Running crawler tests..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "crawler" $(TEST_DIR)

test-smoke: venv
	@echo "Running smoke tests..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) -m "smoke" $(TEST_DIR)

test-coverage: venv
	@echo "Generating coverage report..."
	@source $(VENV_DIR)/bin/activate && \
	pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) $(TEST_DIR) && \
	coverage html && \
	echo "Coverage report generated in htmlcov/index.html"

lint: venv
	@echo "Running linters..."
	@source $(VENV_DIR)/bin/activate && \
	ruff check . && \
	ruff format . && \
	mypy .

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete

clean-venv:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)

reset: clean clean-venv dev
