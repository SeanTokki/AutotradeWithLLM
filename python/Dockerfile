FROM python:3.12-alpine

WORKDIR /app/python

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install

COPY . .

WORKDIR /back_fastapi

CMD python main.py