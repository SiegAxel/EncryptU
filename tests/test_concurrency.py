import threading
import sqlite3
import tempfile
import os
import time
import random


def _insert_user_with_retries(db_path: str, user_id: int, max_retries: int = 5):
    attempt = 0
    while attempt < max_retries:
        try:
            conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
            # Mejorar concurrencia
            conn.execute('PRAGMA journal_mode = WAL')
            c = conn.cursor()
            c.execute("INSERT INTO User (username) VALUES (?)", (f'user_{user_id}',))
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            # database is locked -> reintentar con backoff
            attempt += 1
            time.sleep(0.01 * (2 ** attempt) + random.random() * 0.01)
        except Exception:
            return False
    return False


def test_p1_concurrency(tmp_path):
    # Crear una base de datos temporal en disco para simular concurrencia real
    db_file = tmp_path / "test_db_concurrency.db"
    db_path = str(db_file)

    print("\n" + "="*60)
    print("PRUEBA DE CONCURRENCIA P1")
    print("="*60)

    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode = WAL')
    conn.execute("CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)")
    conn.commit()
    conn.close()

    print("Base de datos temporal creada con modo WAL")
    print("Iniciando 50 inserciones concurrentes en 5 threads...")
    
    start_time = time.time()
    threads = []
    for i in range(50):
        t = threading.Thread(target=_insert_user_with_retries, args=(db_path, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time

    # Verificar cuántos se insertaron
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT count(*) FROM User").fetchone()[0]
    conn.close()

    print(f"Usuarios insertados: {count}/50")
    print(f"Tiempo total: {elapsed:.2f} segundos")
    print(f"Velocidad: {50/elapsed:.0f} inserciones/segundo")
    print("Modo de diario: WAL (Write-Ahead Logging)")
    print("[OK] Prueba de concurrencia completada")
    print("="*60)

    # Esperamos que 50 usuarios hayan sido insertados
    assert count == 50, f"Se insertaron {count}/50 usuarios; hubo bloqueo o fallo"
