FROM python:3.9

WORKDIR .

RUN pip install disnake

CMD ["python", "main.py"]
