import connection

db_con=connection.server()


if db_con and db_con.is_connected():
    try:
        if db_con.is_connected():
            with db_con.cursor() as cursor:
                result = cursor.fetchone()
                print("\033[1;32mconnected to database.! : \033[0m",result[0])

    except Exception as err:
        print(f"\033[1;31mError... Query execution failed.! : {err}\033[0m")

    finally:
        db_con.close()
        print("\033[1;32mconnection successfully closed.!\033[0m")
