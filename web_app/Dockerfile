# Use an official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy dependency files first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose port Flask will run on
EXPOSE 5000

# Specify how to run the app
CMD ["python", "app.py"]
