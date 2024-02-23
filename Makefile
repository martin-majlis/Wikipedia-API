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
	python3 setup.py --long-description | rst2html.py > pypi-doc.html

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

requirements:
	pip3 install -r requirements.txt

requirements-dev:
	pip3 install -r requirements-dev.txt

requirements-build:
	pip3 install -r requirements-build.txt

pre-release-check: run-type-check run-flake8 run-coverage pypi-html run-tox
	echo "Pre-release check was successful"

release:
	if [ "x$(MSG)" = "x" -o "x$(VERSION)" = "x" ]; then \
		echo "Use make release MSG='some msg' VERSION='1.2.3'"; \
		exit 1; \
	fi; \
	version=`grep __version__ wikipediaapi/__init__.py | sed -r 's/.*= \( *(.*), *(.*), *(.*)\)/\1.\2.\3/'`; \
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
	number_dots=`echo -n $(VERSION) | sed -r 's/[^.]//g' | wc -c`; \
	if [ ! "$${number_dots}" = "2" ]; then \
		echo "Version has to have format X.Y.Z"; \
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
	commas_VERSION=`echo $(VERSION) | sed -r 's/\./, /g'`; \
	echo "Short version: $$short_VERSION"; \
	sed -ri 's/version=.*/version="'$(VERSION)'",/' setup.py; \
	sed -ri 's/^release = .*/release = "'$(VERSION)'"/' conf.py; \
	sed -ri 's/^version = .*/version = "'$$short_VERSION'"/' conf.py; \
	sed -ri 's/^__version__ = .*/__version__ = ('"$$commas_VERSION"')/' wikipediaapi/__init__.py; \
	git commit setup.py conf.py wikipediaapi/__init__.py -m "Update version to $(VERSION) for new release."; \
	git push; \
	git tag v$(VERSION) -m "$(MSG)"; \
	git push --tags origin master

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
