import sqlite3

db_path = 'c:/Users/waverider/Downloads/lidwa.db'
password = "EgSNvjq%7@cW86&J6fWzq9j@5SGhWx7jEtutbps7S@&h%d8f4ewyRkaqHmvr$SSx%qD*HSyuW8BVSJ4hSFH8#$tzdMS9B!rK@wYh$Qp%E6$5AYQpstzV@pXVctq4rzcg4NeTtxPn!YjRSFcUQ$wFufasszaHAcT3Qi&^PH6pHT$vEFsYWY$Ikw@P9ukkBcoGB%@lcsEKA37IIPjYKl!%z!to2JFO5!7M409Mmirv3X1utAZi!XHGWh#&E"

conn = sqlite3.connect(db_path)
try:
    conn.execute(f"PRAGMA key='{password}'")
    res = conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
    print("Success! Tables count:", res[0])
except Exception as e:
    print("Error:", e)
