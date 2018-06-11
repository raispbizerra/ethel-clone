import psycopg2

def open_BD(dbname, host, user, password):
    connect_text = "dbname=" + dbname + " host=" + host + " user=" + user + " password=" + password
    #Connecting to DB
    conn = psycopg2.connect(connect_text)
    #Opening DB cursor
    cur = conn.cursor()

    return conn, cur

def select(cursor, columns, table):
    #Define o texto do select
    select_text = "SELECT" + columns + "FROM" +  table + ";"
    
    #Execute a query
    cursor.execute(select_text)

    #Retorno da query
    return cursor.fetchall()
