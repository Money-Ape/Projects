import mysql.connector as typing
import hashed

schema="taskdo"

def con(user, passcode):
    return typing.connect(
            host="localhost",
            user=user,
            passwd=passcode,
            database=schema.format('{}','{}','{}')
            )

# user execution
user, passcode = hashed.main_hash()

#Connection Verification...
def server():
    while True:
        db_con = None
        try:  # Verifies the connection.!
            db_con = con(user, passcode)
            if db_con.is_connected():  # Connection is successfully established so exited from the loop.!
                print(f"\033[1;32m{user}'s\033[0m database connected successfully.!\n'\033[1;32m{schema}\033[0m' has been selected as default Database.!")
                return db_con
                break

        # If any Error, displayed by connector as 'err' here.!
        except typing.Error as err:
            print(f"\033[1;31mError...  {err}\033[0m")
            print(f"\033[1;31mYour Entered Username or Passwd wrong... Failed connection..,\nPlease try again.!\033[0m")

        # Optionally close the connection in case of a partial connection
        if 'db_con' in locals() and db_con.is_connected():
            db_con.close()
            print("\033[1;32mconnection closed.!\033[0m")


