# syntax=docker/dockerfile:1

FROM python:3.13-slim

# 1) set workdir
WORKDIR /app

# 2) copy only what we need
COPY requirements.txt .
COPY app.py .
COPY templates/ ./templates
COPY static/ ./static

# 3) install deps
RUN pip install --no-cache-dir -r requirements.txt

# 4) copy the rest (frames/, uploads/, etc. can stay empty in source)
COPY . .

# 5) expose the port env Render will supply
EXPOSE 10000

# 6) run via Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]