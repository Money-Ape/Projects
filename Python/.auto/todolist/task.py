import connection

# Establish a database connection
db_con = connection.server()

# Check if the connection is active and create a cursor for database operations
if db_con and db_con.is_connected():
    try:
        with db_con.cursor() as cursor:
            # Example query (replace with actual queries as needed)
            cursor.execute("SELECT DATABASE();")
            result = cursor.fetchone()
            print("Connected to database:", result[0])

    except Exception as e:
        print(f"\033[1;31mQuery execution failed: {e}\033[0m")

    finally:
        # Ensure the connection is closed
        db_con.close()
        print("\033[1;32mConnection closed successfully.\033[0m")
