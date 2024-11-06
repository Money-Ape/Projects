import mysql.connector as typing
import main_task

main_task.main()

con = main_task.con()
cur = con.cursor()

def data():
    tb="show tables"
    cur.execute(tb)
    tables=cur.fetchall()
    for table in tables:
        print(table)
    if not tables:
        print("tables not found.!")

data()
