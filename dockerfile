FROM python:3.9

WORKDIR .

RUN cd chris-local-bot

CMD ["python", "main.py"]
