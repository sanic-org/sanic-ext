pretty:
	black --line-length 79 --target-version=py39 sanic_ext tests
	isort --line-length 79 --trailing-comma -m 3 sanic_ext tests
