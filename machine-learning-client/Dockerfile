FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app

# Copy ONLY the contents of the web_app folder into the container
COPY machine-learning-client/requirements.txt ./requirements.txt

# Install the web app dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY machine-learning-client/ .

EXPOSE 8000

CMD ["uvicorn", "convert:app", "--host", "0.0.0.0", "--port", "8000"]