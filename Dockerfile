FROM python:3.9-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --deploy --system

COPY . .

CMD ["python", "dataplayer-api.py"]
