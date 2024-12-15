FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN chmod +x src/main.py
CMD sleep infinity
# CMD python -u src/main.py
