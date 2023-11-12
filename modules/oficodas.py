from __future__ import annotations
import datetime

from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, ForeignKey, Integer, DateTime, func, Boolean, UniqueConstraint
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class OficodaId(BaseModel):
    id_oficoda: int

    class Config:
        from_attributes = True


class OficodaP(OficodaId):
    usuario: 'UsuarioE'
    oficina: 'OficinaE'
    fecha_creacion: datetime.datetime
    desac: bool


class OficodaU(OficodaId):
    id_usuario: int | None = None
    id_oficina: int | None = None
    fecha_creacion: datetime.datetime | None = None


class OficodaE(BaseModel):
    id_oficoda: int | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None


class OficodaR(BaseModel):
    id_oficoda: int | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None
    usuario: Optional['UsuarioE'] = None
    oficina: Optional['OficinaE'] = None


class OficodaC(BaseModel):
    usuario: 'UsuarioId'
    oficina: 'OficinaId'
    fecha_creacion: datetime.datetime


class OficodaOf(OficodaId):
    id_oficina: int
    oficina: 'OficinaE'


class OficodaUs(OficodaId):
    id_usuario: int
    usuario: 'UsuarioE'


# noinspection PyTypeChecker
class OficodaS(Base):
    __tablename__ = "oficodas"
    id_oficoda = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True,
                        nullable=False, index=True)
    usuario: Mapped['UsuarioS'] = relationship('UsuarioS', back_populates="oficodas")
    id_oficina = Column(Integer, ForeignKey('oficinas.id_oficina', ondelete='CASCADE'), primary_key=True,
                        nullable=False, index=True)
    oficina: Mapped['OficinaS'] = relationship('OficinaS', back_populates="oficodas")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    __table_args__ = (UniqueConstraint(id_oficina, id_usuario, name='u_oficina_usuario'),)


from .usuarios import UsuarioE, UsuarioS, UsuarioId
from .oficinas import OficinaE, OficinaS, OficinaId

OficodaP.model_rebuild()
OficodaR.model_rebuild()
OficodaU.model_rebuild()
OficodaC.model_rebuild()
OficodaOf.model_rebuild()
OficodaUs.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(OficodaS)
    if p:
        if p.id_oficoda:
            query = query.filter(OficodaS.id_oficoda == p.id_oficoda)
        if p.fecha_creacion:
            query = query.filter(OficodaS.fecha_creacion == p.fecha_creacion)
        if p.desac is not None:
            query = query.filter(OficodaS.desac == p.desac)
        if p.usuario:
            r = p.usuario
            query = query.join(UsuarioS, UsuarioS.id_usuario == OficodaS.id_usuario)
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
        if p.oficina:
            r = p.oficina
            query = query.join(OficinaS, OficodaS.id_oficina == OficinaS.id_oficina)
            if r.id_oficina:
                query = query.filter(OficinaS.id_oficina == r.id_oficina)
            if r.nombre:
                query = query.filter(OficinaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(OficinaS.direccion.ilike(f'%{r.direccion}%'))
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[OficodaP])
async def read_all(skip: int = 0, limit: int = 100, p: OficodaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=OficodaP)
async def read(p: OficodaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=OficodaP)
async def create(p: OficodaC, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficina == p.id_oficina,
                                      OficodaS.id_usuario == p.id_usuario)
    model = OficodaS(id_usuario=p.id_usuario, id_oficina=p.id_oficina)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=OficodaP)
async def update(up: OficodaU, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficoda == up.id_oficoda)
    return await forwards.update(up, query, ['id_oficoda'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=OficodaE)
async def delete(p: OficodaId, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficoda == p.id_oficoda)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=OficodaP)
async def activate(up: OficodaId, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficoda == up.id_oficoda)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/oficina", response_model=OficodaOf)
async def read_oficina(p: OficodaId, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficoda == p.id_oficoda)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/usuario", response_model=OficodaUs)
async def read_usuario(p: OficodaId, db: Session = Depends(get_db)):
    query = db.query(OficodaS).filter(OficodaS.id_oficoda == p.id_oficoda)
    return await forwards.read(query)
