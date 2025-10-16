PROJECT_NAME = registration-bot
IMAGE_NAME = $(PROJECT_NAME):latest
CONTAINER_NAME = $(PROJECT_NAME)-container
REPOSITORY_URL = https://github.com/MrAlexandrov/registration-bot.git
DIRECTORY_NAME = registration-bot

include .env
export

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
	docker-compose build --no-cache
	docker-compose up -d
	docker-compose logs -f

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d
	docker-compose logs -f

docker-clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

.PHONY: install run docker-build docker-run docker-stop docker-clean help



.PHONY: connect
connect:
	ssh ${VM_USER}@${VM_IP_ADDRESS}

.PHONY: first-deploy
first-deploy:
	ssh ${VM_USER}@${VM_IP_ADDRESS} "git clone ${REPOSITORY_URL} || (cd ${DIRECTORY_NAME} && git pull)"
	scp -r .env credentials.json ${VM_USER}@${VM_IP_ADDRESS}:~/$(PROJECT_NAME)/

.PHONY: deploy
deploy:
	ssh ${VM_USER}@${VM_IP_ADDRESS} "cd ~/${DIRECTORY_NAME} && git pull"
	ssh ${VM_USER}@${VM_IP_ADDRESS} "cd ~/${DIRECTORY_NAME} && rm .env credentails.json"
	scp -r .env credentials.json ${VM_USER}@${VM_IP_ADDRESS}:~/$(PROJECT_NAME)/
	# TODO: Обработать данные, которые есть


# .PHONY: ci
# ci: deploy
# 	@ echo "Stopping existing screen session..."
# 	@ ssh ${VM_USER}@${VM_IP_ADDRESS} 'screen -S registration -X quit || true'
# 	echo "Running start.sh..."
# 	ssh ${VM_USER}@${VM_IP_ADDRESS} 'bash start.sh'
# 	echo "Creating new screen session..."
# 	ssh ${VM_USER}@${VM_IP_ADDRESS} 'screen -dmS registration bash -c "cd ~/$(PROJECT_NAME) && make run"'
