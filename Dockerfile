# Two separate environments, because experiments/requirements.txt and
# requirements_artifacts.txt pin different NumPy versions.
#   docker compose build
#   docker compose run --rm experiments python run_experiments.py --output results_group --repeats 5
#   docker compose run --rm publish python build_report_docx.py

FROM python:3.12-slim-bookworm AS experiments
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
COPY experiments/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
WORKDIR /work/experiments

FROM python:3.12-slim-bookworm AS publish
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      pandoc libreoffice-writer poppler-utils fonts-liberation fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*
COPY requirements_artifacts.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
WORKDIR /work
