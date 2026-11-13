PYTHON ?= python3
ARGS ?=

.PHONY: init install dev pdf test

init:
	$(PYTHON) scripts/setup/manage.py init $(ARGS)

install:
	$(PYTHON) scripts/setup/manage.py install $(ARGS)

dev:
	$(PYTHON) scripts/setup/manage.py dev -- $(ARGS)

pdf:
	$(PYTHON) scripts/setup/manage.py dev -- "$(INPUT)" "$(OUTPUT)"

test:
	$(PYTHON) scripts/setup/manage.py test
