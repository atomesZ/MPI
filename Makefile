RED=\e[91m
GREEN=\e[92m
NC=\e[0m


.PHONY: all install_requirements check check_testsuite clean

all: #install_requirements
	python3 choose_server_client.py

install_requirements:
	pip3 install -r requirements.txt


check: clean all
	@echo ""
	python3 testsuite.py

check_testsuite: clean all
	@if ! python3 testsuite.py; then echo "\nTestsuite is already failing before we try to make it fail\n==> TEST OF THE TESTSUITE: ${RED}KO${NC}" && exit 1; fi
	@echo ""
	touch log_server_0.txt
	@python3 testsuite.py || echo "\n==> TEST OF THE TESTSUITE: ${GREEN}OK${NC}"

clean:
	@rm log_server_*.txt 2> /dev/null || true
