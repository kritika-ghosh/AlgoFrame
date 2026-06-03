# Use official Python lightweight slim image
FROM python:3.10-slim

# Install system media dependencies required by Manim, Cairo, and FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    freeglut3-dev \
    pkg-config \
    fontconfig \
    fonts-freefont-ttf \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Establish working directory inside container
WORKDIR /code

# Copy and install Python requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy backend files into the container
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
