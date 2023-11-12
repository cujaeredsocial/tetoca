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


class ResponsableId(BaseModel):
    id_responsable: int

    class Config:
        from_attributes = True


class ResponsableP(ResponsableId):
    usuario: 'UsuarioE'
    tienda: 'TiendaE'
    fecha_creacion: datetime.datetime
    desac: bool


class ResponsableU(ResponsableId):
    id_usuario: int | None = None
    id_tienda: int | None = None
    fecha_creacion: datetime.datetime | None = None


class ResponsableE(BaseModel):
    id_responsable: int | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None


class ResponsableR(BaseModel):
    id_responsable: int | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None
    usuario: Optional['UsuarioE'] = None
    tienda: Optional['TiendaE'] = None


class ResponsableC(BaseModel):
    usuario: 'UsuarioId'
    tienda: 'TiendaId'
    fecha_creacion: datetime.datetime


class ResponsableTi(ResponsableId):
    id_tienda: int
    tienda: 'TiendaE'


class ResponsableUs(ResponsableId):
    id_usuario: int
    usuario: 'UsuarioE'


class ResponsableS(Base):
    __tablename__ = "responsables"
    id_responsable = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True,
                        nullable=False, index=True)
    usuario: Mapped['UsuarioS'] = relationship('UsuarioS', back_populates="responsables")
    id_tienda = Column(Integer, ForeignKey('tiendas.id_tienda', ondelete='CASCADE'), primary_key=True,
                       nullable=False, index=True)
    tienda: Mapped['TiendaS'] = relationship('TiendaS', back_populates="responsables")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    __table_args__ = (UniqueConstraint(id_tienda, id_usuario, name='u_tienda_usuario'),)


from .usuarios import UsuarioE, UsuarioS, UsuarioId
from .tiendas import TiendaE, TiendaS, TiendaId

ResponsableP.model_rebuild()
ResponsableR.model_rebuild()
ResponsableU.model_rebuild()
ResponsableC.model_rebuild()
ResponsableTi.model_rebuild()
ResponsableUs.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(ResponsableS)
    if p:
        if p.id_responsable:
            query = query.filter(ResponsableS.id_responsable == p.id_responsable)
        if p.fecha_creacion:
            query = query.filter(ResponsableS.fecha_creacion == p.fecha_creacion)
        if p.desac is not None:
            query = query.filter(ResponsableS.desac == p.desac)
        if p.usuario:
            r = p.usuario
            query = query.join(UsuarioS, UsuarioS.id_usuario == ResponsableS.id_usuario)
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
        if p.tienda:
            r = p.tienda
            query = query.join(TiendaS, ResponsableS.id_tienda == TiendaS.id_tienda)
            if r.id_tienda:
                query = query.filter(TiendaS.id_tienda == r.id_tienda)
            if r.nombre:
                query = query.filter(TiendaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(TiendaS.direccion.ilike(f'%{r.direccion}%'))
            if r.frecuencia_venta:
                query = query.filter(TiendaS.frecuencia_venta == r.frecuencia_venta)
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[ResponsableP])
async def read_all(skip: int = 0, limit: int = 100, p: ResponsableR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=ResponsableP)
async def read(p: ResponsableR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=ResponsableP)
async def create(p: ResponsableC, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_tienda == p.id_tienda,
                                          ResponsableS.id_usuario == p.id_usuario)
    model = ResponsableS(id_usuario=p.id_usuario, id_tienda=p.id_tienda)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=ResponsableP)
async def update(up: ResponsableU, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_responsable == up.id_responsable)
    return await forwards.update(up, query, ['id_responsable'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=ResponsableE)
async def delete(p: ResponsableId, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_responsable == p.id_responsable)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=ResponsableP)
async def activate(up: ResponsableId, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_responsable == up.id_responsable)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/tienda", response_model=ResponsableTi)
async def read_tienda(p: ResponsableId, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_responsable == p.id_responsable)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/usuario", response_model=ResponsableUs)
async def read_usuario(p: ResponsableId, db: Session = Depends(get_db)):
    query = db.query(ResponsableS).filter(ResponsableS.id_responsable == p.id_responsable)
    return await forwards.read(query)
