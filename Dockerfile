# syntax=docker/dockerfile:1

FROM python:3.10-bookworm

ARG MY_ENV

ENV MY_ENV=production \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1

# system deps
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# run project iniitialization
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /app

EXPOSE 7001

HEALTHCHECK CMD curl --fail http://localhost:7001/_stcore/health

# --browser.serverPort
# --browser.serverAddress
CMD ["poetry", "run", "streamlit", "--", "run", "/app/travel_map/app.py", "--browser.gatherUsageStats=false", "--server.port=7001", "--server.address=0.0.0.0", "--server.headless=true", "--client.showErrorDetails=true", "--logger.level=debug"]
