FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y \
    gcc \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    python3-dev \
    build-essential \
    libglib2.0-dev \
    libpixman-1-dev \
    libpng-dev \
    libfreetype6-dev \
    librsvg2-dev \
    gir1.2-rsvg-2.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir results
COPY Json.txt .
COPY svg_to_png_v3.py .
COPY svg_to_png_v1.py .

CMD ["python3", "svg_to_png_v3.py"]
