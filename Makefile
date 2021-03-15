PYTHON=python3.9

all: build run

build: lint test

run:
	$(PYTHON) -m src.main

dev-deps:
	pip3 install -r requirements.txt

lint:
	flake8 src/ tests/

test:
	$(PYTHON) -m unittest

.PHONY: all build run dev-deps lint test
