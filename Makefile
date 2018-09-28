
all: server

requirements.txt:

.venv/: requirements.txt
	virtualenv -p python3 .venv/

.venv/bin/wes-server: .venv/
	.venv/bin/pip install -r requirements.txt

server: .venv/bin/wes-server
	.venv/bin/wes-server --backend=wes_service.cwl_runner --opt runner=cwltoil --opt extra=--logLevel=CRITICAL

client:
	 .venv/bin/wes-client --proto http --host=localhost:8080 --list
