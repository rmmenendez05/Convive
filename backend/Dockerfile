FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_URL=sqlite:////data/convive.db

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Usuario sin privilegios; /data es el volumen de la base de datos.
RUN useradd --create-home --uid 1000 convive \
    && mkdir -p /data \
    && chown -R convive:convive /data /app
USER convive

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
