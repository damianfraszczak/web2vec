FROM python:3.10-slim

WORKDIR /app

COPY generate_dataset.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "generate_dataset.py"]
