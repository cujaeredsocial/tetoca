from __future__ import annotations

import datetime

from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Session, relationship, Mapped
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class UsuarioId(BaseModel):
    id_usuario: int

    class Config:
        from_attributes = True


class UsuarioP(UsuarioId):
    nom_usuario: str | None
    num_cel: str | None
    ci: str
    nombre_completo: str | None
    dir_postal: str | None
    usuario_ws: str | None
    usuario_te: str | None
    usuario_to: str | None
    dir_correo: str | None
    fecha_creacion: datetime.datetime
    desac: bool
    rol: Optional['RolE'] = None
    responsables: List['ResponsableE'] | None
    consumidores: List['ConsumidorE'] | None
    oficodas: List['OficodaE'] | None
    compras: List['CompraE'] | None


class UsuarioU(UsuarioId):
    nom_usuario: str | None = None
    num_cel: str | None = None
    ci: str | None = None
    nombre_completo: str | None = None
    dir_postal: str | None = None
    usuario_ws: str | None = None
    usuario_te: str | None = None
    usuario_to: str | None = None
    dir_correo: str | None = None
    fecha_creacion: datetime.datetime | None = None
    id_rol: int | None = None


class UsuarioE(BaseModel):
    id_usuario: int | None = None
    nom_usuario: str | None = None
    num_cel: str | None = None
    ci: str | None = None
    nombre_completo: str | None = None
    dir_postal: str | None = None
    usuario_ws: str | None = None
    usuario_te: str | None = None
    usuario_to: str | None = None
    dir_correo: str | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None


class UsuarioR(BaseModel):
    id_usuario: int | None = None
    nom_usuario: str | None = None
    num_cel: str | None = None
    ci: str | None = None
    nombre_completo: str | None = None
    dir_postal: str | None = None
    usuario_ws: str | None = None
    usuario_te: str | None = None
    usuario_to: str | None = None
    dir_correo: str | None = None
    fecha_creacion: datetime.datetime | None = None
    desac: bool | None = None
    rol: Optional['RolE'] = None
    responsable: List['ResponsableE'] = None
    consumidor: List['ConsumidorE'] = None
    oficoda: List['OficodaE'] = None
    compra: List['CompraE'] = None


class UsuarioC(BaseModel):
    nom_usuario: str = ''
    num_cel: str = ''
    ci: str
    clave: str
    nombre_completo: str = ''
    dir_postal: str = ''
    usuario_ws: str = ''
    usuario_te: str = ''
    usuario_to: str = ''
    dir_correo: str = ''
    fecha_creacion: datetime.datetime
    rol: Optional['RolId'] = None


class UsuarioCMin(BaseModel):
    nom_usuario: str = ''
    num_cel: str = ''
    ci: str
    clave: str
    nombre_completo: str = ''
    dir_postal: str = ''
    usuario_ws: str = ''
    usuario_te: str = ''
    usuario_to: str = ''
    dir_correo: str = ''
    fecha_creacion: datetime.datetime
    rol: Optional['RolId'] = None


class UsuarioRo(UsuarioId):
    ci: str
    id_rol: int = None
    rol: Optional['RolE'] = None


class UsuarioRe(UsuarioId):
    ci: str
    responsables: List['ResponsableE']


class UsuarioCo(UsuarioId):
    ci: str
    consumidores: List['ConsumidorE']


class UsuarioOf(UsuarioId):
    ci: str
    oficodas: List['OficodaE']


class UsuarioCm(UsuarioId):
    ci: str
    compras: List['CompraE']


