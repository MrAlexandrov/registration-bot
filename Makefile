# Переменные
APP_NAME=registration-bot
DOCKER_IMAGE=registration-bot-image
DOCKER_TEST_CONTAINER=registration-bot-test
TEST_DIR=tests

.PHONY: help install run build-docker docker-run docker-stop docker-clean docker-test test

help:
	@echo "Используйте 'make <command>' для запуска одной из следующих команд:"
	@echo "  install          - Установить зависимости локально"
	@echo "  run              - Запустить бота локально"
	@echo "  test             - Запустить тесты локально"
	@echo "  build-docker     - Собрать Docker-образ"
	@echo "  docker-run       - Запустить бота в Docker-контейнере"
	@echo "  docker-stop      - Остановить запущенный Docker-контейнер"
	@echo "  docker-clean     - Удалить контейнер и образ"
	@echo "  docker-test      - Запустить тесты в Docker-контейнере"

install:
	@echo "Установка зависимостей..."
	pip install -r requirements.txt

run:
	@echo "Запуск бота локально..."
	python src/main.py

build-docker:
	@echo "Сборка Docker-образа..."
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	@echo "Запуск Docker-контейнера..."
	docker run --env-file .env --name $(APP_NAME) $(DOCKER_IMAGE)

docker-stop:
	@echo "Остановка Docker-контейнера..."
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

docker-clean: docker-stop
	@echo "Удаление Docker-образа..."
	docker rmi $(DOCKER_IMAGE) || true

test:
	@echo "Запуск тестов локально..."
	pytest $(TEST_DIR)

docker-test: build-docker
	@echo "Запуск тестов в Docker-контейнере..."
	docker build -t $(DOCKER_IMAGE)-test -f Dockerfile.test .
	docker run --name $(DOCKER_TEST_CONTAINER) $(DOCKER_IMAGE)-test pytest $(TEST_DIR)
	docker rm $(DOCKER_TEST_CONTAINER)
