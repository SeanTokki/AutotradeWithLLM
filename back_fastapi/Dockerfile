FROM python:3.12

WORKDIR /app/back

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD python main.py