# syntax=docker/dockerfile:1

FROM python:3.13-slim

# 1) install OS deps for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 2) set workdir
WORKDIR /app

# 3) copy only what we need to install dependencies
COPY requirements.txt . 

# 4) install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 5) copy the rest of the app
COPY app.py .  
COPY templates/ ./templates
COPY static/ ./static
COPY extract_frames.py full_pipeline.py  .  # if you have other scripts

# 6) expose the port Render will supply
EXPOSE 10000

# 7) run via Gunicorn (still using shell form so $PORT is expanded)
CMD gunicorn app:app --bind 0.0.0.0:$PORT