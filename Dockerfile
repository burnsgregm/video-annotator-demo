# syntax=docker/dockerfile:1

FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ ./templates
COPY static/ ./static
COPY extract_frames.py full_pipeline.py .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]