# Makefile

# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = python

# Targets
.PHONY: up wait-for-db makemigrations migrate run start

up:
	$(DOCKER_COMPOSE) up -d

wait-for-db:
	$(PYTHON) wait_for_db.py

makemigrations:
	$(PYTHON) manage.py makemigrations bot

migrate:
	$(PYTHON) manage.py migrate bot

run:
	$(PYTHON) manage.py runserver

createsuperuser:
	$(PYTHON) manage.py createsuperuser

start: up wait-for-db makemigrations migrate run
start2: up wait-for-db makemigrations migrate createsuperuser run 

stop:
	$(DOCKER_COMPOSE) down

remove:
	$(DOCKER_COMPOSE) down -v
	rm -rf bot/migrations/*.py
	rm -rf bot/migrations/*.pyc

restart: stop start

restart-hard: remove start2