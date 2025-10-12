import os
import io
import secrets
import datetime
from datetime import timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada en el archivo .env")

DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- NUEVA BASE DECLARATIVA MODERNA ---
class Base(DeclarativeBase):
    pass

# --- MODELOS ORM ACTUALIZADOS CON SINTAXIS MODERNA ---
class User(Base):
    __tablename__ = "User"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    passwordHash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="usuario")
    createdAt: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class FileStorage(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    filename: Mapped[str] = mapped_column(String)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ContactTicket(Base):
    __tablename__ = "contact_tickets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    firstName: Mapped[str] = mapped_column(String)
    lastName: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    createdAt: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

# --- INICIALIZACIÓN DE LA APP ---
app = FastAPI(title="EncryptU API Unificada")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- FUNCIONES DE AUTENTICACIÓN ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    # Con los modelos modernos, Pylance ya no dará un error aquí
    if not user or not verify_password(password, user.passwordHash):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None: raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None: raise credentials_exception
    return user

# --- MODELOS PYDANTIC ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    createdAt: datetime.datetime

# --- ENDPOINTS PRINCIPALES ---

@app.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "usuario"
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        passwordHash=hashed_password,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o Contraseña incorrectos")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_role": user.role}

# --- ENDPOINTS PARA ARCHIVOS ---

@app.post('/upload')
def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = file.file.read()
    db_file = FileStorage(owner_id=current_user.id, filename=file.filename, content=content)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {"msg": "Archivo subido", "filename": file.filename, "id": db_file.id}

@app.get('/download/{file_id}')
def download_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_file = db.query(FileStorage).filter(FileStorage.id == file_id, FileStorage.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    return StreamingResponse(io.BytesIO(db_file.content), media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{db_file.filename}"'})

@app.get('/files', response_model=List[Dict[str, Any]])
def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = db.query(FileStorage.id, FileStorage.filename, FileStorage.created_at).filter(FileStorage.owner_id == current_user.id).order_by(FileStorage.created_at.desc()).all()
    return [{"id": f.id, "filename": f.filename, "created_at": f.created_at.isoformat()} for f in files]

@app.delete('/files/{file_id}', status_code=status.HTTP_200_OK)
def delete_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_file = db.query(FileStorage).filter(FileStorage.id == file_id, FileStorage.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    db.delete(db_file)
    db.commit()
    return {'msg': f'Archivo con ID {file_id} eliminado.'}

# --- ENDPOINTS DE ADMINISTRACIÓN ---

@app.get('/admin/User', response_model=List[UserOut])
def list_all_users(current_admin: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.delete('/admin/User/{user_id}', status_code=status.HTTP_200_OK)
def delete_user_by_admin(user_id: int, current_admin: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Un administrador no puede eliminar su propia cuenta.")
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado.")
    db.query(FileStorage).filter(FileStorage.owner_id == user_id).delete()
    db.delete(user_to_delete)
    db.commit()
    return {'msg': f'Usuario con ID {user_id} y todos sus datos han sido eliminados.'}

# --- ENDPOINTS DE DIAGNÓSTICO ---

@app.get('/test-db')
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text('SELECT NOW()'))
        db_time = result.scalar_one()
        return {"status": "ok", "message": "Conexión a Neon exitosa.", "database_server_time": db_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar a la base de datos: {e}")

@app.get('/status')
def get_status():
    return {"status": "ok", "time": datetime.datetime.utcnow().isoformat()}