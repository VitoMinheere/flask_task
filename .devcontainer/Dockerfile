FROM python:3.11

COPY pyproject.toml ./

# install python poetry dependencies
RUN pip install --no-cache-dir poetry==1.3.2 \
    && poetry config virtualenvs.create false \
    && poetry install