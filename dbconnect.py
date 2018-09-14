import MySQLdb as mysql

def connect():
    conn = mysql.connect(host='127.0.0.1',
                          user = 'root',
                          passwd = 'xxxxxxxx',
                          db = 'xxxxxxxx',
                          port = 3306,
                          unix_socket = 'xxxxxxxx')
    c = conn.cursor()
    return c
