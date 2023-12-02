from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class RolId(BaseModel):
    id_rol: int

    class Config:
        from_attributes = True


class RolP(RolId):
    nombre: str
    descripcion: str | None
    usuarios: List['UsuarioE'] | None


class RolU(RolId):
    nombre: str | None = None
    descripcion: str | None = None


class RolE(BaseModel):
    id_rol: int | None = None
    nombre: str | None = None
    descripcion: str | None = None


class RolR(BaseModel):
    id_rol: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    usuario: Optional['UsuarioE'] | None


class RolC(BaseModel):
    nombre: str
    descripcion: str = ''


class RolCo(RolId):
    nombre: str
    usuarios: List['UsuarioE']


class RolS(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    usuarios: Mapped[List['UsuarioS']] = relationship(back_populates="rol", cascade="all, delete")


from .usuarios import UsuarioS, UsuarioE

RolP.model_rebuild()
RolR.model_rebuild()
RolU.model_rebuild()
RolC.model_rebuild()
RolCo.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(RolS)
    if p:
        if p.id_rol:
            query = query.filter(RolS.id_rol == p.id_rol)
        if p.nombre:
            query = query.filter(RolS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(RolS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.usuario:
            r = p.usuario
            query = query.join(UsuarioS, UsuarioS.id_rol == RolS.id_rol)
            if r.id_usuario:
                query = query.filter(UsuarioS.id_usuario == r.id_usuario)
            if r.nom_usuario:
                query = query.filter(UsuarioS.nom_usuario.ilike(f'%{r.nom_usuario}%'))
            if r.num_cel:
                query = query.filter(UsuarioS.num_cel.ilike(f'%{r.num_cel}%'))
            if r.ci:
                query = query.filter(UsuarioS.ci.ilike(f'%{r.ci}%'))
            if r.nombre_completo:
                query = query.filter(UsuarioS.nombre_completo.ilike(f'%{r.nombre_completo}%'))
            if r.dir_postal:
                query = query.filter(UsuarioS.dir_postal.ilike(f'%{r.dir_postal}%'))
            if r.usuario_ws:
                query = query.filter(UsuarioS.usuario_wa.ilike(f'%{r.usuario_wa}%'))
            if r.usuario_te:
                query = query.filter(UsuarioS.usuario_te.ilike(f'%{r.usuario_te}%'))
            if r.usuario_to:
                query = query.filter(UsuarioS.usuario_to.ilike(f'%{r.usuario_to}%'))
            if r.dir_correo:
                query = query.filter(UsuarioS.dir_correo.ilike(f'%{r.dir_correo}%'))
            if r.fecha_creacion:
                query = query.filter(UsuarioS.fecha_creacion == r.fecha_creacion)
    return query


# noinspection PyTypeChecker
@router.post("/all", response_model=List[RolP])
async def read_all(skip: int = 0, limit: int = 100, p: RolR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=RolP)
async def read(p: RolR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=RolP)
async def create(p: RolC, db: Session = Depends(get_db)):
    query = db.query(RolS).filter(RolS.nombre == p.nombre)
    model = RolS(nombre=p.nombre, descripcion=p.descripcion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=RolP)
async def update(up: RolU, db: Session = Depends(get_db)):
    query = db.query(RolS).filter(RolS.id_rol == up.id_rol)
    return await forwards.update(up, query, ['id_rol'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=RolE)
async def delete(p: RolId, db: Session = Depends(get_db)):
    query = db.query(RolS).filter(RolS.id_rol == p.id_rol)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.post("/usuarios", response_model=RolCo)
async def read_usuarios(p: RolId, db: Session = Depends(get_db)):
    query = db.query(RolS).filter(RolS.id_rol == p.id_rol)
    return await forwards.read(query)
