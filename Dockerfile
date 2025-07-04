FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the script and session file
COPY . .

EXPOSE 10000

# Run the script
CMD ["python","-u","app.py"]
