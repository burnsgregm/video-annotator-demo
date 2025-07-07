# syntax=docker/dockerfile:1

FROM python:3.13-slim

# install libGL for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ ./templates
COPY static/ ./static

EXPOSE 10000

# use shell form so $PORT is expanded at container start
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]