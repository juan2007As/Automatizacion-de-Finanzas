from app.core.security import get_password_hash, verify_password

plain_password = "misuperpassword"
hash_pw = get_password_hash(plain_password)
print(f"Hash generado: {hash_pw}")

is_valid = verify_password(plain_password, hash_pw)
print(f"Es valido?: {is_valid}")

if not is_valid:
    raise Exception("El hashing falló")
