import hashlib as enc
import pickle

def hash_input(user_input):
    # Use SHA-256 to hash user input.
    hash_data = enc.sha256(user_input.encode())
    return hash_data.hexdigest()

def save_hashed_udata(uname, passwd, uf="ufile.bin"):
    # Hash the username & password separately.
    hashed_data = {
        "username": hash_input(uname),
        "password": hash_input(passwd)
    }

    # Save hashed data in binary format.
    with open(uf, "wb") as uf_file:
        pickle.dump(hashed_data, uf_file)
    print("Username & Password have been saved successfully!")

def load_hashed_udata(uf="ufile.bin"):
    # Load the hashed data from the binary file.
    try:
        with open(uf, "rb") as uf_file:
            return pickle.load(uf_file)
    except FileNotFoundError:
        print("Username or Password doesn't exist!")
        return None

def uverification(uname, passwd, uf="ufile.bin"):
    # Load the existing data from the file.
    existing_data = load_hashed_udata(uf)
    if not existing_data:
        return False

    # Hash the input username and password
    username = hash_input(uname)
    password = hash_input(passwd)

    # Check if both the username and password match the stored hashes
    if username == existing_data["username"] and password == existing_data["password"]:
        print("Permission Granted!")
        return True
    else:
        print("Verification failed! Username or Password doesn't match!")
        return False

def main_hash(uf="ufile.bin"):
    # Check if there is existing data in the file
    existing_data = load_hashed_udata(uf)

    if existing_data is None:
        # If no data, prompt to save new credentials
        uname = input("> Enter your database Username: ")
        passwd = input(f"> Enter {uname}'s database Password: ")
        # Save the input username and password into the binary file
        save_hashed_udata(uname, passwd)
    else:
        # If data exists, prompt for verification
        v_uname = input("> Enter your database Username for verification: ")
        v_passwd = input(f"> Enter {v_uname}'s database Password: ")
        # Verify the username and password against the stored data
        uverification(v_uname, v_passwd)

if __name__ == "__main__":
    main_hash()
