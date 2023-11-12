from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from .usuarios import UsuarioS, UsuarioP, UsuarioE
from .nucleos import NucleoId, NucleoS

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


# noinspection PyTypeChecker
async def _get_user(i: str, db: Session):
    return db.query(UsuarioS).filter((UsuarioS.ci == i) | (UsuarioS.id_usuario == i) | (UsuarioS.num_cel == i)).first()


async def get_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                             headers={"WWW-Authenticate": "Bearer"}, )
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        username = payload.get("user")
        if not username:
            raise cred_exc
    except JWTError:
        raise cred_exc
    else:
        user = await _get_user(username, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"})
        elif user.desac:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")
    return user


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token, summary="Autenticar por Token", response_description="Crear Token", )
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    user = await _get_user(form_data.username, db)
    if not user or not await _verify_password(form_data.password, user.hash_clave):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    elif user.desac:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")
    expires_delta = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    to_encode = {"user": str(user.id_usuario), "exp": datetime.utcnow() + expires_delta}
    access_token = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/perfil", response_model=UsuarioE)
async def read_users_me(current_user: Annotated[UsuarioP, Depends(get_user)]):
    return current_user


class UserCons(BaseModel):
    num_cel: str
    ci: str
    clave: str
    nucleo: str


# noinspection PyTypeChecker

@router.post("/registro", response_model=Token)
async def create_users(p: UserCons, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter((UsuarioS.ci == p.ci) | (UsuarioS.num_cel == p.num_cel))

    usuario = query.first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este carnet de identidad no existe")

    if not usuario.desac:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este usuario ya existe")

    if usuario.ci != p.ci or usuario.num_cel != usuario.num_cel:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No coincide móvil con carnet")

    nucleo = db.query(NucleoS).filter(NucleoS.id_nucleo == p.nucleo).first()

    if not nucleo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Núcleo no existe")

    # Revisa si hay coincidencia de consumidor entre la persona que tiene el carnet de identidad y el nucleo
    if not len(set([i.id_consumidor for i in usuario.consumidores]) &
               set([i.id_consumidor for i in nucleo.consumidores])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existes en ese núcleo")
    else:
        query_aux = {'desac': False, 'num_cel': p.num_cel, 'hash_clave': await get_password_hash(p.ci)}
        try:
            query.update(query_aux)
            db.commit()
        except (Exception,):
            raise HTTPException(status_code=400, detail="No se pudo hacer el registro")
        else:
            expires_delta = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
            to_encode = {"user": str(usuario.id_usuario), "exp": datetime.utcnow() + expires_delta}
            access_token = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
            return {"access_token": access_token, "token_type": "bearer"}



"""
# noinspection PyTypeChecker
@router.post("/activate", response_model=UsuarioP)
async def for_activate(p: TokenData, current_user: Annotated[UsuarioE, Depends(get_current_active_user)],
                       db: Session = Depends(get_db)):
    aux = db.query(UsuarioS).filter(UsuarioS.nom_usuario == p.nom_usuario)
    new_aux = aux.first()
    if not new_aux:
        raise HTTPException(status_code=400, detail="Is Not Exists")
    up_aux = {'id_usuario': new_aux.id_usuario, 'disabled': not new_aux.disabled}
    aux.update(up_aux)
    db.commit()
    db.refresh(new_aux)
    return new_aux


@router.get("/all_user", response_model=List[UsuarioP])
def read_all(current_user: Annotated[UsuarioE, Depends(get_user)],
             skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    aux = db.query(UsuarioS).offset(skip).limit(limit).all()
    return aux


"""