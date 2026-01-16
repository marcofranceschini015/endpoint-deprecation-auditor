FROM python:3.9

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/

CMD ["tail", "-f", "/dev/null"]

