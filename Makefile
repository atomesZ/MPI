RED=\e[91m
GREEN=\e[92m
NC=\e[0m


.PHONY: all install_requirements check check_testsuite clean test

# Simple execuction of the main
all: clean install_requirements
	python3 main.py

# Install python dependencies
install_requirements:
	pip3 install -r requirements.txt

# Run the testsuite after the main to assert everything works well
check: clean all
	@echo ""
	python3 testsuite.py

# Same as 'check' but after we check that the testsuite works by inserting a wrong element to make it fails
check_testsuite: clean all
	@if ! python3 testsuite.py; then echo "\nTestsuite is already failing before we try to make it fail\n==> TEST OF THE TESTSUITE: ${RED}KO${NC}" && exit 1; fi
	@echo ""
	touch log_server_0.txt
	@python3 testsuite.py || echo "\n==> TEST OF THE TESTSUITE: ${GREEN}OK${NC}"

# Run the testsuite
test:
	python3 testsuite.py

# Debug
debug: clean install_requirements
	python3 main.py debug

# Testsuite & Debug
check_debug: debug
	@echo ""
	python3 testsuite.py

# Remove all generated elements by the main
clean:
	@rm -rf logs_server clients_input perfs 2> /dev/null || true
