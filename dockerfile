FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install disnake

COPY . /app

CMD [ "python", "main.py" ]