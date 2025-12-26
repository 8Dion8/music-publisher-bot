# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables (will be overridden by docker run)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]