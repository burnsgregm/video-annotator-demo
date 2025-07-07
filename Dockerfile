# syntax=docker/dockerfile:1

FROM python:3.13-slim

# 1) set workdir
WORKDIR /app

# 2) copy, install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) copy app code
COPY app.py .
COPY templates/ ./templates
COPY static/   ./static

# 4) expose the port Render will supply
EXPOSE 10000

# 5) run via Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]