# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.14
ARG POETRY_VERSION=2.2.1

FROM python:${PYTHON_VERSION}-slim AS builder

ARG POETRY_VERSION
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
	POETRY_NO_INTERACTION=1 \
	VIRTUAL_ENV=/opt/venv \
	PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip /usr/local/bin/python -m pip install "poetry==${POETRY_VERSION}"
RUN /usr/local/bin/python -m venv "$VIRTUAL_ENV"

WORKDIR /build

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
	poetry install --only main --no-root

COPY README.md ./
COPY src ./src
RUN poetry build --format wheel \
	&& python -m pip install --no-cache-dir --no-deps dist/*.whl \
	&& rm -f "$VIRTUAL_ENV"/bin/pip* \
	&& find "$VIRTUAL_ENV/lib" -type d -name pip -prune -exec rm -rf {} + \
	&& find "$VIRTUAL_ENV/lib" -type d -name 'pip-*.dist-info' -prune -exec rm -rf {} + \
	&& find "$VIRTUAL_ENV" -type d -name __pycache__ -prune -exec rm -rf {} +

FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.source="https://github.com/mbovo/pixiefairy" \
	  org.opencontainers.image.authors="Manuel Bovo" \
	  org.opencontainers.image.maintainers="Manuel Bovo" \
	  org.opencontainers.image.licenses="Apache-2.0" \
	  org.opencontainers.image.title="pixiefairy"

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	VIRTUAL_ENV=/opt/venv \
	PATH="/opt/venv/bin:$PATH"

RUN groupadd --gid 1000 user \
	&& useradd --no-log-init --uid 1000 --gid user --home-dir /app --no-create-home user \
	&& install -d -o user -g user /app/templates

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
USER 1000:1000
EXPOSE 5000
ENTRYPOINT ["pixiefairy"]
CMD ["start", "--help"]
