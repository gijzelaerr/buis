

.PHONY: wes-server wes-client django-server django-migrate setup django-test celery-worker npm-rundev docker npm-cypress

all: django-server

.venv/:
	virtualenv -p python3 .venv/

.venv/installed: .venv/ requirements.txt
	.venv/bin/pip install -r requirements.txt
	touch .venv/installed

setup: .venv/installed

wes-server: setup
	.venv/bin/wes-server --backend=wes_service.cwl_runner --opt runner=$(CURDIR)/.venv/bin/cwltoil \
		--opt extra=--logLevel=CRITICAL

wes-list: setup
	 .venv/bin/wes-client --proto http --host=localhost:8080 --list

wes-submit: setup
	.venv/bin/wes-client --host=localhost:8080 --proto=http --attachments=testdata/sleep.cwl testdata/sleep.cwl testdata/sleep.json

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

djang-collectstatic: setup
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
