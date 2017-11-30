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
	soundboard

.PHONY: test
test:
	pylint --errors-only src/
