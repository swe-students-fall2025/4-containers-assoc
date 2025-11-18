FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean

# Copy ONLY the contents of the web_app folder into the container
COPY web_app/requirements.txt ./requirements.txt
# Install the web app dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app/ .

EXPOSE 5001

CMD ["python", "app.py"]

