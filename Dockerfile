# Use a lightweight Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container's /app directory
COPY . /app

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional, you can also use a .env file)
ENV TELEGRAM_API_ID=28920533
ENV TELEGRAM_API_HASH=93e710fb3c90ac39d16dd7f3d0cd52eb
ENV TELEGRAM_PHONE_NUMBER="+918459615960"
ENV N8N_WEBHOOK_URL="https://job-workflow-automation.onrender.com/webhook/79a8cb42-a99c-4d6e-858b-2ecd936b7ace"

# Set the default command to run your Python script
CMD ["python", "telethon_monitor.py"]