class UsuarioS(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nom_usuario = Column(String, unique=True, nullable=True, index=True)
    hash_clave = Column(String, nullable=False, index=False)
    num_cel = Column(String, unique=True, nullable=True, index=True)
    ci = Column(String, unique=True, nullable=False, index=True)
    nombre_completo = Column(String, nullable=True, index=True)
    dir_postal = Column(String, nullable=True, index=True)
    usuario_ws = Column(String, nullable=True, index=True)
    usuario_te = Column(String, nullable=True, index=True)
    usuario_to = Column(String, nullable=True, index=True)
    dir_correo = Column(String, nullable=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    desac = Column(Boolean, nullable=False, index=False, default=True)
    id_rol = Column(Integer, ForeignKey('roles.id_rol', ondelete="CASCADE"), nullable=True, index=True)
    rol: Mapped['RolS'] = relationship('RolS', back_populates="usuarios")
    responsables: Mapped[List['ResponsableS']] = relationship(back_populates="usuario", cascade="all, delete")
    consumidores: Mapped[List['ConsumidorS']] = relationship(back_populates="usuario", cascade="all, delete")
    oficodas: Mapped[List['OficodaS']] = relationship(back_populates="usuario", cascade="all, delete")
    compras: Mapped[List['CompraS']] = relationship(back_populates="usuario", cascade="all, delete")


from .roles import RolS, RolId, RolE
from .oficodas import OficodaS, OficodaE
from .consumidores import ConsumidorS, ConsumidorE
from .responsables import ResponsableS, ResponsableE
from .compras import CompraS, CompraE

UsuarioP.model_rebuild()
UsuarioR.model_rebuild()
UsuarioU.model_rebuild()
UsuarioC.model_rebuild()
UsuarioRo.model_rebuild()
UsuarioRe.model_rebuild()
UsuarioCo.model_rebuild()
UsuarioOf.model_rebuild()
UsuarioCm.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(UsuarioS)
    if p:
        if p.id_usuario:
            query = query.filter(UsuarioS.id_usuario == p.id_usuario)
        if p.nom_usuario:
            query = query.filter(UsuarioS.nom_usuario.ilike(f'%{p.nom_usuario}%'))
        if p.num_cel:
            query = query.filter(UsuarioS.num_cel.ilike(f'%{p.num_cel}%'))
        if p.ci:
            query = query.filter(UsuarioS.ci.ilike(f'%{p.ci}%'))
        if p.nombre_completo:
            query = query.filter(UsuarioS.nombre_completo.ilike(f'%{p.nombre_completo}%'))
        if p.dir_postal:
            query = query.filter(UsuarioS.dir_postal.ilike(f'%{p.dir_postal}%'))
        if p.usuario_ws:
            query = query.filter(UsuarioS.usuario_wa.ilike(f'%{p.usuario_wa}%'))
        if p.usuario_te:
            query = query.filter(UsuarioS.usuario_te.ilike(f'%{p.usuario_te}%'))
        if p.usuario_to:
            query = query.filter(UsuarioS.usuario_to.ilike(f'%{p.usuario_to}%'))
        if p.dir_correo:
            query = query.filter(UsuarioS.dir_correo.ilike(f'%{p.dir_correo}%'))
        if p.fecha_creacion:
            query = query.filter(UsuarioS.fecha_creacion == p.fecha_creacion)
        if p.desac is not None:
            query = query.filter(UsuarioS.desac == p.desac)
        if p.rol:
            r = p.rol
            query = query.join(RolS, UsuarioS.id_rol == RolS.id_rol)
            if r.id_rol:
                query = query.filter(RolS.id_rol == r.id_rol)
            if r.nombre:
                query = query.filter(RolS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(RolS.descripcion.ilike(f'%{r.descripcion}%'))
        if p.responsable:
            r = p.responsable
            query = query.join(ResponsableS, UsuarioS.id_usuario == ResponsableS.id_usuario)
            if r.id_responsable:
                query = query.filter(ResponsableS.id_responsable == r.id_responsable)
            if r.fecha_creacion:
                query = query.filter(ResponsableS.fecha_creacion == r.fecha_creacion)
        if p.consumidor:
            r = p.consumidor
            query = query.join(ConsumidorS, UsuarioS.id_usuario == ConsumidorS.id_usuario)
            if r.id_consumidor:
                query = query.filter(ConsumidorS.id_consumidor == r.id_consumidor)
            if r.verificado:
                query = query.filter(ConsumidorS.verificado == r.verificado)
            if r.fecha_creacion:
                query = query.filter(ConsumidorS.fecha_creacion == r.fecha_creacion)
        if p.oficoda:
            r = p.oficoda
            query = query.join(OficodaS, UsuarioS.id_usuario == OficodaS.id_usuario)
            if r.id_oficoda:
                query = query.filter(OficodaS.id_oficoda == r.id_oficoda)
            if r.fecha_creacion:
                query = query.filter(OficodaS.fecha_creacion == r.fecha_creacion)
        if p.compra:
            r = p.compras
            query = query.join(CompraS, UsuarioS.id_usuario == CompraS.id_usuario)
            if r.id_compra:
                query = query.filter(CompraS.id_compra == r.id_compra)
            if r.fecha:
                query = query.filter(CompraS.fecha == r.fecha)
            if r.terminado:
                query = query.filter(CompraS.terminado == r.terminado)
            if r.pagado:
                query = query.filter(CompraS.pagado == r.pagado)
            if r.seleccion:
                query = query.filter(CompraS.seleccion.ilike(f'%{r.seleccion}%'))
    return query


# noinspection PyTypeChecker
@router.post("/all", response_model=List[UsuarioP])
async def read_all(skip: int = 0, limit: int = 100, p: UsuarioR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=UsuarioP)
async def read(p: UsuarioR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=UsuarioP)
async def create(p: UsuarioC, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(
        (UsuarioS.ci == p.ci) | (UsuarioS.nom_usuario == p.nom_usuario) | (UsuarioS.num_cel == p.num_cel))

    model = UsuarioS(nom_usuario=p.nom_usuario, hash_clave=p.clave, num_cel=p.num_cel, ci=p.ci,
                     nombre_completo=p.nombre_completo, dir_postal=p.dir_postal, usuario_ws=p.usuario_ws,
                     usuario_te=p.usuario_te, usuario_to=p.usuario_to, dir_correo=p.dir_correo,
                     fecha_creacion=p.fecha_creacion, id_rol=p.id_rol)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=UsuarioP)
async def update(up: UsuarioU, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == up.id_usuario)
    return await forwards.update(up, query, ['id_usuario'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=UsuarioE)
async def delete(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=UsuarioP)
async def activate(up: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == up.id_usuario)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.post("/rol", response_model=UsuarioRo)
async def read_rol(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/responsables", response_model=UsuarioRe)
async def read_responsables(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/consumidores", response_model=UsuarioCo)
async def read_consumidores(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/oficodas", response_model=UsuarioOf)
async def read_oficodas(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/compras", response_model=UsuarioCm)
async def read_compras(p: UsuarioId, db: Session = Depends(get_db)):
    query = db.query(UsuarioS).filter(UsuarioS.id_usuario == p.id_usuario)
    return await forwards.read(query)
