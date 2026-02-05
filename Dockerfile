# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir \
  ruff==0.6.9 \
  mypy==1.11.2 \
  pytest==8.3.3 \
  requests \
  streamlit

CMD ["bash"]
