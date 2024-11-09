import connection


db_con=connection.server()


if db_con and db_con.is_connected():
    db_con.close()
    print("\033[1;32mconnection successfully closed.!\033[0m")
