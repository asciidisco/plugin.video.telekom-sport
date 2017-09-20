.PHONY: all test clean

SOURCEDIR = ./resources/lib
TEST_DIR = ./resources/test
COVERAGE_DIR = ./coverage
REPORT_DIR = ./report
DOCS_DIR = ./docs
MODULES=addon setup Constants

all: test

clean-pyc:
	find . -name '*.pyc' -exec rm {} +
	find . -name '*.pyo' -exec rm {} +

clean-report:
	rm -rf $(REPORT_DIR)
	mkdir $(REPORT_DIR)

clean-docs:
	rm -rf $(DOCS_DIR)
	mkdir $(DOCS_DIR)

clean-coverage:
	rm -rf $(COVERAGE_DIR)
	mkdir $(COVERAGE_DIR)

lint:
	flake8	
	pylint $(MODULES) --output-format=html > ./report/lint.html || exit 0
	pylint $(MODULES) --output-format=colorized

test:
	nosetests $(TEST_DIR) -s --cover-package=resources.lib.Constants --cover-erase --with-coverage --cover-html --cover-branches --cover-html-dir=$(COVERAGE_DIR)
	nosetests $(TEST_DIR) --quiet --cover-erase --with-coverage --cover-branches


help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-report"
	@echo "        Remove coverage/lint report artifacts."
	@echo "    clean-docs"
	@echo "        Remove pydoc artifacts."	
	@echo "    lint"
	@echo "        Check style with flake8 & pylint"	
	@echo "    test"
	@echo "        Run unit tests"