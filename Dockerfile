# syntax=docker/dockerfile:1

FROM python:3.13-slim

# 1) system deps for OpenCV
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# 2) set workdir
WORKDIR /app

# 3) copy only what we need for install
COPY requirements.txt . 

# 4) install deps
RUN pip install --no-cache-dir -r requirements.txt

# 5) copy code
COPY . .

# 6) expose the port Render will supply
EXPOSE 10000

# 7) start with extended timeout
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "600"]