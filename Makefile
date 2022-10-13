$(eval venv         := .venv)
$(eval pip          := $(venv)/bin/pip)
$(eval python       := $(venv)/bin/python)
$(eval black        := $(venv)/bin/black)
$(eval isort        := $(venv)/bin/isort)
$(eval pytest       := $(venv)/bin/pytest)
$(eval twine        := $(venv)/bin/twine)
$(eval flake8       := $(venv)/bin/pflake8)
$(eval proselint    := $(venv)/bin/proselint)

setup-virtualenv:
	@test -e $(python) || python3 -m venv $(venv) || python -m venv $(venv)

format: setup-virtualenv
	$(pip) install --requirement=requirements-utils.txt
	$(black) .
	$(isort) .

lint: setup-virtualenv
	$(pip) install --requirement=requirements-utils.txt
	$(flake8) --exit-zero *.py
	$(MAKE) proselint

proselint:
	$(proselint) *.md || true

test: setup-virtualenv
	$(pip) install --editable=.[test]
	$(pytest)

publish: setup-virtualenv
	$(pip) install build twine
	$(python) -m build
	$(twine) upload --skip-existing --verbose dist/*{.tar.gz,.whl}
