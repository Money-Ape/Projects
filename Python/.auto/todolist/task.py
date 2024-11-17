import connection

def money_ape():

    print("\033[1;93m __  __                                _          \033[0m")
    print("\033[1;93m|  \\/  | ___  _ __   ___ _   _        / \\   _ __   ___ \033[0m")
    print("\033[1;93m| |\\/| |/ _ \\| '_ \\ / _ \\ | | |_____ / _ \\ | '_ \\ / _ \\\033[0m")
    print("\033[1;93m| |  | | (_) | | | |  __/ |_| |_____/ ___ \\| |_) |  __/\033[0m")
    print("\033[1;93m|_|  |_|\\___/|_| |_|\\___|\\__, |    /_/   \\_\\ .__/ \\___|\033[0m")
    print("\033[1;93m                         |___/             |_|\033[0m")
    print("\033[1;32m\n                    Github : Money-Ape\033[0m {verison : 1.1}\n")
money_ape()


# Establish a database connection
db_con = connection.server()

# Check if the connection is active and create a cursor for database operations
if db_con.is_connected():
    try:
        with db_con.cursor() as cursor:
            result = cursor.fetchone()
            print(result[0])

    # Check for the Errors.!
    except Exception as e:
        print(f"\033[1;31mQuery execution failed: {e}\033[0m")

    finally:
        # Ensure the connection is closed
        db_con.close()
        print("\033[1;32mConnection successfully closed.!\033[0m")
