FROM python:3.9.16-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.sh /main.sh
COPY main.py /main.py

ENTRYPOINT ["/main.sh"]
