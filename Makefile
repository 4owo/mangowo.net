APP := poole

# =============================================================================

export LC_ALL := en_US.UTF-8

VIRTUALENV := virtualenv --python=python3

HERE:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.DEFAULT_GOAL := build

# =============================================================================
# clean up
# =============================================================================

.PHONY: clean
clean:
	rm *.pyc
	touch requirements.txt
	rm -f env/_done_*

.PHONY: distclean
distclean: clean
	rm -f bin
	rm -rf env

# =============================================================================
# build
# =============================================================================

env/bin/python:
	$(VIRTUALENV) env

env/_done_requirements: requirements.txt
	env/bin/pip install -U -r requirements.txt
	touch $@

bin:
	ln -s env/bin

.PHONY: env
env: env/bin/python bin
env: env/_done_requirements

define POOLE_BIN
#!/bin/bash

$(HERE)/env/bin/python $(HERE)/poole.py $$@
endef
export POOLE_BIN

poole: poole.py Makefile
	@echo "$$POOLE_BIN" > $@
	chmod +x poole

.PHONY: build
build: env poole

# =============================================================================
# tests
# =============================================================================

.PHONY: test
test: ## run the test suite
test: build
	cd tests && $(HERE)/env/bin/python run.py

