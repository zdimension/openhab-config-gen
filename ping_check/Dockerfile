# Dockerfile that launches the ping_check.py file

FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY ping_check/ping_check_runner.py .

RUN pip install --no-cache-dir multiping requests

CMD ["python", "./ping_check_runner.py"]