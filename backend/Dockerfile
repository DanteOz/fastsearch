FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# COPY SOURCE
ADD . /code

# INSTALL DEPS
ENV UV_COMPILE_BYTECODE=1
WORKDIR /code
RUN uv sync --frozen --no-install-project --no-editable

# CACHE WEIGHTS
ENV HF_HOME="./models"
RUN mkdir ${HF_HOME}

ARG HF_TOKEN
ARG RETRIEVER_MODEL
ARG RANKING_MODEL
RUN uv run /code/scripts/cache_model.py 

RUN uv sync --frozen --no-editable

ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
CMD ["uv", "run", "uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "80"]