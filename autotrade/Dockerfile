FROM python:3.12

WORKDIR /app/program

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install

COPY . .

CMD python autotrade.py