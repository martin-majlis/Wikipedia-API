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
	python3 setup.py --long-description | rst2html > pypi-doc.html
	echo file://$$( pwd )/pypi-doc.html

run-pre-commit:
	pre-commit run -a

run-tests:
	python3 -m unittest discover tests/ '*test.py'

run-type-check:
	mypy ./wikipediaapi

run-flake8:
	flake8 --max-line-length=100 wikipediaapi tests

run-tox:
	tox

run-coverage:
	coverage run --source=wikipediaapi -m unittest discover tests/ '*test.py'
	coverage report -m
	coverage xml

run-example:
	./example.py

requirements-all: requirements requirements-dev requirements-doc requirements-build

requirements:
	pip install -r requirements.txt

requirements-dev:
	pip install -r requirements-dev.txt

requirements-doc:
	pip install -r requirements-doc.txt

requirements-build:
	pip install -r requirements-build.txt

pre-release-check: run-pre-commit run-type-check run-flake8 run-coverage pypi-html run-tox run-example
	echo "Pre-release check was successful"

release: pre-release-check
	if [ "x$(MSG)" = "x" -o "x$(VERSION)" = "x" ]; then \
		echo "Use make release MSG='some msg' VERSION='1.2.3'"; \
		exit 1; \
	fi; \
	version=`grep __version__ wikipediaapi/__init__.py | sed -E 's/.*= \( *(.*), *(.*), *(.*)\)/\1.\2.\3/'`; \
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
	sed -i.bak -E 's/version=.*/version="'$(VERSION)'",/' setup.py; rm setup.py.bak; \
	sed -i.bak -E 's/^release = .*/release = "'$(VERSION)'"/' conf.py; rm conf.py.bak; \
	sed -i.bak -E 's/^version = .*/version = "'$$short_VERSION'"/' conf.py; rm conf.py.bak; \
	sed -i.bak -E 's/^__version__ = .*/__version__ = ('"$$commas_VERSION"')/' wikipediaapi/__init__.py; rm wikipediaapi/__init__.py.bak; \
	git commit .github CHANGES.rst setup.py conf.py wikipediaapi/__init__.py -m "Update version to $(VERSION) for new release." && \
	git push && \
	git tag v$(VERSION) -m "$(MSG)" && \
	git push --tags origin master


build-package:
	python setup.py sdist

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
