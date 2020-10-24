import os
from csv import DictReader
import pandas as pd
import logging
import datetime
import math
import concurrent.futures
import sys
import psycopg2
import queue
import threading
import time

from database import Database
from exceptions import *
import utils
import query_provider as queries

class Etl:

    _dataset_path = 'data-sample-big2.csv'
    _batch_size = 100
    _thread_amount = 32

    def __init__(self):
        hostname = os.environ['DATABASE_HOSTNAME']
        port = os.environ['DATABASE_PORT']
        database_name = os.environ['DATABASE_DB']
        username = os.environ['DATABASE_USER']
        password = os.environ['DATABASE_PASSWORD']

        self._dataset_url = 'https://query.data.world/s/w7po2qr36r6fw27tjsah535qezantj' #os.environ['DATASET_URL']
        self._db = Database(hostname, port, database_name, username, password, self._thread_amount * 4)
        self._tags = {}
        self._products = {}
        self._issues = {}
        self._companies = {}
        self._states = {}
        self._queue = queue.Queue()
        self._df_len = 0
        self._start = None

    def start(self):
        logging.info('Loading data...')
        df = utils.benchmark('Data successfuly loaded in {}', self.__load)

        self._start = datetime.datetime.now()
        reporter = threading.Thread(target=self.__report_progress)
        reporter.start()

        self.__transform(df)

        reporter.join()
        self._db.close()
        exit(0)

    def __load(self):
        return pd.read_csv(self._dataset_url)

    def __transform(self, df):
        current = 0
        self._df_len = len(df)  

        df = df.where(pd.notnull(df), None)
        with concurrent.futures.ThreadPoolExecutor(max_workers = self._thread_amount) as executor:
            futures = []

            while(current < self._df_len):
                top = current + self._batch_size
                
                if(top > self._df_len):
                    top = self._df_len

                df_part = df.iloc[current:top]
                futures.append(executor.submit(self.__transform_df, df=df_part))
                current = top
            
    def __report_progress(self):
        percentage = 0.0
        processed_rows = 0
        avg_elapsed = 0.0

        logging.info('Transforming data...')
        sys.stdout.write('\r0% completed (estimated: ?)')
        sys.stdout.flush()

        while(percentage != 100):
            if(not self._queue.empty()):
                elasped = self._queue.get()
                try:
                    processed_rows += self._batch_size

                    if(avg_elapsed == 0):
                        avg_elapsed = elasped.total_seconds()
                    else:
                        avg_elapsed = (avg_elapsed + elasped.total_seconds()) / 2

                    estimation = ((self._df_len - processed_rows) * avg_elapsed / self._batch_size) / self._thread_amount
                    percentage = processed_rows / self._df_len * 100

                    if(percentage > 100):
                        percentage = 100

                    formatted_estimation = utils.hhmmssms_from_ms(estimation * 1000)

                    if(percentage != 100):
                        sys.stdout.write('\r{:.2f}%% completed (remaining: {}).'.format(percentage, formatted_estimation))
                    else:
                        total_elapsed = datetime.datetime.now() - self._start
                        formatted_total_elapsed = utils.hhmmssms_from_ms(total_elapsed.total_seconds() * 1000)
                        sys.stdout.write('\r100%% completed in {}.\r\n'.format(formatted_total_elapsed))
                        sys.stdout.flush()

                    sys.stdout.flush()
                except Exception as e:
                    raise Exception('Something went wrong') from e
            else:
                time.sleep(1)

    def __transform_df(self, df):
        start = datetime.datetime.now()
        df.apply(lambda row: self.__transform_row(row), axis = 1)
        end = datetime.datetime.now()
        return self._queue.put(end - start)
        
    def __transform_row(self, row):
        product = self.__get_product(row['Product'], row['Sub-product'])
        issue = self.__get_issue(row['Issue'], row['Sub-issue'])
        company = self.__get_company(row['Company'])
        state = self.__get_state(row['State'])
        date_received = datetime.datetime.strptime(row['Date received'], '%m/%d/%Y')
        date_sent = datetime.datetime.strptime(row['Date sent to company'], '%m/%d/%Y')
        consumer_consent = utils.parse_boolean(row['Consumer consent provided?'])
        timely_response = utils.parse_boolean(row['Timely response?'])
        consumer_disputed = utils.parse_boolean(row['Consumer disputed?'])
        complaint_id = row['Complaint ID']
        state_id = None

        if (state):
            state_id = state[0]

        if(product is None or issue is None or company is None):
            pass

        with self._db as conn:
            with conn.cursor() as cursor:
                self._db.execute(cursor, 'INSERT INTO complaints(id, reception_date, product_id, issue_id, company_id, state_id, zip_code, consumer_narrative, '
                    'company_public_response, company_consumer_response, consumer_consent, submission_channel, company_sent_date, timely_response, '
                    'consumer_disputed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', [complaint_id, date_received, product[0],
                    issue[0], company[0], state_id, row['ZIP code'], row['Consumer complaint narrative'], row['Company public response'],
                    row['Company response to consumer'], consumer_consent, row['Submitted via'], date_sent, timely_response, consumer_disputed])

                if(not self._db.has_results(cursor)):
                    raise ComplaintNotInsertedException(complaint_id)

                self.__add_tags(cursor, complaint_id, row['Tags'])
                conn.commit()

    def __add_tags(self, cursor, complaint_id, tags_str):
        tags = str(tags_str).split(",")

        if(len(tags) > 0):
            for tag_str in tags:
                if(tag_str != 'None'):
                    tag = self.__get_tag(tag_str.upper())
                    tag_id = tag[0]

                    self._db.execute(cursor, 'INSERT INTO complaint_tags (complaint_id, tag_id) VALUES (%s, %s)', [complaint_id, tag_id])

                    if(not self._db.has_results(cursor)):
                        raise ComplaintTagNotInsertedException(complaint_id, tag_id)

    def __get_tag(self, tag):
        result = None
        tag = utils.upper(tag)

        if(tag in self._tags):
            return self._tags[tag]

        try:
            with self._db as conn:
                with conn.cursor() as cursor:
                    query = queries.get_tag_query(tag)

                    self._db.execute(cursor, query['query'], query['params'])

                    if(not self._db.has_results(cursor)):
                        try:
                            self._db.execute(cursor, 'INSERT INTO tags (name) VALUES (%s)', [tag])
                            if(not self._db.has_results(cursor)):
                                raise TagNotInsertedException(tag)
                        except psycopg2.IntegrityError:
                            conn.rollback()
                            logging.debug('the tag (name: \'{}\') was added by other thread'.format(tag))

                        self._db.execute(cursor, query['query'], query['params'])
                    
                    result = self._db.fetch(cursor)

        except Exception as e:
            logging.error('could not retrieve the tag (name: \'%s\') due %s', tag, e)
            return None

        self._tags[tag] = result

        return result

    def __get_product(self, product_name, product_type):
        result = None
        product_name = utils.upper(product_name)
        product_type = utils.upper(product_type)
        key = '{}#{}'.format(product_name, product_type)

        if(key in self._products):
            return self._products[key]

        try:
            with self._db as conn:
                with conn.cursor() as cursor:
                    query = queries.get_product_query(product_name, product_type)
                    self._db.execute(cursor, query['query'], query['params'])

                    if(not self._db.has_results(cursor)):
                        try:
                            self._db.execute(cursor, 'INSERT INTO products (name, type) VALUES (%s, %s)', [product_name, product_type])
                            if(not self._db.has_results(cursor)):
                                raise ProductNotInsertedException(product_name, product_type)

                        except psycopg2.IntegrityError:
                            conn.rollback()
                            logging.debug('the product (name: \'{}\', type: \'{}\') was added by other thread'.format(product_name, product_type))

                        self._db.execute(cursor, query['query'], query['params'])
                    
                    result = self._db.fetch(cursor)

        except Exception as e:
            logging.error('could not retrieve the product (name: \'%s\', type: \'%s\') due %s', product_name, product_type, e)
            return None

        self._products[key] = result

        return result

    def __get_issue(self, issue_name, issue_type):
        result = None
        issue_name = utils.upper(issue_name)
        issue_type = utils.upper(issue_type)
        key = '{}#{}'.format(issue_name, issue_type)

        if(key in self._issues):
            return self._issues[key]

        try:
            with self._db as conn:
                with conn.cursor() as cursor:
                    query = queries.get_issue_query(issue_name, issue_type)
                    self._db.execute(cursor, query['query'], query['params'])

                    if(not self._db.has_results(cursor)):
                        try:
                            self._db.execute(cursor, 'INSERT INTO issues (name, type) VALUES (%s, %s)', [issue_name, issue_type])
                            if(not self._db.has_results(cursor)):
                                raise IssueNotInsertedException(issue_name, issue_type)

                        except psycopg2.IntegrityError:
                            conn.rollback()
                            logging.debug('the issue (name: \'{}\', type: \'{}\') was added by other thread'.format(issue_name, issue_type))

                        self._db.execute(cursor, query['query'], query['params'])

                    result = self._db.fetch(cursor)

        except Exception as e:
            logging.error('could not retrieve the issue (name: \'%s\', type: \'%s\') due %s', issue_name, issue_type, e)
            return None

        self._issues[key] = result

        return result

    def __get_company(self, company_name):
        result = None
        company_name = utils.upper(company_name)

        if(company_name in self._companies):
            return self._companies[company_name]

        try:
            with self._db as conn:
                with conn.cursor() as cursor:
                    query = queries.get_company_query(company_name)
                    self._db.execute(cursor, query['query'], query['params'])

                    if(not self._db.has_results(cursor)):
                        try:
                            self._db.execute(cursor, 'INSERT INTO companies (name) VALUES (%s)', [company_name])
                            if(not self._db.has_results(cursor)):
                                raise CompanyNotInsertedException(company_name)
                        
                        except psycopg2.IntegrityError:
                            conn.rollback()
                            logging.debug('the company (name: \'{}\') was added by other thread'.format(company_name))

                        self._db.execute(cursor, query['query'], query['params'])

                    result = self._db.fetch(cursor)

        except Exception as e:
            logging.error('could not retrieve the company (name: \'%s\') due %s', company_name, e)
            return None

        self._companies[company_name] = result

        return result

    def __get_state(self, state_name):
        if(state_name is None):
            return None

        result = None
        state_name = utils.upper(state_name)

        if(state_name in self._states):
            self._states[state_name]

        try:
            with self._db as conn:
                with conn.cursor() as cursor:
                    query = queries.get_state_query(state_name)
                    self._db.execute(cursor, query['query'], query['params'])

                    if(not self._db.has_results(cursor)):
                        try:
                            self._db.execute(cursor, 'INSERT INTO states (name) VALUES (%s)', [state_name])
                            if(not self._db.has_results(cursor)):
                                raise StateNotInsertedException(state_name)
                        
                        except psycopg2.IntegrityError:
                            conn.rollback()
                            logging.debug('the state (name: \'{}\') was added by other thread'.format(state_name))

                        self._db.execute(cursor, query['query'], query['params'])

                    result = self._db.fetch(cursor)

        except Exception as e:
            logging.error('could not retrieve the state (name: \'%s\') due %s', state_name, e)
            return None

        self._states[state_name] = result

        return result


logging.basicConfig(level=logging.INFO)
etl = Etl()
etl.start()