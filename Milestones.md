# Milestones.md

## Project Development Checklist

| # | Milestone | Deliverables | Testable Acceptance |
|---|-----------|--------------|---------------------|
| 1 | **Project setup & folder structure** | Folder hierarchy, `requirements.txt`, `.gitignore`, `.env.example`, `README.md` | `tree` shows expected layout |
| 2 | **Synthetic data generation & validation** | `src/data_generator.py`, generated CSV in `data/raw/` | Running `python src/data_generator.py` creates a CSV with ≥10k rows and valid columns |
| 3 | **Data cleaning & EDA** | `src/data_processing.py` (load/clean utilities), `notebooks/01_exploratory_data_analysis.ipynb` with basic analysis & plots | Notebook opens without error, shows summary statistics and at least one plot |
| 4 | **Feature engineering pipeline** | `src/feature_engineering.py` using `sklearn` `Pipeline` & `ColumnTransformer` | Unit test verifies `fit_transform` returns a NumPy array without target leakage |
| 5 | **Baseline ML models** | `src/train_model.py`, `src/predict.py`, `src/model_evaluation.py`, saved model in `models/` | Model file exists, `predict` returns probability in `[0,1]` |
| 6 | **Intelligent decision engine** | `src/decision_engine.py`, `src/retry_strategy.py`, `src/revenue_calculator.py` | Unit tests confirm permanent failures are not auto‑retried and net‑benefit selection works |
| 7 | **Backend API (FastAPI)** | `api/main.py`, `api/schemas.py`, `api/routes/` (transactions, predictions, retries) | `uvicorn api.main:app` launches, Swagger UI reachable, basic endpoints return 200 |
| 8 | **Database integration** | SQLAlchemy models, Alembic migrations, PostgreSQL connection | `alembic upgrade head` runs, tables created, CRUD works |
| 9 | **Frontend dashboard (React)** | Vite+TS project with pages, components, API service layer | `npm run dev` shows a functional UI with placeholder data |
|10| **Explainability (SHAP)** | `src/model_explainability.py`, notebook visualisations | SHAP summary plot generated for a sample record |
|11| **Retry simulation & tracking** | Simulation endpoint, audit logs | Simulated retry updates DB correctly |
|12| **Testing & QA** | Pytest suite covering ML, decision, API, frontend | `pytest -q` passes all tests |
|13| **Security hardening** | env var handling, input validation, rate limiting | Security tests pass, no secrets in repo |
|14| **Docker & deployment** | `Dockerfile`, `docker-compose.yml`, CI scripts | `docker compose up` launches all services, app reachable |
|15| **Final documentation** | Complete README, LICENSE, CONTRIBUTING, API docs | README renders correctly on GitHub, all links work |

Each milestone is **independently testable** and will be demonstrated before proceeding to the next.
