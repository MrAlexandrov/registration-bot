PROJECT_NAME = registration-bot
IMAGE_NAME = $(PROJECT_NAME):latest
CONTAINER_NAME = $(PROJECT_NAME)-container

install:
	pip install -r requirements.txt

run:
	python src/main.py

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

docker-build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

docker-run:
	docker run -it \
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
