FROM python:3.13-slim-bookworm

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better caching)
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application source
COPY app/ ./

# Ensure static subdirs exist (they will be overmounted by volumes)
RUN mkdir -p static/input static/output

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
