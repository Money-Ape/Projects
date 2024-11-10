import hashlib as enc
import pickle

def hash_input(user_input):
    hash_data = enc.sha256(user_input.encode())
    return hash_data.hexdigest()

def save_hashed_udata(uname, passwd, uf="ufile.bin"):
    hashed_data = {
        "username": hash_input(uname),
        "password": hash_input(passwd)
    }
    with open(uf, "wb") as uf_file:
        pickle.dump(hashed_data, uf_file)
    print("\033[1;32mUsername & Password have been saved successfully!\033[0m")

def load_hashed_udata(uf="ufile.bin"):
    try:
        with open(uf, "rb") as uf_file:
            return pickle.load(uf_file)
    except FileNotFoundError:
        print("\033[1;31mUsername or Password doesn't exist!\033[0m")
        return None

def uverification(uname, passwd, uf="ufile.bin"):
    existing_data = load_hashed_udata(uf)
    if not existing_data:
        return False
    username = hash_input(uname)
    password = hash_input(passwd)
    if username == existing_data["username"] and password == existing_data["password"]:
        print("\033[1;32mPermission Granted!\033[0m")
        return True
    else:
        print("\033[1;31mVerification failed! Username or Password doesn't match!\033[0m")
        return False

def nu_input():
    uname = input("> Enter your database Username: ")
    passcode = input(f"> Enter {uname}'s database Password: ")
    save_hashed_udata(uname, passcode)
    return uname, passcode

def vu_input():
    v_uname = input("> Enter your database Username : ")
    v_passcode = input(f"> Enter {v_uname}'s database Password: ")
    if uverification(v_uname, v_passcode):
        return v_uname, v_passcode
    else:
        print("Verification failed.")
        return None, None

def main_hash():
    existing_data = load_hashed_udata()
    if existing_data is None:
        print("\033[1;31mNo credentials found. Setting up new credentials.\033[0m")
        return nu_input()
    else:
        print("\033[1;33mCredentials found. Verifying...\033[0m")
        return vu_input()

if __name__ == "__main__":
    user, passcode = main_hash()
    if user and passcode:
        print("\033[1;32mUser authenticated successfully.\033[0m")
    else:
        print("\033[1;31mAuthentication failed.\033[0m")
