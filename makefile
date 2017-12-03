.PHONY: install
install:
	pip install .

.PHONY: uninstall
uninstall:
	pip uninstall -y soundboard

.PHONY: reinstall
reinstall: uninstall install

.PHONY: run
run:
	soundboard --config-file ./example-config.yml

.PHONY: test
test:
	pylint --errors-only src/
