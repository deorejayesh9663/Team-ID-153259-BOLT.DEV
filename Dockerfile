FROM python:3.12-slim

WORKDIR /app

# Install zenoh for the ping script
RUN pip install eclipse-zenoh

COPY . /app/

CMD ["python", "vyuha/samvaad/ping.py"]
