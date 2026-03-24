FROM python:3.9-slim

# Set up the working directory inside the container
WORKDIR /app

# Demucs and torchaudio require ffmpeg, libsndfile1, and sox for backend processing
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 sox libsox-fmt-all && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our application
COPY . .

# Hugging Face Spaces expects the app to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Prevent permissions issues downloading PyTorch AI models in HF
ENV TORCH_HOME=/app/cache
ENV HF_HOME=/app/cache

# Create required directories and make them writable for the non-root user
RUN mkdir -p uploads separated cache && chmod -R 777 uploads separated cache

# Command to run our Flask app
CMD ["python", "app.py"]

# Force Docker Rebuild 1
