FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN chmod +x src/main.py
CMD sleep infinity
# ENTRYPOINT python -u src/main.py  # to be used when demonstrating basic reservation scenario