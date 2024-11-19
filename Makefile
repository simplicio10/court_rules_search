.PHONY: build up down shell install dev test lint clean help test-unit test-integration test-coverage

# Variables
DOCKER_COMPOSE = docker compose
DOCKER_APP = $(DOCKER_COMPOSE) exec app
SHELL := /bin/bash
PYTEST_FLAGS = -v
COVERAGE_FLAGS = --cov=court_rules_search --cov-report=term-missing --cov-report=html
TEST_DIR = tests

help:
	@echo "Available commands:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start Docker containers"
	@echo "  make down      - Stop Docker containers"
	@echo "  make shell     - Open shell in app container"
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

build:
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) build

up:
	@echo "Starting Docker containers..."
	$(DOCKER_COMPOSE) up -d

down:
	@echo "Stopping Docker containers..."
	$(DOCKER_COMPOSE) down

shell:
	@echo "Opening shell in app container..."
	$(DOCKER_APP) /bin/bash

install:
	@echo "Installing dependencies..."
	$(DOCKER_APP) pip install -e ".[dev,nlp,vector]"

dev:
	@echo "Setting up development environment..."
	@git config --unset-all core.hooksPath || true
	$(DOCKER_APP) git config --global user.name "$$GIT_AUTHOR_NAME"
	$(DOCKER_APP) git config --global user.email "$$GIT_AUTHOR_EMAIL"
	$(DOCKER_APP) pre-commit install --install-hooks
	@mkdir -p .git/hooks
	@echo '#!/bin/bash' > .git/hooks/pre-commit
	@echo 'docker compose exec -T app pre-commit run --files $$(git diff --cached --name-only)' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed"

test:
	@echo "Running tests..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) $(TEST_DIR)

test-unit:
	@echo "Running unit tests..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "not integration" $(TEST_DIR)

test-integration:
	@echo "Running integration tests..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "integration" $(TEST_DIR)

test-crawler:
	@echo "Running crawler tests..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) -m "crawler" $(TEST_DIR)

test-smoke:
	@echo "Running smoke tests..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) -m "smoke" $(TEST_DIR)

test-coverage:
	@echo "Generating coverage report..."
	$(DOCKER_APP) pytest $(PYTEST_FLAGS) $(COVERAGE_FLAGS) $(TEST_DIR)
	echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running linters..."
	$(DOCKER_APP) ruff check .
	$(DOCKER_APP) ruff format .
	$(DOCKER_APP) mypy .

clean:
	@echo "Cleaning build artifacts..."
	$(DOCKER_APP) rm -rf build/
	$(DOCKER_APP) rm -rf dist/
	$(DOCKER_APP) rm -rf *.egg-info/
	$(DOCKER_APP) rm -rf .pytest_cache/
	$(DOCKER_APP) rm -rf .ruff_cache/
	$(DOCKER_APP) rm -rf .mypy_cache/
	$(DOCKER_APP) rm -rf htmlcov/
	$(DOCKER_APP) rm -rf .coverage
	$(DOCKER_APP) rm -rf .coverage.*
	$(DOCKER_APP) find . -type d -name __pycache__ -exec rm -rf {} +
	$(DOCKER_APP) find . -type f -name "*.pyc" -delete
	$(DOCKER_APP) find . -type f -name "*.pyo" -delete
	$(DOCKER_APP) find . -type f -name ".coverage" -delete

reset: down
	@echo "Performing full cleanup and rebuild..."
	$(DOCKER_COMPOSE) down -v
	docker system prune -f
	$(MAKE) build
	$(MAKE) up
	$(MAKE) dev
