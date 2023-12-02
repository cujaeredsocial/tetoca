from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class OficinaId(BaseModel):
    id_oficina: int

    class Config:
        from_attributes = True


class OficinaP(OficinaId):
    nombre: str
    direccion: str | None
    desac: bool
    municipio: 'MunicipioE'
    bodegas: List['BodegaE'] | None
    oficodas: List['OficodaE'] | None


class OficinaU(OficinaId):
    nombre: str | None = None
    direccion: str | None = None
    id_municipio: int | None = None


class OficinaE(BaseModel):
    id_oficina: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    desac: bool | None = None
    municipio: Optional['MunicipioE'] = None


class OficinaR(BaseModel):
    id_oficina: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    desac: bool | None = None
    municipio: Optional['MunicipioE'] = None
    bodega: Optional['BodegaE'] = None
    oficoda: Optional['OficodaE'] = None


class OficinaC(BaseModel):
    nombre: str
    direccion: str = ''
    municipio: 'MunicipioId'


class OficinaBo(OficinaId):
    nombre: str
    municipio: 'MunicipioE'
    bodegas: List['BodegaE']


class OficinaOf(OficinaId):
    nombre: str
    municipio: 'MunicipioE'
    oficodas: List['OficodaE']


class OficinaMu(OficinaId):
    nombre: str
    id_municipio: int
    municipio: 'MunicipioE'


# noinspection PyTypeChecker
class OficinaS(Base):
    __tablename__ = "oficinas"
    id_oficina = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=False, nullable=False, index=True)
    direccion = Column(String, unique=False, nullable=False, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_municipio = Column(Integer, ForeignKey('municipios.id_municipio', ondelete='CASCADE'),
                          nullable=False, index=True)
    municipio: Mapped['MunicipioS'] = relationship('MunicipioS', back_populates="oficinas")
    bodegas: Mapped[List['BodegaS']] = relationship(back_populates="oficina", cascade="all, delete")
    oficodas: Mapped[List['OficodaS']] = relationship(back_populates="oficina", cascade="all, delete")
    __table_args__ = (UniqueConstraint(nombre, id_municipio, name='u_nombre_municipio'),)


from .municipios import MunicipioId, MunicipioS, MunicipioE
from .bodegas import BodegaS, BodegaE
from .oficodas import OficodaS, OficodaE

OficinaP.model_rebuild()
OficinaR.model_rebuild()
OficinaC.model_rebuild()
OficinaU.model_rebuild()
OficinaBo.model_rebuild()
OficinaOf.model_rebuild()
OficinaMu.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(OficinaS)
    if p:
        if p.id_oficina:
            query = query.filter(OficinaS.id_oficina == p.id_oficina)
        if p.nombre:
            query = query.filter(OficinaS.nombre.ilike(f'%{p.nombre}%'))
        if p.direccion:
            query = query.filter(OficinaS.direccion.ilike(f'%{p.direccion}%'))
        if p.desac is not None:
            query = query.filter(OficinaS.desac == p.desac)
        if p.municipio:
            r = p.municipio
            query = query.join(MunicipioS, MunicipioS.id_municipio == OficinaS.id_municipio)
            if r.id_municipio:
                query = query.filter(MunicipioS.id_municipio == r.id_municipio)
            if r.nombre:
                query = query.filter(MunicipioS.nombre.ilike(f'%{r.nombre}%'))
            if r.siglas:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.siglas}%'))
            if r.ubicacion:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.ubicacion}%'))
        if p.oficoda:
            r = p.oficoda
            query = query.join(OficodaS, OficodaS.id_oficina == OficinaS.id_oficina)
            if r.id_oficoda:
                query = query.filter(OficodaS.id_oficoda == r.id_oficoda)
            if r.fecha_creacion:
                query = query.filter(OficodaS.fecha_creacion == r.fecha_creacion)
        if p.bodega:
            r = p.bodega
            query = query.join(BodegaS, BodegaS.id_oficina == OficinaS.id_oficina)
            if r.id_bodega:
                query = query.filter(BodegaS.id_bodega == r.id_bodega)
            if r.numero:
                query = query.filter(BodegaS.numero.ilike(f'%{r.numero}%'))
            if r.direccion:
                query = query.filter(BodegaS.direccion.ilike(f'%{r.direccion}%'))
            if r.grupos_rs:
                query = query.filter(BodegaS.grupos_rs.ilike(f'%{r.grupos_rs}%'))
            if r.es_especial:
                query = query.filter(BodegaS.es_especial == r.es_especial)
    return query


# noinspection PyTypeChecker
@router.post("/all", response_model=List[OficinaP])
async def read_all(skip: int = 0, limit: int = 100, p: OficinaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=OficinaP)
async def read(p: OficinaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=OficinaP)
async def create(p: OficinaC, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.nombre == p.nombre)
    query = query.filter(OficinaS.id_municipio == p.municipio.id_municipio)
    model = OficinaS(nombre=p.nombre, id_municipio=p.id_municipio, direccion=p.direccion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=OficinaP)
async def update(up: OficinaU, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == up.id_oficina)
    return await forwards.update(up, query, ['id_oficina'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=OficinaE)
async def delete(p: OficinaId, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == p.id_oficina)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=OficinaP)
async def activate(up: OficinaId, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == up.id_oficina)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.post("/bodegas", response_model=OficinaBo)
async def read_bodegas(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == p.id_oficina)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/oficodas", response_model=OficinaOf)
async def read_oficodas(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == p.id_oficina)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/municipio", response_model=OficinaMu)
async def read_municipio(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(OficinaS).filter(OficinaS.id_oficina == p.id_oficina)
    return await forwards.read(query)
