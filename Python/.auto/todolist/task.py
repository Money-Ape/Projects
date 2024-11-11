import connection

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
