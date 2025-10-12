import os
import io
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

# Cargar variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = secrets.token_hex(32)  # Genera una nueva llave secreta al iniciar
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- CONTEXTO DE HASHING ---
# Se mantiene Argon2 para la compatibilidad con las contraseñas existentes
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- CONFIGURACIÓN DE LA BASE DE DATOS (POSTGRESQL CONSQLALCHEMY) ---
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada en el archivo .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DE LA BASE DE DATOS (ORM) ---
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="usuario")
    createdAt = Column(DateTime, default=datetime.utcnow)

class FileStorage(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContactTicket(Base):
    __tablename__ = "contact_tickets"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

# --- INICIALIZACIÓN DE LA APP Y LA BD ---
app = FastAPI(title="EncryptU API Unificada")

@app.on_event("startup")
def on_startup():
    # Crea las tablas en la base de datos si no existen
    Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
#     allow_headers=["*"], # Permite todos los headers
# )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- FUNCIONES DE AUTENTICACIÓN Y USUARIO (ADAPTADAS A POSTGRESQL) ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.passwordHash):  # type: ignore
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: Se requieren permisos de administrador.")
    return current_user

# --- ENDPOINTS DE LA API (ACTUALIZADOS) ---

@app.post('/register', status_code=status.HTTP_201_CREATED)
def register(name: str = Form(...), email: EmailStr = Form(...), db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    master_key = secrets.token_hex(16)
    
    # El primer usuario registrado será administrador
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "usuario"
    
    new_user = User(
        name=name,
        email=email,
        passwordHash=get_password_hash(master_key),
        role=role
    )
    db.add(new_user)
    db.commit()
    
    return {"msg": f"Usuario '{name}' creado exitosamente con rol '{role}'.", "master_key": master_key}

@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password) # form_data.username es el email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o Clave Maestra incorrectos"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_role": user.role}

# --- ENDPOINTS PARA LA APP DE ESCRITORIO (SIN CAMBIOS EN LÓGICA) ---

@app.post('/upload')
def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = file.file.read()
    db_file = FileStorage(
        owner_id=current_user.id,
        filename=file.filename,
        content=content
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {"msg": "Archivo subido", "filename": file.filename, "id": db_file.id}

@app.get('/download/{file_id}')
def download_file(file_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_file = db.query(FileStorage).filter(FileStorage.id == file_id, FileStorage.owner_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado o no tienes permiso para accederlo.")
    return StreamingResponse(io.BytesIO(db_file.content), media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{db_file.filename}"'})  # type: ignore

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

@app.get('/admin/user', response_model=List[Dict[str, Any]])
def list_all_users(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    users = db.query(User.id, User.name, User.email, User.role).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]

@app.delete('/admin/user/{user_id}', status_code=status.HTTP_200_OK)
def delete_user_by_admin(user_id: int, current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Un administrador no puede eliminar su propia cuenta.")
    
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado.")

    # Eliminar datos asociados (cascada)
    db.query(FileStorage).filter(FileStorage.owner_id == user_id).delete()
    db.delete(user_to_delete)
    db.commit()
        
    return {'msg': f'Usuario con ID {user_id} y todos sus datos han sido eliminados.'}

# --- ENDPOINTS PARA EL WEBSITE (NUEVO) ---

class TicketWebsite(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    reason: str
    phone: str
    description: str

@app.post('/contact-ticket', status_code=status.HTTP_201_CREATED)
def create_contact_ticket(ticket: TicketWebsite, db: Session = Depends(get_db)):
    new_ticket = ContactTicket(**ticket.dict())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return {'msg': 'Ticket de contacto recibido. Gracias.', 'ticket_id': new_ticket.id}

@app.get('/admin/contact-tickets', response_model=List[Dict[str, Any]])
def list_all_contact_tickets(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    tickets = db.query(ContactTicket).order_by(ContactTicket.createdAt.desc()).all()
    return [t.__dict__ for t in tickets]

@app.get('/test-db')
def test_db_connection(db: Session = Depends(get_db)):
    """
    Endpoint de diagnóstico para verificar la conexión con la base de datos de Neon.
    """
    try:
        # Ejecuta una consulta SQL muy simple que pide la hora actual al servidor de la BD.
        # Si esto funciona, la conexión es exitosa.
        result = db.execute(text('SELECT NOW()'))
        db_time = result.scalar_one()
        
        # Si la consulta fue exitosa, devuelve un mensaje de OK y la hora del servidor de BD.
        return {
            "status": "ok", 
            "message": "La conexión con la base de datos de Neon es exitosa.",
            "database_server_time": db_time
        }
    except Exception as e:
        # Si ocurre cualquier error durante la conexión o la consulta,
        # levanta una excepción HTTP 500 con un mensaje de error detallado.
        print(f"ERROR DE CONEXIÓN A LA BD: {e}") # Esto aparecerá en tus logs de Render
        raise HTTPException(
            status_code=500, 
            detail=f"No se pudo conectar a la base de datos: {e}"
        )


# --- ENDPOINT DE ESTADO ---
@app.get('/status')
def get_status():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}