FROM python:3.10-slim

WORKDIR /app

# Copy ONLY the contents of the web_app folder into the container
COPY . /app

# Install the web app dependencies
RUN pip install --no-cache-dir -r web_app/requirements.txt

EXPOSE 5001

CMD ["python", "web_app/app.py"]

