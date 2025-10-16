install:
	poetry install

run:
	poetry run python -m src.main

test:
	poetry run pytest tests

test-cov:
	poetry run pytest tests --cov=src --cov-report=term-missing --cov-report=html

test-cov-report:
	poetry run pytest tests --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	poetry run ruff check src tests

format:
	poetry run ruff check --fix --unsafe-fixes src tests
	poetry run ruff format src tests

dump:
	bash dump.sh

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

up:
	docker-compose down
	docker-compose up -d
	docker-compose logs -f

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	docker-compose logs -f

docker-clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

.PHONY: install run test test-cov test-cov-report lint format dump clean up down restart docker-clean
