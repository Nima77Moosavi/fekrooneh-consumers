# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /code

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your consumer folder
COPY leaderboard /code/leaderboard

# Default command to run the consumer
CMD ["python", "leaderboard/leaderboard_consumer.py"]
