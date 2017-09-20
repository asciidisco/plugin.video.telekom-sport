.PHONY: all test clean

SOURCEDIR = ./resources/lib
TEST_DIR = ./resources/test
COVERAGE_DIR = ./coverage

all: test

clean-pyc:
	find . -name '*.pyc' -exec rm {} +
	find . -name '*.pyo' -exec rm {} +

test:
	nosetests $(TEST_DIR) --nocapture --cover-erase --with-coverage --cover-html --cover-branches --cover-html-dir=$(COVERAGE_DIR)
	nosetests $(TEST_DIR) --quiet --cover-erase --with-coverage --cover-branches


help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    test"
	@echo "        Run unit tests"