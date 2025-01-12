COMPOSE_FILE = docker-compose.yml

setup:
	docker-compose -f $(COMPOSE_FILE) build

start:
    docker-compose -f $(COMPOSE_FILE) up -d celery
	docker-compose -f $(COMPOSE_FILE) run app
