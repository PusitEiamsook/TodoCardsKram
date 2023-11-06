# This is the script user.py, which will be handling all-things users
# This includes: authentication, changing usernames & password, 
import os, hashlib, hmac

# global variable for consistant salt size
SALT_SIZE = 16

# Authentication function to generate password hash
# Note that the salt is simply concatenated to the hash
def hash_password(password):
    salt = os.urandom(SALT_SIZE)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hex(int.from_bytes(pw_hash + salt, 'big'))[2:]

# Authentication function to generate password hash
# using indexing to retrieve the salt
def is_password_correct(pw_salt_hash, password):
    byte_hash = bytes.fromhex(pw_salt_hash)
    salt = byte_hash[-SALT_SIZE:]
    pw_hash = byte_hash[:-SALT_SIZE]
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )

# authenticates a user using username and password,
# returns True or False
def login(mydb, username, password):

    with mydb.cursor() as mycursor:
        mycursor.execute(
            """
            SELECT password FROM user WHERE username = %s
            """, (username,))
        
        result = mycursor.fetchall()
        if len(result) != 0:
            return is_password_correct(result[0][0], password)
        else:
            return False

# check for not-duplicate username then insert a new user
# returns True or False
def signup(mydb, username, password):

    hs_pwd = hash_password(password)

    with mydb.cursor() as mycursor:

        mycursor.execute("SELECT COUNT(*) FROM user WHERE username = %s", (username,))
        
        result = mycursor.fetchall()
        if result[0][0] != 0:
            return False

        mycursor.execute("INSERT INTO user VALUES (%s, %s)", (username, hs_pwd))
        mydb.commit()
        return login(mydb, username, password)