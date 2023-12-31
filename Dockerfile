FROM python:alpine

WORKDIR /app

COPY src/ ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7086

ENTRYPOINT ["python3", "./index.py"]
