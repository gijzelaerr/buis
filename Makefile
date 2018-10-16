
.PHONY: wes-server wes-client django-server django-migrate setup

all: django-server

requirements.txt:

.venv/: requirements.txt
	virtualenv -p python3 .venv/

.venv/bin/wes-server: .venv/
	.venv/bin/pip install -r requirements.txt

setup: .venv/bin/wes-server

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


