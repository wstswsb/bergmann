lint:
	ruff check --fix
	ruff format
	pyright .
