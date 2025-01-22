PROJECT_NAME = registration-bot
IMAGE_NAME = $(PROJECT_NAME):latest
CONTAINER_NAME = $(PROJECT_NAME)-container
REPOSITORY_URL = https://github.com/MrAlexandrov/registration-bot.git
DIRECTORY_NAME = registration-bot

include .env
export

install:
	pip install -r requirements.txt

run:
	python3 src/main.py

test:
	PYTHONPATH=src pytest tests

dump:
	bash dump.sh

drop:
	rm database.sqlite | true

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

docker-build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

docker-run:
	docker run -d -it \
		--name $(CONTAINER_NAME) \
		--env-file .env \
		$(IMAGE_NAME)

docker-stop:
	docker stop $(CONTAINER_NAME)

docker-remove:
	docker rm $(CONTAINER_NAME)

docker-clean:
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true
	docker rmi $(TEST_IMAGE_NAME) || true

.PHONY: install run docker-build docker-run docker-stop docker-remove help



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