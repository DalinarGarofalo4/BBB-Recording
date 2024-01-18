.PHONY: setup-dev pip-tools

PIP-TOOLS := $(shell command -v pip-compile 2> /dev/null)
pip-tools:
ifndef PIP-TOOLS
	$(error "pip-tools not installed. Install by running 'pip install --upgrade pip-tools'")
endif

include .env
export $(shell sed 's/=.*//' .env)

help:
	@echo "\x1B[0;34m====================================================\x1B[0m"
	@echo "\x1B[0;34m::::::::::: Recording API - Commands :::::::::::\x1B[0m"
	@echo "\x1B[0;34m====================================================\x1B[0m"

	@echo "\x1B[1;32m help \x1B[0m                              \x1B[1;32m -- Prints this basic help."
	@echo "\x1B[1;32m install \x1B[0m                      	    \x1B[1;32m -- Install all dependencies."
	@echo "\x1B[1;32m install-prod \x1B[0m                      \x1B[1;32m -- Install only production dependencies."
	@echo "\x1B[1;32m install-dev \x1B[0m                       \x1B[1;32m -- Install only development dependencies."
	@echo "\x1B[1;32m server \x1B[0m                            \x1B[1;32m -- Deploy server."
	@echo "\x1B[1;32m tests \x1B[0m                             \x1B[1;32m -- Run unit tests."
	@echo "\x1B[1;32m tox \x1B[0m                               \x1B[1;32m -- Run unit tests, code coverage and lint."
	@echo "\x1B[1;32m start \x1B[0m                             \x1B[1;32m -- Compile .in requirements, install all requirements and start server."
	@echo "\x1B[1;32m lint \x1B[0m                              \x1B[1;32m -- Run tox py310_lint."
	@echo "\x1B[1;32m generate-keys \x1B[0m                     \x1B[1;32m -- Generate RSA key pair."

requirements.txt: pip-tools requirements.in
	@echo "\n > ⚙\x1B[1;32m running pip-compile over requirements.in... \x1B[0m"
	pip-compile --output-file=requirements.txt requirements.in
	@echo " > ✅ \x1B[1;32m pip-compile complete... \x1B[0m \n"

requirements-dev.txt: pip-tools requirements-dev.in
	@echo "\n > ⚙\x1B[1;32m running pip-compile over requirements.in... \x1B[0m"
	pip-compile --output-file=requirements-dev.txt requirements-dev.in
	@echo " > ✅ \x1B[1;32m pip-compile complete... \x1B[0m \n"

setup-dev: pip-tools requirements.txt requirements-dev.txt
	@echo "\n > ⚙\x1B[1;32m running pip-sync over requirements and requirements-dev... \x1B[0m"
	pip-sync requirements.txt requirements-dev.txt
	@echo " > ✅ \x1B[1;32m pip-sync complete... \x1B[0m \n"

install:
	@echo "\n > ⚙\x1B[1;32m install requirements and requirements-dev... \x1B[0m"
	pip install -r requirements.txt -r requirements-dev.txt
	@echo " > ✅ \x1B[1;32m install complete... \x1B[0m \n"

install-prod:
	@echo "\n > ⚙\x1B[1;32m install requirements... \x1B[0m"
	pip install -r requirements.txt
	@echo " > ✅ \x1B[1;32m install complete... \x1B[0m \n"

install-dev:
	@echo "\n > ⚙\x1B[1;32m install requirements-dev... \x1B[0m"
	pip install -r requirements-dev.txt
	@echo " > ✅ \x1B[1;32m install complete... \x1B[0m \n"

server:
	@echo "\n > 🚀\x1B[1;32m run server... \x1B[0m"
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

start: setup-dev pip-tools install server

lint:
	@echo "\n > 🕵\x1B[1;32m running pycodestyle... \x1B[0m"
	pycodestyle app tests
	@echo " > ✅ \x1B[1;32m pycodestyle complete... \x1B[0m \n"

	@echo " > 🕵\x1B[1;32m running flake8... \x1B[0m"
	flake8 --statistics --show-source app tests
	@echo " > ✅ \x1B[1;32m flake8 complete... \x1B[0m \n"

	@echo " > 🕵\x1B[1;32m running pylint... \x1B[0m"
	pylint --disable=C,R,W --rcfile=./.pylintrc app tests
	@echo " > ✅ \x1B[1;32m pylint complete... \x1B[0m \n"

	@echo " > 🕵\x1B[1;32m running mypy... \x1B[0m"
	mypy --ignore-missing-imports tests
	@echo " > ✅ \x1B[1;32m mypy complete... \x1B[0m \n"

tox:
	@echo "\n > 🕵\x1B[1;32m running tox... \x1B[0m"
	tox -e py310,py310_lint
	@echo " > ✅ \x1B[1;32m tox complete... \x1B[0m \n"

generate-keys:
	@echo "\n > 🗝\x1B[1;32m generating RSA key pair... \x1B[0m"
	python -c "from app.utils import rsa_util; rsa_util.generate_keys()"
	@echo " > ✅ \x1B[1;32m run RSA logic complete... \x1B[0m \n"
