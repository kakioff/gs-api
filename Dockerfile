FROM python:3.12-alpine

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD fastapi run --port 8000 ./src/main.py