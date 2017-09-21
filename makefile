.PHONY: all test clean

SOURCEDIR = ./resources/lib
TEST_DIR = ./resources/test
COVERAGE_DIR = ./coverage
REPORT_DIR = ./report
DOCS_DIR = ./docs

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
	flake8 --filename=./addon.py,./setup.py,./resources/lib/Constants.py,./resources/lib/Utils.py,./resources/lib/Settings.py,./resources/lib/Cache.py,./resources/lib/Session.py,./resources/lib/ItemHelper.py,./resources/lib/ContentLoader.py
	pylint addon setup resources --ignore=test --output-format=html > ./report/lint.html || exit 0
	pylint addon setup resources --ignore=test --output-format=colorized

test:
	nosetests $(TEST_DIR) -s --cover-package=resources.lib.Cache --cover-package=resources.lib.Constants --cover-package=resources.lib.ContentLoader --cover-package=resources.lib.Dialogs --cover-package=resources.lib.ItemHelper --cover-package=resources.lib.Session --cover-package=resources.lib.Settings --cover-package=resources.lib.Utils --cover-erase --with-coverage --cover-html --cover-branches --cover-html-dir=$(COVERAGE_DIR)
	nosetests $(TEST_DIR) -q -s --cover-package=resources.lib.Cache --cover-package=resources.lib.Constants --cover-package=resources.lib.ContentLoader --cover-package=resources.lib.Dialogs --cover-package=resources.lib.ItemHelper --cover-package=resources.lib.Session --cover-package=resources.lib.Settings --cover-package=resources.lib.Utils --cover-erase --with-coverage --cover-branches


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