FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tha \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app
# Add an unbuffered mode for logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
