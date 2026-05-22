FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend/requirements /app/backend/requirements
RUN pip install --no-cache-dir -r /app/backend/requirements/prod.txt

COPY ml /app/ml
COPY backend /app/backend
COPY scripts /app/scripts

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app/backend

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
