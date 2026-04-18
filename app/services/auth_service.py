from sqlalchemy.orm import Session
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario import UsuarioCreate
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:

    @staticmethod
    def encriptar_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        return pwd_context.verify(password_plano, password_hash)

    @staticmethod
    def crear_token(data: dict) -> str:
        payload = data.copy()
        expira  = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
        payload.update({"exp": expira})
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verificar_token(token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None

    @staticmethod
    def registrar_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
        
        existe = db.query(Usuario).filter(Usuario.email == datos.email).first()
        if existe:
            raise ValueError("El email ya está registrado")

        usuario = Usuario(
            nombre   = datos.nombre,
            email    = datos.email,
            telefono = datos.telefono,
            password = AuthService.encriptar_password(datos.password),
            rol      = datos.rol
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def login(db: Session, email: str, password: str) -> Usuario:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise ValueError("Credenciales incorrectas")
        if not AuthService.verificar_password(password, usuario.password):
            raise ValueError("Credenciales incorrectas")
        return usuario