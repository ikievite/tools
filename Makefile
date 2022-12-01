lint:
	poetry run isort tools/
	poetry run flake8 tools/

make black:
	poetry run black tools/

install:
	poetry install

build:
	poetry build

package-install:
	python3 -m pip install --user dist/*.whl

test:
	poetry run pytest --cov=tools --cov-report xml tests/

mypy:
	poetry run mypy --strict tools/
