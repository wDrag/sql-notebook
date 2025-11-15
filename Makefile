.PHONY: dev
.PHONY: install
.PHONY: init

dev:
	bash scripts/setup/dev.sh

install:
	bash scripts/setup/install.sh $(filter-out $@,$(MAKECMDGOALS))

init:
	bash scripts/setup/init.sh
	make install

PY=./python_modules/bin/python

.PHONY: pdf
pdf:
	bash scripts/utilities/export_notebook.sh $(filter-out $@,$(MAKECMDGOALS))


%:
	@:
