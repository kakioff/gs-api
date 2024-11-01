FROM python:3.12-alpine

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8000
CMD fastapi run --port 8000 ./src/main.py