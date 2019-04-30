.PHONY: django-server django-migrate setup django-test celery-worker npm-rundev docker npm-cypress

# by default we want to run the django server
all: django-server


## General setup make targets

.venv/:
	python3 -m venv .venv/

.venv/installed: .venv/ requirements.txt
	.venv/bin/pip install -r requirements.txt
	touch .venv/installed

.venv/bin/docker-compose: .venv/
	curl -L https://github.com/docker/compose/releases/download/1.24.0/docker-compose-`uname -s`-`uname -m` -o .venv/bin/docker-compose
	chmod 755 .venv/bin/docker-compose

setup: .venv/installed


## Django related make targets

django-server: setup
	.venv/bin/python ./manage.py runserver

django-migrate: setup
	.venv/bin/python ./manage.py migrate

django-makemigrations: setup
	.venv/bin/python ./manage.py makemigrations

django-loaddata: setup
	.venv/bin/python ./manage.py loaddata repositories

django-test: setup
	.venv/bin/python ./manage.py test

django-createsuperuser: setup
	.venv/bin/python ./manage.py createsuperuser

django-collectstatic: setup
	.venv/bin/python ./manage.py collectstatic


celery-worker: setup
	DJANGO_SETTINGS_MODULE="buis.settings.dev" .venv/bin/celery -A buis worker -l info


## Javascript frontend related make targets

node_modules/:
	npm update

npm-rundev: node_modules/
	npm run dev

npm-cypress: node_modules/
	npm run cypress


## Docker related make targets

docker:
	docker build . -t gijzelaerr/buis

docker-shell:
	docker run -ti  -v /var/run/docker.sock:/var/run/docker.sock gijzelaerr/buis bash

docker-compose-up: .venv/bin/docker-compose
	.venv/bin/docker-compose up

docker-compose-migrate: .venv/bin/docker-compose
	.venv/bin/docker-compose run web python3 manage.py migrate

docker-compose-createsuperuser: .venv/bin/docker-compose
	.venv/bin/docker-compose run web python3  ./manage.py createsuperuser

docker-compose-build:
	.venv/bin/docker-compose build
