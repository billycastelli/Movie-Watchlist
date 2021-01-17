import mysql.connector
import os

def connect():
    conn = mysql.connector.connect(host=os.environ["MYSQL_HOST_IP"], user=os.environ["MYSQL_USER"], \
                                password=os.environ["MYSQL_PASS"], database=os.environ["MYSQL_DB"])
    cursor = conn.cursor(buffered=True)
    return conn, cursor
