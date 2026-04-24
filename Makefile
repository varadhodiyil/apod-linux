
fixup:
	@echo " ============== Running linter auto fix ============== "
	uv run  ruff check --fix .
	uv run  ruff format .

lint:
	@echo " ============== Running linter ============== "
	uv run  ruff check .
	uv run  ruff format --check .
	
type-check:
	@echo " ============== Running type checker ============== "
	uv run  ty check .
