
.PHONY: wes-server wes-client django-server django-migrate setup django-test celery-worker

all: django-server

.venv/:
	virtualenv -p python3 .venv/

.venv/installed: .venv/ requirements.txt
	.venv/bin/pip install -r requirements.txt
	touch .venv/installed

setup: .venv/installed

wes-server: setup
	.venv/bin/wes-server --backend=wes_service.cwl_runner --opt runner=cwltoil --opt extra=--logLevel=CRITICAL

wes-client: setup
	 .venv/bin/wes-client --proto http --host=localhost:8080 --list

django-server: setup
	.venv/bin/python ./manage.py runserver

django-migrate: setup
	.venv/bin/python ./manage.py migrate

django-makemigrations: setup
	.venv/bin/python ./manage.py makemigrations

django-loaddata: setup
	.venv/bin/python ./manage.py loaddata repositories

django-test: setup
	.venv/bin/python ./manage.py test scheduler

celery-worker: setup
	.venv/bin/celery -A buis worker -l info


