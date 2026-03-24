FROM python:3.9-slim

# Set up the working directory inside the container
WORKDIR /app

# Demucs requires ffmpeg for processing audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our application
COPY . .

# Hugging Face Spaces expects the app to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Create upload and separated directories and make them writable
RUN mkdir -p uploads separated && chmod -R 777 uploads separated

# Command to run our Flask app
CMD ["python", "app.py"]
