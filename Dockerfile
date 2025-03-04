FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app
# Add an unbuffered mode for logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
