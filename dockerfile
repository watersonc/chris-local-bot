FROM python:3.9
FROM disnakeDev/disnake

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY . .

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]