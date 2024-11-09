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
    print("\033[1;32mUsername & Password have been saved successfully!\033[0m")

def load_hashed_udata(uf="ufile.bin"):
    # Load the hashed data from the binary file.
    try:
        with open(uf, "rb") as uf_file:
            return pickle.load(uf_file)
    except FileNotFoundError:
        print("\033[1;31mUsername or Password doesn't exist!\033[0m")
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
        print("\033[1;32mPermission Granted!\033[0m")
        return True
    else:
        print("\033[1;31mVerification failed! Username or Password doesn't match!\033[0m")
        return False

def nu_input():
    # If no data, prompt to save new credentials
    uname = input("> Enter your database Username: ")
    passcode = input(f"> Enter {uname}'s database Password: ")
    # Save the input username and password into the binary file
    save_hashed_udata(uname, passcode)
    return uname, passcode

def vu_input():
    # If data exists, prompt for verification
    v_uname = input("> Enter your database Username : ")
    v_passcode = input(f"> Enter {v_uname}'s database Password: ")
    # Verify the username and password against the stored data
    if uverification(v_uname, v_passcode):
        return v_uname, v_passcode
    else:
        print("\033[1;31mVerification Failed.!\033[0m")
        return None, None


def main_hash(uf="ufile.bin"):
    # Check if there is existing data in the file
    existing_data = load_hashed_udata(uf)

    if existing_data is None:
        print("\033[1;31mNo credentials found. Setting up new credentials.\033[0m")
        return nu_input()

    else:
        print("\033[1;33mCredentials found. Verifying...\033[0m")
        return vu_input()

if __name__ == "__main__":
    main_hash()
