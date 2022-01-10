.PHONY: clean help autoformat typecheck
.DEFAULT_GOAL := help

SHELL := /bin/bash


define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

clean: ## remove .pyc files.
	@find . -name "*.pyc" | xargs rm
	@find . -name "__pycache__" | xargs rm -r


help: ## List available Make commands
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


autoformat: ## Apply code formatting and sort imports.
	@black . --line-length=120
	@isort pathfinder

typecheck: ## Type-check with MyPy
	@mypy .
