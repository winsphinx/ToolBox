FROM python:alpine

RUN python3 -m pip install -U --no-cache-dir pip pywebio IPy

WORKDIR /app

ADD *.py ./

CMD ["python3", "/app/home.py"]
