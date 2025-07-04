FROM python:3.10

# Cài đặt các gói hệ thống cần thiết (thêm libsqlite3-dev)
RUN apt-get update && apt-get install -y gcc libpq-dev libsqlite3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]