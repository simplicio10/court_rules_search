.PHONY: venv install dev test lint clean help

# Variables
VENV_DIR = .venv
PYTHON = python3
SHELL := /bin/bash

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
	pytest

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
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete

clean-venv:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)

reset: clean clean-venv dev
