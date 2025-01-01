FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app:app