# Docker version for the Python version included in macOS developer tools
FROM python:3.9.16-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY main.sh /main.sh
COPY main.py /main.py

ENTRYPOINT ["/main.sh"]