FROM python:3.11

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

RUN pip install --upgrade pip 

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--app-dir", "src", "--workers", "4", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips=*", "--proxy-headers"]

