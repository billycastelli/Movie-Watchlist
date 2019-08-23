import mysql.connector

def connect():
    conn = mysql.connector.connect(host="x", user="x", password="x", database="x")
    cursor = conn.cursor()
    return conn, cursor
