FROM python:3.12

WORKDIR /app/python

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps

COPY . .

EXPOSE 8080
ENV TZ Asia/Seoul

CMD ["python", "main.py"]