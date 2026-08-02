FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir prometheus_client
COPY ufw_exporter.py .
EXPOSE 9092
CMD ["python", "ufw_exporter.py"]
