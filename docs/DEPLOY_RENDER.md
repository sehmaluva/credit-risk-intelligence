# Deploy to Render

## 1. PostgreSQL

Create a **PostgreSQL** instance on Render. Copy the **Internal Database URL** as `DATABASE_URL`.

## 2. Redis

Create a **Redis** instance. Copy the connection URL as `REDIS_URL`.

## 3. Web Service (Django API)

- **Build Command**: `pip install -r backend/requirements/prod.txt && cd ml && python train.py --fast && cd ../backend && python manage.py collectstatic --noinput`
- **Start Command**: `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- **Release Command**: `cd backend && python manage.py migrate && python /opt/render/project/src/scripts/seed_demo.py --if-empty`

### Environment variables

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Random secure string |
| `DEBUG` | `False` |
| `DATABASE_URL` | From Render Postgres |
| `REDIS_URL` | From Render Redis |
| `ALLOWED_HOSTS` | `your-api.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `frontend url` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `ML_ARTIFACTS_PATH` | `/opt/render/project/src/ml/artifacts` |

## 4. Background Worker (Celery)

Duplicate the web service as a **Background Worker**:

- **Start Command**: `cd backend && celery -A config worker -l info`
- Same env vars as the web service

## 5. Static Site (React Frontend)

- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist`
- **Environment**: `VITE_API_URL=https://frontend_address/api/v1`

## 6. ML Artifacts

Train locally and commit artifacts, or run `python ml/train.py` in the build step (as above). Ensure `ml/artifacts/` contains:

- `calibrated_model.pkl`
- `model.pkl`
- `shap_background.pkl`
- `feature_manifest.json`

## 7. HTTPS

Render provides TLS automatically. Django uses `SECURE_PROXY_SSL_HEADER` in prod settings.
