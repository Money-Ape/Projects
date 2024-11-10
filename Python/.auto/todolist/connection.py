import mysql.connector
from mysql.connector import Error
import hashed

schema = "taskdo"

def con(user, passcode):
    return mysql.connector.connect(
        host="localhost",
        user=user,
        passwd=passcode,
        database=schema
    )

def server():
    user, passcode = hashed.main_hash()
    db_con = None
    while True:
        try:
            db_con = con(user, passcode)
            if db_con.is_connected():
                print(f"\033[1;32m{user}'s database connected successfully!\033[0m")
                print(f"\033[1;32m'{schema}' has been selected as the default database.\033[0m")
                return db_con
        except Error as err:
            print(f"\033[1;31mError: {err}\033[0m")
            print("\033[1;31mInvalid username or password. Please try again.\033[0m")
        finally:
            if db_con and db_con.is_connected():
                db_con.close()
                print("\033[1;32mConnection successfully closed.\033[0m")
