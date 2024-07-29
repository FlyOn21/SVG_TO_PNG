# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install system dependencies
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

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
RUN mkdir results
COPY Json.txt .
COPY svg_to_png_v3.py .

# Specify the command to run on container start
CMD ["python3", "svg_to_png_v3.py"]
