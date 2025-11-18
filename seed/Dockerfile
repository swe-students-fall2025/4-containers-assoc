FROM python:3.10-slim

WORKDIR /app

COPY seed/spells.json .
COPY seed/seed.py .

RUN pip install pymongo

CMD ["python", "seed.py"]
