# Instalar dependencias
poetry install

# Ejecutar herramientas de calidad
poetry run ruff check .
poetry run black .
poetry run isort .

# Ejecutar pre-commit
poetry run pre-commit run --all-files
