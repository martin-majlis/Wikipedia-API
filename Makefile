# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python3 -msphinx
SPHINXPROJ    = Wikipedia-API
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

pypi-html:
	cat README.rst | uv run rst2html > pypi-doc.html
	echo file://$$( pwd )/pypi-doc.html

run-pre-commit:
	uv run pre-commit run -a

run-tests: run-tests-unit run-test-cli-verify

run-tests-unit:
	uv run python -m unittest discover tests/ '*test.py'

run-test-cli-verify: install
	uv run ./tests/cli/test_cli.sh verify

run-test-cli-record: install
	uv run ./tests/cli/test_cli.sh record

run-type-check:
	uv run mypy ./wikipediaapi

run-flake8:
	uv run flake8 --max-line-length=100 wikipediaapi tests

run-tox:
	uv run tox --version
	uv run tox

run-tox-ci:
	uv run tox --version
	uv run tox -e py

run-coverage:
	uv run coverage run --source=wikipediaapi -m unittest discover tests/ '*test.py'
	uv run coverage report -m
	uv run coverage xml

run-example:
	./example.py

requirements-all:
	uv sync -v

requirements:
	uv sync -v --no-group dev --no-group doc --no-group build

requirements-dev:
	uv sync -v --no-group doc --no-group build

requirements-doc:
	uv sync -v --group doc

requirements-build:
	uv sync -v --no-group doc

update-pre-commit:
	for repo in `grep "repo: " .pre-commit-config.yaml | grep http | cut -f5 -d" "`; do \
		echo $$repo; \
		uv run pre-commit autoupdate --repo "$${repo}"; \
	done;

pre-release-check: run-pre-commit run-type-check run-flake8 run-coverage pypi-html run-tox run-example
	echo "Pre-release check was successful"

release: pre-release-check
	if [ "x$(MSG)" = "x" -o "x$(VERSION)" = "x" ]; then \
		echo "Use make release MSG='some msg' VERSION='1.2.3'"; \
		exit 1; \
	fi; \
	version=`grep '^__version__ = ' wikipediaapi/_version.py | sed -E 's/.*= \( *(.*), *(.*), *(.*)\)/\1.\2.\3/'`; \
	if [ "x$$version" = "x" ]; then \
		echo "Unable to extract version"; \
		exit 1; \
	fi; \
	echo "Current version: $$version"; \
	as_number() { \
		total=0; \
		for p in `echo $$1 | tr "." "\n"`; do \
			total=$$(( $$total * 1000 + $$p )); \
		done; \
		echo $$total; \
	}; \
	number_dots=`echo $(VERSION) | tr -cd '.' | wc -c | tr -d ' '`; \
	echo "$(VERSION) has $${number_dots} dots"; \
	if [ ! "$${number_dots}" = "2" ]; then \
		echo "Version has to have format X.Y.Z"; \
		echo "Number of dots: $${number_dots}"; \
		echo "Specified version is $(VERSION)"; \
		exit 2; \
	fi; \
	number_version=`as_number $$version`; \
	number_VERSION=`as_number $(VERSION);`; \
	if [ $$number_version -ge $$number_VERSION ]; then \
		echo -n "Specified version $(VERSION) ($$number_VERSION) is lower than"; \
		echo "current version $$version ($$number_version)"; \
		echo "New version has to be greater"; \
		exit 2; \
	fi; \
	has_documentation=`grep -c "^$(VERSION)\\$$" CHANGES.rst`; \
	if [ $$has_documentation -eq 0 ]; then \
		echo "There is no information about $(VERSION) in CHANGES.rst"; \
		exit 3; \
	fi; \
	short_VERSION=`echo $(VERSION) | cut -f1-2 -d.`; \
	commas_VERSION=`echo $(VERSION) | sed -E 's/\./, /g'`; \
	echo "Short version: $$short_VERSION"; \
	sed -i.bak -E 's/version=.*/version = "'$(VERSION)'",/' pyproject.toml; rm pyproject.toml.bak; \
	sed -i.bak -E 's/^release = .*/release = "'$(VERSION)'"/' conf.py; rm conf.py.bak; \
	sed -i.bak -E 's/^version = .*/version = "'$$short_VERSION'"/' conf.py; rm conf.py.bak; \
	sed -i.bak -E 's/^__version__ = .*/__version__ = ('"$$commas_VERSION"')/' wikipediaapi/_version.py; rm wikipediaapi/_version.py.bak; \
	git commit .github CHANGES.rst pyproject.toml conf.py wikipediaapi/_version.py -m "Update version to $(VERSION) for new release." && \
	git push && \
	git tag v$(VERSION) -m "$(MSG)" && \
	git push --tags origin master


build-package:
	uv build

install: install-package
install-package:
	uv pip install -e .

install-pre-commit:
	uv run pre-commit install

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
