PY_FILES := $(shell find . -type f -name '*.py' -not -path './ping_check/*')
SHELL := /bin/bash

pip:
	python3 -m pip install -r requirements.txt

gen_modbus: $(PY_FILES)
	python3 __main__.py

ping_check_runner: gen_modbus

ping_check: ping_check_runner ping_check/Dockerfile
	docker build -t ping-check-runner -f ping_check/Dockerfile .

ping_check_run: ping_check
	{ \
	    ID=$$(docker ps -a -q --filter ancestor=ping-check-runner --format="{{.ID}}"); \
		if [ -n "$$ID" ]; then \
	        echo "Found container $$ID"; \
	        echo "Stopping"; \
	        docker stop $$ID; \
	        echo "Removing"; \
	        docker rm $$ID; \
	    fi; }
	docker run --env-file=.env -d --name ping-check-runner ping-check-runner

all: ping_check_run