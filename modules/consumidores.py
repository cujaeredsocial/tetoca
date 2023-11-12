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


class ConsumidorId(BaseModel):
    id_consumidor: int

    class Config:
        from_attributes = True


class ConsumidorP(ConsumidorId):
    usuario: 'UsuarioE'
    nucleo: 'NucleoE'
    verificado: bool
    fecha_creacion: datetime.datetime
    desac: bool


class ConsumidorU(ConsumidorId):
    id_usuario: int | None = None
    id_nucleo: int | None = None
    verificado: bool | None = None
    fecha_creacion: datetime.datetime | None = None


class ConsumidorE(BaseModel):
    id_consumidor: int | None = None
    verificado: bool | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None


class ConsumidorR(BaseModel):
    id_consumidor: int | None = None
    verificado: bool | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None
    usuario: Optional['UsuarioE'] = None
    nucleo: Optional['NucleoE'] = None


class ConsumidorC(BaseModel):
    usuario: 'UsuarioId'
    nucleo: 'NucleoId'
    verificado: bool | None = None
    fecha_creacion: datetime.datetime


class ConsumidorNu(ConsumidorId):
    id_nucleo: int
    nucleo: 'NucleoE'


class ConsumidorUs(ConsumidorId):
    id_usuario: int
    usuario: 'UsuarioE'


# REVISAR EL TEMA DEL JEFE, VER CUANTOS NUCLOES ESTE CONSUMIDOR ESTA
# noinspection PyTypeChecker
class ConsumidorS(Base):
    __tablename__ = "consumidores"
    id_consumidor = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False, index=True)
    usuario: Mapped['UsuarioS'] = relationship('UsuarioS', back_populates="consumidores")
    id_nucleo = Column(Integer, ForeignKey('nucleos.id_nucleo', ondelete='CASCADE'), nullable=False, index=True)
    nucleo: Mapped['NucleoS'] = relationship('NucleoS', back_populates="consumidores")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    verificado = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    __table_args__ = (UniqueConstraint(id_usuario, id_nucleo, name='u_nucleo_usuario'),)


from .usuarios import UsuarioE, UsuarioS, UsuarioId
from .nucleos import NucleoE, NucleoS, NucleoId

ConsumidorP.model_rebuild()
ConsumidorR.model_rebuild()
ConsumidorU.model_rebuild()
ConsumidorC.model_rebuild()
ConsumidorNu.model_rebuild()
ConsumidorUs.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(ConsumidorS)
    if p:
        if p.id_consumidor:
            query = query.filter(ConsumidorS.id_consumidor == p.id_consumidor)
        if p.verificado is not None:
            query = query.filter(ConsumidorS.verificado == p.verificado)
        if p.fecha_creacion:
            query = query.filter(ConsumidorS.fecha_creacion == p.fecha_creacion)
        if p.desac is not None:
            query = query.filter(ConsumidorS.desac == p.desac)
        if p.usuario:
            r = p.usuario
            query = query.join(UsuarioS, UsuarioS.id_usuario == ConsumidorS.id_usuario)
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
        if p.nucleo:
            r = p.nucleo
            query = query.join(NucleoS, ConsumidorS.id_nucleo == NucleoS.id_nucleo)
            if r.id_nucleo:
                query = query.filter(NucleoS.id_nucleo == r.id_nucleo)
            if r.numero:
                query = query.filter(NucleoS.numero.ilike(f'%{r.numero}%'))
            if r.cant_miembros:
                query = query.filter(NucleoS.cant_miembros == r.cant_miembros)
            if r.cant_modulos:
                query = query.filter(NucleoS.cant_modulos == r.cant_modulos)
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[ConsumidorP])
async def read_all(skip: int = 0, limit: int = 100, p: ConsumidorR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=ConsumidorP)
async def read(p: ConsumidorR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=ConsumidorP)
async def create(p: ConsumidorC, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_nucleo == p.id_nucleo,
                                          ConsumidorS.id_usuario == p.id_usuario)
    model = ConsumidorS(id_usuario=p.id_usuario, id_nucleo=p.id_nucleo)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=ConsumidorP)
async def update(up: ConsumidorU, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_consumidor == up.id_consumidor)
    return await forwards.update(up, query, ['id_consumidor'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=ConsumidorE)
async def delete(p: ConsumidorId, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_consumidor == p.id_consumidor)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=ConsumidorP)
async def activate(up: ConsumidorId, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_consumidor == up.id_consumidor)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/nucleo", response_model=ConsumidorNu)
async def read_nucleo(p: ConsumidorId, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_consumidor == p.id_consumidor)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/usuario", response_model=ConsumidorUs)
async def read_usuario(p: ConsumidorId, db: Session = Depends(get_db)):
    query = db.query(ConsumidorS).filter(ConsumidorS.id_consumidor == p.id_consumidor)
    return await forwards.read(query)
