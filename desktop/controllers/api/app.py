import os
import io
import secrets
import datetime
import re
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary, text, inspect
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = (
    os.getenv("AUTH_SECRET")
    or os.getenv("SECRET_KEY")
    or os.getenv("JWT_SECRET")
)
if not SECRET_KEY:
    raise RuntimeError(
        "AUTH_SECRET (o SECRET_KEY) no está configurado en el entorno del servidor."
    )

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
    __tablename__ = "ContactTicket"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    firstName: Mapped[str] = mapped_column(String)
    lastName: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    createdAt: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="open")
    assignedToId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("User.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True
    )
    assigned_to = relationship("User", backref="tickets_assigned", lazy="joined")
    messages = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.created_at",
    )

class TicketMessage(Base):
    __tablename__ = "TicketMessage"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(
        "ticketId",
        ForeignKey("ContactTicket.id", ondelete="CASCADE"),
        index=True,
    )
    author: Mapped[str] = mapped_column(String, default="user")
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "createdAt",
        DateTime,
        default=datetime.datetime.utcnow,
    )
    ticket = relationship("ContactTicket", back_populates="messages")

# --- INICIALIZACIÓN DE LA APP ---
def ensure_contact_ticket_columns() -> None:
    """Ensure legacy databases include newer support ticket columns."""
    inspector = inspect(engine)

    def resolve_table() -> Optional[tuple[str, Optional[str]]]:
        schema_candidates: List[Optional[str]] = []
        default_schema = getattr(inspector, "default_schema_name", None)
        if default_schema:
            schema_candidates.append(default_schema)
        schema_candidates.append(None)  # fallback search without schema

        for schema_name in schema_candidates:
            for candidate in ("ContactTicket"):
                try:
                    if inspector.has_table(candidate, schema=schema_name):
                        return candidate, schema_name
                except Exception:
                    continue
        return None

    resolved = resolve_table()
    if not resolved:
        return

    table_name, schema_name = resolved
    try:
        columns = {
            col["name"] for col in inspector.get_columns(table_name, schema=schema_name)
        }
    except Exception:
        return

    def qualify(identifier: str) -> str:
        def quote(name: str) -> str:
            return f'"{name}"' if name and name.lower() != name else name

        table_sql = quote(table_name)
        if schema_name:
            schema_sql = quote(schema_name)
            return f"{schema_sql}.{table_sql}"
        return table_sql

    qualified_table = qualify(table_name)

    statements = []
    if "status" not in columns:
        statements.append(
            text(f"ALTER TABLE {qualified_table} ADD COLUMN status TEXT DEFAULT 'open'")
        )
        statements.append(
            text(f"UPDATE {qualified_table} SET status = 'open' WHERE status IS NULL")
        )
    if "assignedToId" not in columns:
        statements.append(
            text(
                f'ALTER TABLE {qualified_table} ADD COLUMN "assignedToId" INTEGER'
            )
        )
        statements.append(
            text(
                f'ALTER TABLE {qualified_table} ADD CONSTRAINT "{table_name}_assignedToId_fkey" '
                f'FOREIGN KEY ("assignedToId") REFERENCES "User"(id) '
                "ON UPDATE CASCADE ON DELETE SET NULL"
            )
        )

    if not statements:
        return

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(statement)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_contact_ticket_columns()
    yield


app = FastAPI(title="EncryptU API Unificada", lifespan=lifespan)


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
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # type: ignore

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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
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


class SupportTicketCreate(BaseModel):
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: Optional[EmailStr] = None
    reason: str
    phone: str
    description: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("first_name", "last_name", "reason", "description")
    @classmethod
    def _trim_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Este campo es obligatorio.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 9:
            raise ValueError("El telefono debe tener exactamente 9 digitos.")
        return digits

    @field_validator("reason")
    @classmethod
    def _validate_reason(cls, value: str) -> str:
        slug = value.strip().lower()
        if slug not in {"soporte", "consulta"}:
            raise ValueError("Motivo no valido.")
        return slug
    
class SupportTicketMessageCreate(BaseModel):
    body: str

    @field_validator("body")
    @classmethod
    def _trim_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El mensaje no puede estar vacio.")
        return cleaned[:2000]

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

# --- ENDPOINTS DE SOPORTE ---

@app.post("/support/tickets")
def create_support_ticket(
    ticket_data: SupportTicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = (ticket_data.email or current_user.email).strip().lower()
    ticket = ContactTicket(
        firstName=ticket_data.first_name,
        lastName=ticket_data.last_name,
        email=email,
        reason=ticket_data.reason,
        phone=ticket_data.phone,
        description=ticket_data.description,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ok": True,
        "ticket": {
            "id": ticket.id,
            "first_name": ticket.firstName,
            "last_name": ticket.lastName,
            "email": ticket.email,
            "reason": ticket.reason,
            "status": ticket.status,
            "phone": ticket.phone,
            "description": ticket.description,
            "created_at": ticket.createdAt.isoformat(),
            "messages_count": 0,
        },
    }


@app.get("/support/tickets")
def list_support_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(ContactTicket)
        .filter(ContactTicket.email == current_user.email)
        .order_by(ContactTicket.createdAt.desc())
        .all()
    )
    payload = []
    for ticket in tickets:
        payload.append(
            {
                "id": ticket.id,
                "first_name": ticket.firstName,
                "last_name": ticket.lastName,
                "email": ticket.email,
                "reason": ticket.reason,
                "status": ticket.status,
                "phone": ticket.phone,
                "description": ticket.description,
                "created_at": ticket.createdAt.isoformat(),
                "messages_count": len(ticket.messages),
            }
        )
    return {"ok": True, "tickets": payload}


def _get_ticket_for_user(db: Session, ticket_id: int, user: User) -> ContactTicket:
    ticket = (
        db.query(ContactTicket)
        .filter(ContactTicket.id == ticket_id, ContactTicket.email == user.email)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    return ticket


@app.get("/support/tickets/{ticket_id}/messages")
def list_ticket_messages(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_ticket_for_user(db, ticket_id, current_user)
    messages = [
        {
            "id": message.id,
            "author": message.author,
            "name": message.name,
            "email": message.email,
            "body": message.body,
            "timestamp": message.created_at.isoformat(),
        }
        for message in ticket.messages
    ]
    return {"ok": True, "messages": messages}


@app.post("/support/tickets/{ticket_id}/messages")
def create_ticket_message(
    ticket_id: int,
    payload: SupportTicketMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_ticket_for_user(db, ticket_id, current_user)

    message = TicketMessage(
        ticket_id=ticket_id,
        author="user",
        name=current_user.name,
        email=current_user.email,
        body=payload.body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "ok": True,
        "message": {
            "id": message.id,
            "author": message.author,
            "name": message.name,
            "email": message.email,
            "body": message.body,
            "timestamp": message.created_at.isoformat(),
        },
    }


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
