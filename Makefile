
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

run:
	@echo " ============== Running the application ============== "
	cd src && uv run  python apod_fetcher.py

commit: lint type-check