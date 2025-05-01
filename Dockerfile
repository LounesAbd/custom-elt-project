FROM python:3.12-slim

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY elt_script/elt_script.py .

CMD ["python", "elt_script.py"]