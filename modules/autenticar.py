from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from .usuarios import UsuarioS, UsuarioP, UsuarioE
from .nucleos import NucleoS

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

usuarios_activos = list()
usuarios_desacti = list()


async def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


# noinspection PyTypeChecker
async def _get_user(i: str, db: Session):
    return db.query(UsuarioS).filter((UsuarioS.ci == i) | (UsuarioS.num_cel == i)).first()


# noinspection PyTypeChecker
async def _get_user_id(i: str, db: Session):
    return db.query(UsuarioS).filter((UsuarioS.id_usuario == i)).first()


# noinspection PyTypeChecker
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
        user = await _get_user_id(username, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"})
        if user.desac and user.id_usuario not in usuarios_desacti:
            usuarios_desacti.append(user.id_usuario)
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")
        if user.id_usuario in usuarios_desacti:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")
    return user


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token, summary="Autenticar por Token", response_description="Crear Token", )
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(get_db)):
    user = await _get_user(form_data.username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    elif user.desac:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")
    elif not await _verify_password(form_data.password, user.hash_clave):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    expires_delta = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    to_encode = {"user": str(user.id_usuario), "exp": datetime.utcnow() + expires_delta}
    access_token = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    if user.id_usuario not in usuarios_activos:
        usuarios_activos.append(user.id_usuario)
    if user.id_usuario in usuarios_desacti:
        usuarios_desacti.remove(user.id_usuario)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/perfil", response_model=UsuarioE)
async def perfil(current_user: Annotated[UsuarioP, Depends(get_user)]):
    return current_user


class UserCom(BaseModel):
    num_cel: str
    ci: str
    nucleo: str


class UserComCon(UserCom):
    clave: str


# noinspection PyTypeChecker
@router.post("/registro", response_model=Token)
async def registro(p: UserComCon, db: Session = Depends(get_db)):
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
        query_aux = {'desac': False, 'num_cel': p.num_cel, 'hash_clave': await get_password_hash(p.clave)}
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


# noinspection PyTypeChecker
@router.post("/compaginar", response_model=bool)
async def compagina(p: UserCom, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.ci == p.ci).filter(UsuarioS.num_cel == p.num_cel)
    usuario = query.first()
    if usuario:
        for cons in usuario.consumidores:
            if str(cons.id_nucleo) == p.nucleo:
                return {'option': True}
    return {'option': False}


# noinspection PyTypeChecker
@router.post("/recuperar", response_model=bool)
async def recuperar(p: UserComCon, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.ci == p.ci).filter(UsuarioS.num_cel == p.num_cel)
    usuario = query.first()
    for cons in usuario.consumidores:
        if str(cons.id_nucleo) == p.nucleo:
            query_aux = {'hash_clave': await get_password_hash(p.clave)}
            try:
                query.update(query_aux)
                db.commit()
            except (Exception,):
                raise HTTPException(status_code=400, detail="No se pudo hacer el cambio de contraseña")
            else:
                return {'option': True}
    return {'option': False}


# noinspection PyTypeChecker
@router.post("/logout", status_code=status.HTTP_200_OK)
async def perfil(user: Annotated[UsuarioP, Depends(get_user)]):
    if user.id_usuario in usuarios_activos:
        usuarios_activos.remove(user.id_usuario)
    if user.id_usuario not in usuarios_desacti:
        usuarios_desacti.append(user.id_usuario)
    return {'option': True}


class Notificar(BaseModel):
    usuario_id: str
    oferta: dict | None = None
    compra: dict | None = None


# noinspection PyTypeChecker
@router.post("/notificar", status_code=status.HTTP_200_OK)
async def create(notificar: Notificar):
    print(notificar.model_dump_json())
    return {'option': True}
