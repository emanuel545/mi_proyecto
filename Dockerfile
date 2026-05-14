FROM python:3.12-slim AS builder

WORKDIR /app

ENV POETRY_REQUESTS_TIMEOUT=300
ENV PIP_DEFAULT_TIMEOUT=300

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY src ./src

FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src ./src

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "mi_proyecto.api_lab:app", "--host", "0.0.0.0", "--port", "8000"]