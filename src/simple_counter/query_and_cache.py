import os
import psycopg2
from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple
import time


class CachingLayer:
    def __init__(self, expire_seconds: int = 60):
        pg_host = os.environ.get('PG_HOST', 'localhost')
        pg_port = int(os.environ.get('PG_PORT', '5432'))
        pg_db = os.environ.get('PG_DB', 'canaan_imac')
        pg_username = os.environ.get('PG_USERNAME', 'canaan_imac')
        pg_password = os.environ.get('PG_PASSWORD', 'None')
        self._connection_info = dict(dbname=pg_db, user=pg_username, password=pg_password, host=pg_host, port=pg_port)

        # init cached result
        self._expire_seconds = expire_seconds
        self._total_result = (datetime(2000, 1, 1), pd.DataFrame())
        self._ten_minutes_result = (datetime(2000, 1, 1), pd.DataFrame())

    def _get_connector(self):
        # DB connection every time query is required (prevent connection lost for long connection)
        conn = psycopg2.connect(**self._connection_info)
        cur = conn.cursor()
        return conn, cur

    def get_or_query_total_result(self) -> Tuple[datetime, pd.DataFrame]:
        """
        Find usable cached result. Query fresh result if necessary.
        :return:
        """
        current_time = datetime.utcnow()
        if (current_time - self._total_result[0]) > timedelta(seconds=self._expire_seconds):
            # query and replace old result
            self._total_result = (current_time, self._query_total_result())
        else:
            # old result can be used
            pass
        return self._total_result

    def _query_total_result(self) -> pd.DataFrame:
        # time.sleep(5)
        sql = """
        SELECT candidate, count(*)
        FROM votes
        GROUP BY candidate
        ORDER BY count DESC;
        """
        _, cur = self._get_connector()
        cur.execute(sql)
        data = pd.DataFrame(cur.fetchall(), columns=['candidate', 'count']).set_index('candidate')
        return data

    def get_or_query_ten_minutes_result(self) -> Tuple[datetime, pd.DataFrame]:
        """
        Find usable cached result. Query fresh result if necessary.
        :return:
        """
        current_time = datetime.utcnow()
        if (current_time - self._ten_minutes_result[0]) > timedelta(seconds=self._expire_seconds):
            # query and replace old result
            self._ten_minutes_result = (current_time, self._query_ten_minutes_result())
        else:
            # old result can be used
            pass
        return self._ten_minutes_result

    def _query_ten_minutes_result(self) -> pd.DataFrame:
        # time.sleep(5)
        ten_minutes_before = (datetime.utcnow() - timedelta(minutes=10)).strftime('%Y-%m-%d %T.%f')
        sql = f"""
                SELECT candidate, count(*)
                FROM votes
                WHERE votetime >= timestamp '{ten_minutes_before}'
                GROUP BY candidate
                ORDER BY count DESC;
                """
        _, cur = self._get_connector()
        cur.execute(sql)
        data = pd.DataFrame(cur.fetchall(), columns=['candidate', 'count']).set_index('candidate')
        return data


if __name__ == '__main__':
    # testing
    cl = CachingLayer()
    # first query
    total_result = cl.get_or_query_total_result()
    ten_minutes_result = cl.get_or_query_ten_minutes_result()
    print(total_result)
    print(ten_minutes_result)
    # second query
    total_result = cl.get_or_query_total_result()
    ten_minutes_result = cl.get_or_query_ten_minutes_result()
    print(total_result)
    print(ten_minutes_result)
