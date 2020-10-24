FROM python:3.6-alpine

ADD ./database.py /
ADD ./queries.py /

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN python -m pip install --upgrade pip
RUN pip3 install psycopg2-binary

ENV DATABASE_HOSTNAME=localhost
ENV DATABASE_PORT=5432
ENV DATABASE_NAME=postgres
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=postgres

CMD [ "python3", "./queries.py" ]