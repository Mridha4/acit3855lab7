FROM python:3.8-slim

LABEL maintainer="salmridha44@gmail.com"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "create_tables_mysql.py"]
CMD ["python", "app.py"]
