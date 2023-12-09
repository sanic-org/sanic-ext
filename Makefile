PYTEST = pytest -rs sanic_ext tests -vv --cache-clear --flake8

.PHONY: test
test:
	${PYTEST}

.PHONY: test-cov
test-cov:
	${PYTEST} --cov sanic_ext

.PHONY: fix
fix:
	ruff check sanic_ext --fix

.PHONY: format
format:
	ruff format sanic_ext

.PHONY: pretty
pretty: fix format
