FROM python:3.11

RUN mkdir /rabbitmq_consumer

WORKDIR /rabbitmq_consumer

RUN pip install --upgrade pip 

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "rabbitmq_consumer.py"]



