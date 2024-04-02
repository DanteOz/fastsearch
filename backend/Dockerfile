FROM python:3.10-slim-buster
WORKDIR /code

# INSTALL PYTHON REQUIREMENTS
COPY ./requirements.lock .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.lock

# CACHE WEIGHTS
ENV TRANSFORMERS_CACHE="./models"
RUN mkdir ${TRANSFORMERS_CACHE}

ARG HF_TOKEN
ARG RETRIEVER_MODEL
ARG RANKING_MODEL
COPY cache_model.py .
RUN python /code/cache_model.py

# COPY SOURCE
COPY . .

ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]