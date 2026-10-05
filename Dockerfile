# Backend image for Railway / Cloud Run. Lives at the repo root so the
# platform can deploy the monorepo without a Root Directory setting.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

# Railway injects $PORT; default to 8000 for local `docker run`.
# Migrate and bootstrap the first admin on every start (both idempotent),
# so the schema never depends on the platform's pre-deploy hook running.
# --proxy-headers: trust Railway's edge for the real scheme and client IP.
CMD ["sh", "-c", "alembic upgrade head && python -m scripts.bootstrap_admin && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips '*'"]
