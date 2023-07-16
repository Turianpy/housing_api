FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH .

CMD ["gunicorn", "housing_api.wsgi:application", "--bind", "0:8000", "--workers", "3", "--reload"]

EXPOSE 8000