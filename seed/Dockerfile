FROM python:3.10-slim

WORKDIR /app

COPY spells.json .
COPY seed.py .

RUN pip install pymongo

CMD ["python", "seed.py"]
