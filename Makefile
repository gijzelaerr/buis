
all: server

requirements.txt:

.venv/: requirements.txt
	virtualenv -p python3 .venv/

.venv/bin/wes-server: 
	.venv/bin/pip install -r requirements.txt

wes-server: .venv/bin/wes-server
	.venv/bin/wes-server --backend=wes_service.cwl_runner --opt runner=cwltoil --opt extra=--logLevel=CRITICAL

wes-client: .venv/bin/wes-server
	 .venv/bin/wes-client --proto http --host=localhost:8080 --list

django-server: .venv/bin/wes-server
	.venv/bin/python buis/manage.py runserver

django-migrate: .venv/bin/wes-server
	.venv/bin/python buis/manage.py migrate


