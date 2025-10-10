from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Form
from fastapi.responses import StreamingResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE, ACCESS_TOKEN_EXPIRE_MINUTES
import sqlite3
import os
from typing import Optional, List, Dict, cast
import io
from pydantic import BaseModel

# 🔹 Usar Argon2 en lugar de bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

app = FastAPI(title="EncryptU API")

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'database')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'encryptu_api.db')


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        content BLOB NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        email TEXT,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

init_db()

# 🔹 Funciones de hashing y verificación
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(username: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(uid: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (uid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    return user


@app.post('/register', status_code=status.HTTP_201_CREATED)
def register(username: str = Form(...), password: str = Form(...)):
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, get_password_hash(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    conn.close()
    return {"msg": "user created"}


@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(cast(str, username))
    if user is None:
        raise credentials_exception
    return user


@app.post('/upload')
def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    content = file.file.read()
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (owner_id, filename, content, created_at) VALUES (?, ?, ?, ?)",
        (current_user['id'], file.filename, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    file_id = cur.lastrowid
    conn.close()
    return {"msg": "uploaded", "filename": file.filename, "id": file_id}


@app.get('/download/{file_id}')
def download_file(file_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM files WHERE id = ? AND owner_id = ?",
        (file_id, current_user['id'])
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    data = row['content']
    filename = row['filename']
    return StreamingResponse(
        io.BytesIO(data),
        media_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.get('/files')
def list_files(current_user: dict = Depends(get_current_user)) -> List[Dict]:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename, created_at FROM files WHERE owner_id = ? ORDER BY created_at DESC",
        (current_user['id'],)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete('/files/{file_id}')
def delete_file(file_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM files WHERE id = ? AND owner_id = ?', (file_id, current_user['id']))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail='File not found')
    cur.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return {'msg': 'deleted'}


class Ticket(BaseModel):
    email: Optional[str] = None
    subject: str
    body: str


@app.post('/tickets', status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: Ticket, current_user: dict = Depends(get_current_user)):
    conn = get_db_conn()
    cur = conn.cursor()
    owner_id = current_user['id'] if current_user else None
    cur.execute('INSERT INTO tickets (owner_id, email, subject, body, created_at) VALUES (?, ?, ?, ?, ?)',
                (owner_id, ticket.email, ticket.subject, ticket.body, datetime.utcnow().isoformat()))
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return {'msg': 'ticket created', 'id': ticket_id}


@app.get('/status')
def get_status():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
