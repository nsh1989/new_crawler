from typing import Any

import pymysql as pymysql
from pymysql.cursors import DictCursor


class DBMng:

    @staticmethod
    def get_one(sql: str) -> Any:
        conn = pymysql.connect(host='localhost', user='root', password='root', db='crawler', charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchone()
        conn.close()
        return rows

    @staticmethod
    def get_all(sql: str) -> Any:
        # cls.__cursor.execute(sql)
        # return cls.__cursor.fetchall()
        conn = pymysql.connect(host='localhost', user='root', password='root', db='crawler', charset='utf8',
                               cursorclass=DictCursor)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        rows: list = []
        for row in result:
            data: dict = {}
            for key, value in row.items():
                data[key] = value
            rows.append(data)
        conn.close()
        return rows

    @staticmethod
    def insert_dictionary(table_name: str, data: dict):
        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in data.keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in data.values())
        sql = "INSERT INTO %s ( %s ) values ( %s );" % (table_name, columns, values)
        DBMng.mutate(sql)

    @staticmethod
    def mutate(sql: str):
        conn = pymysql.connect(host='localhost', user='root', password='root', db='crawler', charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
