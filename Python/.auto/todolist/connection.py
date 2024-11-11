import mysql.connector
from mysql.connector import Error
import hashed

schema = "taskdo"  #Default database for todo.!

def con(user, passcode):  # Connection creates here for the DataBase.
    return mysql.connector.connect(
        host="localhost",
        user=user,
        passwd=passcode,
        database=schema
    )

def server():  # Handles the connection for database.
    user, passcode = hashed.main_hash()
    db_con = None  # Initialise the connection variable to use it further with other modules too.!
    while True:
        try:
            db_con = con(user, passcode)
            if db_con.is_connected():  # Connection status : success.! (with mesg for successfully initialised connection.!
                print(f"\033[1;32m{user}'s database connected successfully!\033[0m")
                print(f"\033[1;32m'{schema}' has been selected as the default database.\033[0m")
                return db_con

        #Connection status : failure.! (with warn.! for faield connection.!
        except Error as err:
            print(f"\033[1;31mError: {err}\033[0m")
            print("\033[1;31mInvalid Username or Password... Please try again.!\033[0m")

            # Verification for credentials when the past input was Failed.!
            user, passcode = hashed.vu_input()

            # Warning mesg for again failed with verifing the credentials.
            if not user or not passcode:
                print("\033[1;31mFailed to verify credentials.!\nExiting...\033[0m")
                break

        # Close the partial connection.
        if 'db_con' and db_con.is_connected():
            db_con.close()
            print("\033[1;32mConnection closed.!\033[0m")
