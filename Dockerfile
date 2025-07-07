# syntax=docker/dockerfile:1

# 1) Base image
FROM python:3.13-slim

# 2) Set working directory
WORKDIR /app

# 3) Copy only requirements first (to leverage Docker layer caching)
COPY requirements.txt .

# 4) Copy application code and templates/static assets
COPY app.py .
COPY templates/ ./templates
COPY static/ ./static

# 5) Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy the rest of the project (e.g., frames/, uploads/)
COPY . .

# 7) Expose the port (Render will set PORT as an env var)
EXPOSE 10000

# 8) Launch via Gunicorn; using shell form for $PORT interpolation
CMD gunicorn app:app --bind 0.0.0.0:$PORT