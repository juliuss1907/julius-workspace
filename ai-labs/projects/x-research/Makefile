.PHONY: help install test run clean lint format setup

help:
	@echo "X-Research Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  run        - Run research (requires TOPIC env var)"
	@echo "  clean      - Clean output and cache files"
	@echo "  lint       - Run linters"
	@echo ""
	@echo "Example:"
	@echo "  make run TOPIC='Ethereum L2 2026'"

install:
	pip install -r requirements.txt
	@echo "Dependencies installed"

test:
	pytest tests/ -v --cov=scripts --cov=lib

run:
	@if [ -z "$(TOPIC)" ]; then \
		echo "Error: TOPIC not set. Usage: make run TOPIC='your topic'"; \
		exit 1; \
	fi
	python scripts/main.py --topic "$(TOPIC)"

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf logs/*.log
	rm -rf working/
	@echo "Cleaned"

lint:
	black scripts/ lib/ --check
	ruff check scripts/ lib/

format:
	black scripts/ lib/
	ruff check scripts/ lib/ --fix

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from template"; \
		echo "Please edit .env with your credentials"; \
	else \
		echo ".env already exists"; \
	fi
	mkdir -p logs
	mkdir -p working/X/report/research
	@echo "Setup complete"
