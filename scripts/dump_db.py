import ctypes
import os

dll_path = r"G:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\scratch\dbb\DB Browser for SQLite\sqlcipher.dll"
sqlcipher = ctypes.CDLL(dll_path)

db_path = b"c:/Users/waverider/Downloads/lidwa.db"
password = b"EgSNvjq%7@cW86&J6fWzq9j@5SGhWx7jEtutbps7S@&h%d8f4ewyRkaqHmvr$SSx%qD*HSyuW8BVSJ4hSFH8#$tzdMS9B!rK@wYh$Qp%E6$5AYQpstzV@pXVctq4rzcg4NeTtxPn!YjRSFcUQ$wFufasszaHAcT3Qi&^PH6pHT$vEFsYWY$Ikw@P9ukkBcoGB%@lcsEKA37IIPjYKl!%z!to2JFO5!7M409Mmirv3X1utAZi!XHGWh#&E"

def dump_db(compatibility):
    db_ptr = ctypes.c_void_p()
    if sqlcipher.sqlite3_open(db_path, ctypes.byref(db_ptr)) != 0:
        return False

    def execute_sql(sql):
        errmsg = ctypes.c_char_p()
        res = sqlcipher.sqlite3_exec(db_ptr, sql, None, None, ctypes.byref(errmsg))
        if res != 0:
            if errmsg.value:
                print(f"Error {res}: {errmsg.value.decode('utf-8', errors='ignore')}")
            return False
        return True

    # Apply compatibility
    if compatibility == 3:
        execute_sql(b"PRAGMA cipher_compatibility = 3;")
    elif compatibility == 2:
        execute_sql(b"PRAGMA cipher_compatibility = 2;")
    elif compatibility == 1:
        execute_sql(b"PRAGMA cipher_compatibility = 1;")
    elif compatibility == 4096:
        execute_sql(b"PRAGMA cipher_page_size = 4096;")
        execute_sql(b"PRAGMA kdf_iter = 64000;")
        execute_sql(b"PRAGMA cipher_hmac_algorithm = HMAC_SHA1;")
        execute_sql(b"PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;")

    # Provide key
    if sqlcipher.sqlite3_key(db_ptr, password, len(password)) != 0:
        print("sqlite3_key failed")
        
    # Test reading
    if not execute_sql(b"SELECT count(*) FROM sqlite_master;"):
        sqlcipher.sqlite3_close(db_ptr)
        return False

    print(f"Success with compatibility {compatibility}!")
    
    out_db = b"G:/AntigravityPortable/.gemini/antigravity/lidwa_dump.db"
    if os.path.exists(out_db.decode('utf-8')):
        os.remove(out_db.decode('utf-8'))

    execute_sql(b"ATTACH DATABASE '" + out_db + b"' AS plaintext KEY '';")
    print("Exporting...")
    execute_sql(b"SELECT sqlcipher_export('plaintext');")
    execute_sql(b"DETACH DATABASE plaintext;")
    print("Done exporting to lidwa_dump.db!")
    sqlcipher.sqlite3_close(db_ptr)
    return True

for comp in [4, 3, 2, 1, 4096]:
    print(f"Trying compatibility {comp}...")
    if dump_db(comp):
        break
