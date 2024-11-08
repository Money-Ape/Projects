import mysql.connector as typing
import pickle


user=input("> Enter your database Username : ")
passcode=input(f"> Enter {user}'s database Password : ")
schema="taskdo"

def con():
    global user, passcode, schema
    return typing.connect(
            host="localhost",
            user=user,
            passwd=passcode,
            database=schema.format('{}','{}','{}')
            )

def uname_save(user):
    with open("ufile.bin","wb") as f:
        pickle.dump(user, f)
    print(f"\033[1;32mUsername detected.!: '{user}'\nsaved successfully.!\033[0m")

def load_uname():
    try:
        # Open the binary file for reading username.
        with open("ufile.bin", "rb") as f:
            uname = pickle.load(f)  # load the username from the binary file
        return uname

    except FileNotFoundError:
        print("\033[1;31mUsername not found...\033[0m")
        return None

def main():
    # loads the username from the binary file.
    uname=load_uname()
    if uname is None:
        uname_save(user)
    else:
        print(f"\n\033[1;32mWelcome back, {uname}.!\033[0m\n")

if __name__=="__main__":
    main()

db_con = con()
# Connection Verification...
def verify():
    global db_con
    while True:

        try:  # Password will verify, if gets wrong it will recontinue.!

            if db_con.is_connected():  # Connection is successfully established so exited from the loop.!
                print(f"\033[1;32m{user}'s\033[0m database connected successfully.!\n'\033[1;32m{schema}\033[0m' has been selected as default Database.!")
                break

        # If any Error, displayed by connector as 'err' here.!
        except typing.Error as err:
            print(f"\033[1;31mError...  {err}\033[0m")
            print(f"\033[1;31mYou Entered : {passcode} as passwd... Failed connection..,\nPlease try again.!\033[0m")

        # Optionally close the connection in case of a partial connection
        if 'db_con' in locals() and db_con.is_connected():
            db_con.close()
            print("\033[1;32mconnection closed.!\033[0m")

verify()

cur = db_con.cursor()



if db_con.is_connected():
    db_con.close()
    print("\033[1;32mconnection closed.!\033[0m")
