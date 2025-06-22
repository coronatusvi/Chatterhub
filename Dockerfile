FROM python:3.10

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Tạo thư mục app và copy code vào container
WORKDIR /app
COPY . /app

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose port (sửa lại nếu app chạy port khác)
EXPOSE 8000

# Chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]