FROM python:3.10

RUN apt-get update && apt-get install -y chromium chromium-driver

WORKDIR /app
COPY . /app

RUN pip install -r Requirements.txt

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
