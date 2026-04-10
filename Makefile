# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = uv run python -msphinx
SPHINXPROJ    = Wikipedia-API
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile prepare-release create-github-release run-type-check run-tests extract-vcr-json

process-readme:
	awk '/^.. PYPI-BEGIN$$/,/^.. PYPI-END$$/ {next} {print}' README.rst > README_processed.rst

pypi-html: process-readme
	cat README_processed.rst | uv run rst2html > pypi-doc.html
	echo file://$$( pwd )/pypi-doc.html

run-pre-commit:
	uv run pre-commit run -a

run-tests: run-tests-unit run-test-cli-verify run-tests-cli-unit

run-tests-unit:
	uv run pytest tests/

run-tests-integration:
	uv run pytest tests/vcr_page_sync_test.py tests/vcr_page_async_test.py tests/vcr_wiki_client_sync_test.py tests/vcr_wiki_client_async_test.py tests/vcr_pages_dict_sync_test.py tests/vcr_pages_dict_async_test.py --record-mode=none -v
	$(MAKE) extract-vcr-json

run-test-cli-verify:
	uv run ./tests/cli/test_cli.sh verify

run-test-cli-record:
	uv run ./tests/cli/test_cli.sh record

run-tests-cli-unit:
	uv run pytest tests/cli_test.py -v

extract-vcr-json:
	@echo "Extracting JSON responses from VCR cassettes..."
	uv run python scripts/extract_vcr_json.py --overwrite

run-type-check: run-type-check-library run-type-check-tests

run-type-check-library:
	uv run ty check wikipediaapi/

run-type-check-tests:
	uv run ty check tests/

run-ruff:
	uv run ruff format --check wikipediaapi/ tests/
	uv run ruff check wikipediaapi/ tests/

run-tox:
	uv run tox --version
	uv run tox

run-tox-ci:
	uv run tox --version
	uv run tox -e py

run-coverage:
	uv run pytest --cov=wikipediaapi --cov-report=term-missing --cov-report=xml tests/

run-validate-attributes-mappping:
	uv run python scripts/validate_attributes_mapping.py

run-example-sync:
	uv run python examples/example_sync.py

run-example-async:
	uv run python examples/example_async.py

requirements-all: process-readme
	uv sync -v --group dev --group build --group doc

requirements: process-readme
	uv sync -v --no-group dev --no-group doc --no-group build

requirements-dev: process-readme
	uv sync -v --group dev

requirements-doc: process-readme
	uv sync -v --group doc

requirements-build: process-readme
	uv sync -v --group build

update-pre-commit:
	for repo in `grep "repo: " .pre-commit-config.yaml | grep http | cut -f5 -d" "`; do \
		echo $$repo; \
		uv run pre-commit autoupdate --repo "$${repo}"; \
	done;

pre-release-check: run-pre-commit run-type-check run-ruff run-coverage run-tox run-example-sync run-example-async run-validate-attributes-mappping
	echo "Pre-release check was successful"

prepare-release:
	@if [ "x$(VERSION)" = "x" ]; then \
		echo "Use make prepare-release VERSION='1.2.3' [MSG='optional PR context']"; \
		exit 1; \
	fi; \
	current_branch=`git rev-parse --abbrev-ref HEAD`; \
	if [ "x$$current_branch" != "xmaster" ]; then \
		echo "prepare-release must be run from master (currently on $$current_branch)"; \
		exit 1; \
	fi; \
	if [ -n "`git status --porcelain`" ]; then \
		echo "Working tree is not clean. Commit or stash your changes first."; \
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
	make pre-release-check; \
	short_VERSION=`echo $(VERSION) | cut -f1-2 -d.`; \
	commas_VERSION=`echo $(VERSION) | sed -E 's/\./, /g'`; \
	echo "Short version: $$short_VERSION"; \
	git checkout -b release/$(VERSION); \
	sed -i.bak -E 's/^version =.*/version = "'$(VERSION)'"/' pyproject.toml && rm pyproject.toml.bak && \
	sed -i.bak -E 's/^release = .*/release = "'$(VERSION)'"/' conf.py && rm conf.py.bak && \
	sed -i.bak -E 's/^version = .*/version = "'$$short_VERSION'"/' conf.py && rm conf.py.bak && \
	sed -i.bak -E 's/^__version__ = .*/__version__ = ('"$$commas_VERSION"')/' wikipediaapi/_version.py && rm wikipediaapi/_version.py.bak; \
	make build-package check-package && \
	git commit CHANGES.rst pyproject.toml uv.lock conf.py wikipediaapi/_version.py -m "Update version to $(VERSION) for new release." && \
	git push -u origin release/$(VERSION) && \
	pr_body="Release $(VERSION)"; \
	if [ -n "$(MSG)" ]; then pr_body="$$pr_body\n\n$(MSG)"; fi; \
	gh pr create --title "Release $(VERSION)" --body "$$pr_body"

create-github-release:
	@if [ "x$(VERSION)" = "x" ]; then \
		echo "Use make create-github-release VERSION='1.2.3'"; \
		exit 1; \
	fi
	gh release create v$(VERSION) --title "v$(VERSION)" --generate-notes


build-package: process-readme
	rm -rfv dist/*.tar.gz dist/*.whl
	uv build

check-package:
	uv run twine check dist/*

install: install-package
install-package: process-readme
	uv pip install -e .

install-pre-commit:
	uv run pre-commit install

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
