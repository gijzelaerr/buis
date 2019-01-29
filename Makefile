.PHONY: django-server django-migrate setup django-test celery-worker npm-rundev docker npm-cypress

all: django-server

.venv/:
	virtualenv -p python3 .venv/

.venv/installed: .venv/ requirements.txt
	.venv/bin/pip install -r requirements.txt
	touch .venv/installed

setup: .venv/installed

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

node_modules/:
	npm update

npm-rundev: node_modules/
	npm run dev

npm-cypress: node_modules/
	npm run cypress

docker:
	docker build . -t gijzelaerr/buis
