set shell := ["bash", "-euo", "pipefail", "-c"]

image_name := env_var_or_default("IMAGE_NAME", "mbovo/pixiefairy")

# List available recipes
default:
    @just --list

# Run all pre-commit hooks
check:
    poetry run pre-commit run --all-files

# Bootstrap the development environment
setup:
    @python3 -c 'import sys; sys.exit("Required Python version not found (3.14)") if sys.version_info[:2] != (3, 14) else None'
    poetry install
    poetry run pre-commit install

# Run tests and coverage
test:
    poetry run pytest --cov=pixiefairy --cov-branch --cov-report=term-missing --cov-fail-under=90 .

# Build the Python package
build:
    poetry build

# Build and publish the Python package
publish: build
    poetry publish --username "$PYPI_USERNAME" --password "$PYPI_TOKEN"

# Remove build artifacts
clean:
    rm -rf dist

# Remove build artifacts and the local virtual environment
reset: clean
    rm -rf .venv

# Build the local Docker image
docker-build:
    docker build -t {{ image_name }}:local -f containers/Dockerfile .

# Remove the local Docker image
docker-clean:
    docker rmi -f {{ image_name }}:local
