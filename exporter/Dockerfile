FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
USER 10001
EXPOSE 9108
CMD ["python", "main.py"]
