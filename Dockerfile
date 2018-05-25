FROM python:3

WORKDIR /maestro

COPY requirements.txt ./

RUN apt-get update && apt-get install --no-install-recommends --yes libldap2-dev libsasl2-dev libssl-dev && pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "-u", "main.py" ]
