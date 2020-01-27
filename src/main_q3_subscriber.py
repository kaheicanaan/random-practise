import time
import os
import psycopg2
from simple_counter import message_queue


pg_host = os.environ.get('PG_HOST', 'localhost')
pg_port = int(os.environ.get('PG_PORT', '5432'))
pg_db = os.environ.get('PG_DB', 'canaan_imac')
pg_username = os.environ.get('PG_USERNAME', 'canaan_imac')
pg_password = os.environ.get('PG_PASSWORD', 'None')

# message queue and DB connection
msg_q = message_queue.MessageQueueSQS()
conn = psycopg2.connect(dbname=pg_db, user=pg_username, password=pg_password, host=pg_host, port=pg_port)
cur = conn.cursor()

# sql statement
value_format = "('{candidate}', '{vote_time}', '{kiosk_id}')"

insert_statement = """
INSERT INTO votes (candidate, voteTime, kioskId)
VALUES {values}
ON CONFLICT DO NOTHING;
"""

while True:
    """
    (1) keep loop and subscribe message from SQS.
    (2) batch insert to DB
    (3) delete handled messages in SQS
    (4) sleep (only when there is no data to be inserted)
    """
    # get data from SQS
    votes_info, msg_handles = msg_q.receive_votes()

    if votes_info:
        # format sql statement
        values = [value_format.format(**vote_info) for vote_info in votes_info]
        sql = insert_statement.format(values=', '.join(values))

        # insert into DB
        cur.execute(sql)
        conn.commit()

        # delete inserted message
        msg_q.delete_handled_msg(msg_handles)
        print(f'Handled {len(votes_info)} data.', flush=True)
    else:
        time.sleep(1)
