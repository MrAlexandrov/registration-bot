# Makefile

# Переменные
PROJECT_NAME = pioneer_trip_bot
IMAGE_NAME = $(PROJECT_NAME):latest
TEST_IMAGE_NAME = $(PROJECT_NAME)-test:latest
CONTAINER_NAME = $(PROJECT_NAME)-container

# Цели по умолчанию
.PHONY: install run test clean docker-build docker-run docker-test docker-clean

# Локальные команды

install:
	pip install -r requirements.txt

run:
	python src/main.py

test:
	pytest tests/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

# Команды для Docker

docker-build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

docker-run:
	docker run --rm -it \
		--name $(CONTAINER_NAME) \
		--env-file .env \
		$(IMAGE_NAME)

docker-test:
	docker build -t $(TEST_IMAGE_NAME) -f Dockerfile.test .
	docker run --rm \
		--env-file .env \
		$(TEST_IMAGE_NAME)

docker-clean:
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true
	docker rmi $(TEST_IMAGE_NAME) || true
