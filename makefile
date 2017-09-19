SOURCEDIR = ./resources/lib
TEST_DIR = ./test
COVERAGE_DIR = ./coverage

all: test

clean-pyc:
	find . -name '*.pyc' -exec rm {} +
	find . -name '*.pyo' -exec rm {} +

test:
	nosetests $(TEST_DIR) -s --nocapture --cover-erase --with-coverage --cover-html --cover-branches --cover-html-dir=$(COVERAGE_DIR)
	nosetests $(TEST_DIR) --quiet -s --cover-erase --with-coverage --cover-branches


help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    test"
	@echo "        Run unit tests"
