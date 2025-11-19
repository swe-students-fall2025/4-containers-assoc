![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg) [![Web App CI](https://github.com/swe-students-fall2025/4-containers-assoc/actions/workflows/ci.yml/badge.svg)](https://github.com/swe-students-fall2025/4-containers-assoc/actions/workflows/ci.yml) [![ML-tests CI](https://github.com/swe-students-fall2025/4-containers-assoc/actions/workflows/ci-ml.yml/badge.svg)](https://github.com/swe-students-fall2025/4-containers-assoc/actions/workflows/ci-ml.yml)

# Holingo - Harry Potter Spell Pronunciation System

This project is a multi-container application that displays Harry Potter spells in a web interface and allows users to assess their spell pronunciation using Azure Cognitive Services.


## Configuration

This project uses a .env file for database and Azure configuration.
An example file is provided as env.example with dummy values. The actual env file values will be sent to graders directly.

## How to Run

From the root directory run 
```bash
docker compose up --build
```
This will:
    - start a local MongoDB container
    - automatically load spell data from seed/spells.json
    - start up the Flask web app
No manual database setup is required — the seed container inserts data on startup.

## Development

```bash
# Navigate to the project folder
cd web_app

# Install dependencies
pipenv install --dev

# Format all Python code
pipenv run black .

# Lint all Python files
pipenv run pylint **/*.py

# Run Flask tests with coverage
pipenv run pytest flaskTests.py \
            --cov=app \
            --cov=models \
            --cov-fail-under=80


```

```bash
# Navigate to the project folder
cd machine_learning_client

# Install dependencies using Pipenv
pipenv install --dev

# Format all Python code with Black
pipenv run black .

# Lint all Python files with Pylint
pipenv run pylint **/*.py

# Run tests with coverage
pipenv run pytest machine_learning_client/tests \
            --cov=machine_learning_client \
            --cov-report=term-missing \
            --cov-fail-under=80 \
            --import-mode=importlib
```

## Team Assoc

| Name | GitHub |
|------|--------|
| Sean Tang | [@plant445](https://github.com/plant445) |
| Morin Zhou | [@Morinzzz](https://github.com/Morinzzz) |
| May Zhou | [@zz4206](https://github.com/zz4206) |
| Howard Appel | [@hna2019](https://github.com/hna2019) |
| Leo Fu | [@LeoFYH](https://github.com/LeoFYH) |


