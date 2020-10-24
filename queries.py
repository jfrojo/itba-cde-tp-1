from database import Database

hostname = os.environ['DATABASE_HOSTNAME']
port = os.environ['DATABASE_PORT']
database_name = os.environ['DATABASE_DB']
username = os.environ['DATABASE_USER']
password = os.environ['DATABASE_PASSWORD']
db = Database(hostname, port, database_name, username, password)

with db as conn:

    print('Query 1: Amount of complaints per company:')
    with conn.cursor() as cursor:
        result = db.query(cursor,   'SELECT \
                                    c.name AS company, \
                                    COUNT(*) AS amount\
                                FROM \
                                    complaints AS cs \
                                    LEFT JOIN companies AS c ON c.id = cs.company_id \
                                GROUP BY \
                                    c.name')
        
        print('company\tamount')
        for r in result:
            print(r[0] + '\t\t\t\t\t' + str(r[1]))
    
    print('\r\n\r\nQuery 2: Amount of complaints with specific tag:')
    with conn.cursor() as cursor:
        result = db.query(cursor,   'SELECT \
                                    t.name AS company,\
                                    COUNT(*) AS amount\
                                FROM \
                                    complaints AS cs \
                                    LEFT JOIN complaint_tags AS ct ON ct.complaint_id = cs.id \
                                    LEFT JOIN tags AS t ON t.id = ct.tag_id \
                                WHERE \
                                    t.name = \'SERVICEMEMBER\' \
                                GROUP BY \
                                    t.name')

        print('company\t\t\t\t\tamount')
        for r in result:
            print(r[0] + '\t\t\t\t\t' + str(r[1]))

    print('\r\n\r\nQuery 3: Find average response time for complaints responded in time per company:')
    with conn.cursor() as cursor:
        result = db.query(cursor,   'SELECT \
                                    c.name AS company,\
                                    AVG(cs.company_sent_date - cs.reception_date) AS elapsed \
                                FROM \
                                    complaints AS cs \
                                    LEFT JOIN companies AS c ON c.id = cs.company_id \
                                WHERE \
                                    cs.timely_response = true \
                                GROUP BY \
                                    company')

        print('company\t\t\t\t\telapsed')
        for r in result:
            print(r[0] + '\t\t\t\t\t' + str(r[1]))

    print('\r\n\r\nQuery 4: Find registered companies:')
    with conn.cursor() as cursor:
        result = db.query(cursor,   'SELECT \
                                    COUNT(*) AS company_amount\
                                FROM \
                                    companies')

        print('registered companies: ' + str(result[0][0]))

    print('\r\n\r\nQuery 5: Amount of complaints not responded in time per channel:')
    with conn.cursor() as cursor:
        result = db.query(cursor,   'SELECT \
                                    cs.submission_channel AS channel,\
                                    COUNT(*) AS amount \
                                FROM \
                                    complaints AS cs \
                                WHERE \
                                    cs.timely_response = false\
                                GROUP BY channel')

        print('channel\t\t\t\t\tamount')
        for r in result:
            print(r[0] + '\t\t\t\t\t' + str(r[1]))

db.close()
exit(0)