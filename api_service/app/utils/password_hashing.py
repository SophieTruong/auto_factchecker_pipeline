import bcrypt

# hash password
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

# verify password
def verify_password(password: str, hashed_password: str) -> bool:
    password_byte_enc = password.encode('utf-8')    
    hashed_password_byte_enc = hashed_password
    print(f"password_byte_enc: {password_byte_enc}")
    print(f"hashed_password_byte_enc: {hashed_password_byte_enc}")
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)