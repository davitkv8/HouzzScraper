FROM python:3.11.5

WORKDIR /app

COPY requirements.txt .

RUN echo "Listing /app contents:" && ls -l /app && cat /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . .
