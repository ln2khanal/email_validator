
FROM python:3.11-slim

# ENVs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends apt-transport-https ca-certificates build-essential netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=email_validator_local.settings
ENV PORT=8000

COPY docker/validator_entrypoint.sh /app/docker/validator_entrypoint.sh
RUN chmod +x /app/docker/validator_entrypoint.sh

RUN useradd -m appuser
USER appuser

EXPOSE ${PORT}

CMD ["/app/docker/validator_entrypoint.sh"]

