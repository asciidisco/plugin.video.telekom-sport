.PHONY: all test clean docs clean-pyc clean-report clean-docs clean-coverage tag commit
.DEFAULT_GOAL := all

SPHINXBUILD = sphinx-build
SPHINXPROJ = pluginvideotelekomsport
BUILDDIR = ./_build
SOURCEDIR = ./resources/lib
TEST_DIR = ./resources/test
COVERAGE_FILE = ./.coverage
COVERAGE_DIR = ./coverage
REPORT_DIR = ./report
DOCS_DIR = ./docs
FLAKE_FILES = ./addon.py,./setup.py,./resources/lib/Constants.py,./resources/lib/Utils.py,./resources/lib/Settings.py,./resources/lib/Cache.py,./resources/lib/Session.py,./resources/lib/ItemHelper.py,./resources/lib/ContentLoader.py
RADON_FILES = resources/lib/*.py ./addon.py ./setup.py
LINT_REPORT_FILE = ./report/lint.html
TEST_OPTIONS = -s --cover-package=resources.lib.Cache --cover-package=resources.lib.Constants --cover-package=resources.lib.ContentLoader --cover-package=resources.lib.Dialogs --cover-package=resources.lib.ItemHelper --cover-package=resources.lib.Session --cover-package=resources.lib.Settings --cover-package=resources.lib.Utils --cover-erase --with-coverage --cover-branches
I18N_FILES = resources/language/**/*.po
JSON_FILES = package.json .kodi-release

all: clean lint test

clean: clean-pyc clean-report clean-docs clean-coverage

clean-pyc:
		find . -name '*.pyc' -exec rm {} +
		find . -name '*.pyo' -exec rm {} +

clean-report:
		rm -rf $(REPORT_DIR)
		mkdir $(REPORT_DIR)

clean-docs:
		rm -rf $(BUILDDIR)

clean-coverage:
		rm $(COVERAGE_FILE) || exit 0
		rm -rf $(COVERAGE_DIR)
		mkdir $(COVERAGE_DIR)

lint:
		flake8 --filename=$(FLAKE_FILES)
		pylint addon setup resources --ignore=test --output-format=html > $(LINT_REPORT_FILE)
		radon cc $(RADON_FILES)
		dennis-cmd lint $(I18N_FILES)
		jsonlint $(JSON_FILES)
		rst-lint docs/index.rst --level=severe
		yamllint .travis.yml .codeclimate.yml

test:
		nosetests $(TEST_DIR) $(TEST_OPTIONS) --cover-html --cover-html-dir=$(COVERAGE_DIR)

docs:
		@$(SPHINXBUILD) $(DOCS_DIR) $(BUILDDIR) -T -c ./docs

commit:
		npm run gcz

tag:
		git config user.name "travis-ci"
		git config user.email "public@asciidisco.com"
		git remote rm origin
		git remote add origin https://asciidisco:${GITHUB_TOKEN}@github.com/asciidisco/plugin.video.telekom-sport.git
		git checkout master
		git fetch --all --tags --prune --progress
		git pull origin master
		echo "Current version: ${CURRENT_VERSION}"
		echo "Next version: ${NEXT_VERSION}"
		echo "Latest changes:"
		kodi-release -l		
		kodi-release -a -o ./Authors.md
		kodi-release -c -o ./Changelog.md
		kodi-release -u
		git add -f ./Changelog.md
		git add -f ./Authors.md
		git add package.json
		git add addon.xml
		make docs
		touch ./_build/.nojekyll
		git commit -m "chore(version): Version bump [ci skip]"
		git tag ${NEXT_VERSION}
		git push origin master
		git push --tags
		git fetch --all --tags --prune --progress

help:
		@echo "    clean-pyc"
		@echo "        Remove python artifacts."
		@echo "    clean-report"
		@echo "        Remove coverage/lint report artifacts."
		@echo "    clean-docs"
		@echo "        Remove sphinx artifacts."
		@echo "    clean-coverage"
		@echo "        Remove code coverage artifacts."
		@echo "    clean"
		@echo "        Calls all clean tasks."		
		@echo "    lint"
		@echo "        Check style with flake8, pylint & radon"
		@echo "    test"
		@echo "        Run unit tests"
		@echo "    docs"
		@echo "        Generate sphinx docs"
		@echo "    commit"
		@echo "        Commit stage changes using commitizen (needs Node)"
		@echo "    tag"
		@echo "        Builds an publishes a new release (Travis only)"				
