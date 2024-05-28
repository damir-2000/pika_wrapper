VENV_PATH = venv
VENV = ./venv/Scripts/
CODE = ./pika_wrapper

setup-dev: create-venv pip-update

create-venv:
	python -m venv ${VENV_PATH}

pip-install-dev:
	${VENV}pip install --upgrade pip pip-tools
	${VENV}pip-sync requirements.txt requirements-dev.txt

pip-install:
	${VENV}pip install --upgrade pip pip-tools
	${VENV}pip-sync requirements.txt

pip-update:
	${VENV}python -m pip install --upgrade pip pip-tools
	${VENV}pip-compile requirements.in
	${VENV}pip-compile requirements-dev.in
	${VENV}pip-sync requirements.txt requirements-dev.txt

lint:
	${VENV}flake8 ${CODE} --exit-zero --per-file-ignores="__init__.py:F401" --max-line-length 90
	${VENV}pylint ${CODE} --ignore=migrations/{0000..1000}_something --disable=C0116 --disable=C0111 --disable=C0114 --exit-zero
	${VENV}mypy ${CODE} 

black:
	${VENV}black ${CODE}

cleanimports:
	${VENV}isort ${CODE}
	
autoflake:
	${VENV}autoflake -r -i --remove-all-unused-imports --ignore-init-module-imports ${CODE}

clean-lint: autoflake cleanimports black lint