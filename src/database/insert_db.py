import sqlite3
import os

base_path = os.path.join('src', 'database')
db_path = os.path.join(base_path, 'pass_main.db')

conn = sqlite3.connect(db_path)

conn.execute("INSERT INTO claves (clave_maestra) VALUES (?)", ('pepito123',))

conn.commit()

conn.close()
