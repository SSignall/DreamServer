# Dream Server — Developer Targets
# Run `make help` to see available commands.

SHELL_FILES := $(shell find . -name '*.sh' -not -path './node_modules/*' -not -path './.git/*' -not -path './data/*' -not -path './token-spy/*')

.PHONY: help lint test smoke simulate validate-ext gate doctor

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

lint: ## Syntax check all shell scripts + Python compile check
	@echo "=== Shell syntax ==="
	@fail=0; for f in $(SHELL_FILES); do bash -n "$$f" || fail=1; done; [ $$fail -eq 0 ]
	@echo "=== Python compile ==="
	@python3 -m py_compile ../extensions/services/dashboard-api/main.py ../extensions/services/dashboard-api/agent_monitor.py
	@echo "All lint checks passed."

test: ## Run unit and contract tests
	@echo "=== Tier map tests ==="
	@bash tests/test-tier-map.sh
	@echo ""
	@echo "=== Installer contracts ==="
	@bash tests/contracts/test-installer-contracts.sh
	@bash tests/contracts/test-preflight-fixtures.sh

smoke: ## Run platform smoke tests
	@echo "=== Smoke tests ==="
	@bash tests/smoke/linux-amd.sh
	@bash tests/smoke/linux-nvidia.sh
	@bash tests/smoke/wsl-logic.sh
	@bash tests/smoke/macos-dispatch.sh
	@echo "All smoke tests passed."

simulate: ## Run installer simulation harness
	@bash scripts/simulate-installers.sh

validate-ext: ## Validate all extension manifests and compose files
	@bash scripts/validate-extensions.sh

doctor: ## Run diagnostic report
	@bash scripts/dream-doctor.sh

gate: lint test smoke simulate validate-ext ## Full pre-release validation
	@echo ""
	@echo "Release gate passed."
