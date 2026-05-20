# AI Credit Risk Intelligence Platform

Production-grade credit risk assessment platform for emerging-market lenders. Predicts loan default probability with **LightGBM**, explains decisions with **SHAP**, and supports full loan officer workflows.

## Features

- JWT authentication with RBAC (Admin, Risk Manager, Loan Officer)
- Loan application workflow (draft → submit → score)
- Real-time LightGBM inference with SHAP explainability
- Actionable recommendations (approve, reject, guarantor, etc.)
- Portfolio analytics dashboards
- Audit logging and async CSV reports (Celery)
- Docker Compose for local dev; Render deployment guide

## Quick Start (Docker)

```bash
cd credit-risk-intelligence
cp .env.example .env.docker

# Train model (first time)
pip install -r backend/requirements/base.txt
python ml/train.py --fast

docker compose up --build
```

Open **http://localhost:8080**

### Demo credentials

| Role | Email | Password |
|------|-------|----------|
| Loan Officer | officer@creditrisk.io | officer123 |
| Risk Manager | risk@creditrisk.io | risk123 |
| Admin | admin@creditrisk.io | admin123 |

## Demo workflow

1. Login as loan officer
2. Dashboard → review portfolio KPIs
3. **New Application** → fill borrower/loan data → Create
4. **Submit** → **Run Risk Score**
5. **Risk Assessment** → probability, SHAP chart, recommendation
6. Login as risk manager → Analytics + Audit logs

## Project structure

```
credit-risk-intelligence/
├── ml/                 # Training, features, SHAP, recommendations
├── backend/            # Django REST API
├── frontend/           # React + Vite + Tailwind
├── nginx/              # Reverse proxy
├── scripts/            # Seed data, train helper
└── docs/DEPLOY_RENDER.md
```

## API

- Swagger: `http://localhost:8000/api/docs/`
- Health: `http://localhost:8000/api/health/`

## Train model

```bash
python ml/train.py          # Full training
python ml/train.py --fast   # CI / quick iteration
```

Artifacts: `ml/artifacts/` (`calibrated_model.pkl`, `feature_manifest.json`, `shap_background.pkl`)

## Development without Docker

```bash
# Backend
cd backend
pip install -r requirements/dev.txt
export DATABASE_URL=postgresql://creditrisk:creditrisk@localhost:5433/creditrisk
export PYTHONPATH=..
python manage.py migrate
python ../scripts/seed_demo.py
python manage.py runserver

# Frontend
cd frontend && npm install && npm run dev
```

## License

MIT — Built for financial inclusion and responsible AI in emerging markets.
