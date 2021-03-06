FROM python:3.8-slim

ADD ./database.py /
ADD ./queries.py /

RUN python -m pip install --upgrade pip
RUN pip3 install psycopg2-binary

ENV DATABASE_HOSTNAME=db
ENV DATABASE_PORT=5432
ENV DATABASE_NAME=postgres
ENV DATABASE_USER=postgres
ENV DATABASE_PASSWORD=postgres

CMD [ "python3", "./queries.py" ]