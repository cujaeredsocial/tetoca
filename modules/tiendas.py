from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional
from service import forwards

router = APIRouter()


class TiendaId(BaseModel):
    id_tienda: int

    class Config:
        from_attributes = True


class TiendaP(TiendaId):
    nombre: str
    direccion: str | None
    frecuencia_venta: int
    desac: bool
    municipio: 'MunicipioE'
    cadena: 'CadenaE'
    bodegas: List['BodegaE'] | None
    resposables: List['ResponsableE'] | None


class TiendaU(TiendaId):
    nombre: str | None = None
    direccion: str | None = None
    frecuencia_venta: int | None = None
    id_municipio: int | None = None
    id_cadena: int | None = None


class TiendaE(BaseModel):
    id_tienda: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    frecuencia_venta: int | None = None
    desac: bool | None = None


class TiendaR(BaseModel):
    id_tienda: int | None = None
    nombre: str | None = None
    direccion: str | None = None
    frecuencia_venta: int | None = None
    desac: bool | None = None
    municipio: Optional['MunicipioE'] = None
    cadena: Optional['CadenaE'] = None
    bodega: Optional['BodegaE'] = None
    responsable: Optional['ResponsableE'] = None


class TiendaC(BaseModel):
    nombre: str = ''
    direccion: str = ''
    frecuencia_venta: int = 0
    municipio: 'MunicipioId'
    cadena: 'CadenaId'


class TiendaMu(TiendaId):
    nombre: str
    id_municipio: int
    municipio: 'MunicipioId'


class TiendaCa(TiendaId):
    nombre: str
    id_cadena: int
    cadena: 'CadenaId'


class TiendaBo(TiendaId):
    nombre: str
    municipio: 'MunicipioId'
    cadena: 'CadenaId'
    bodegas: List['BodegaE']


class TiendaRe(TiendaId):
    nombre: str
    municipio: 'MunicipioId'
    cadena: 'CadenaId'
    responsables: List['ResponsableE']


# noinspection PyTypeChecker
class TiendaS(Base):
    __tablename__ = "tiendas"
    id_tienda = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text, unique=False, nullable=False, index=True)
    direccion = Column(Text, unique=False, nullable=True, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    frecuencia_venta = Column(Integer, unique=False, nullable=False, index=True, default=0)
    id_municipio = Column(Integer, ForeignKey('municipios.id_municipio', ondelete='CASCADE'),
                          nullable=False, index=True)
    municipio: Mapped['MunicipioS'] = relationship('MunicipioS', back_populates="tiendas")
    id_cadena = Column(Integer, ForeignKey('cadenas.id_cadena', ondelete='CASCADE'),
                       nullable=False, index=True)
    cadena: Mapped['CadenaS'] = relationship('CadenaS', back_populates="tiendas")
    bodegas: Mapped[List['BodegaS']] = relationship(back_populates="tienda", cascade="all, delete")
    responsables: Mapped[List['ResponsableS']] = relationship(back_populates="tienda", cascade="all, delete")
    __table_args__ = (UniqueConstraint(nombre, id_municipio, id_cadena, name='nombre, id_municipio, id_cadena'),)


from .municipios import MunicipioId, MunicipioE, MunicipioS
from .cadenas import CadenaId, CadenaE, CadenaS
from .bodegas import BodegaS, BodegaE
from .responsables import ResponsableS, ResponsableE

TiendaC.model_rebuild()
TiendaR.model_rebuild()
TiendaU.model_rebuild()
TiendaP.model_rebuild()
TiendaRe.model_rebuild()
TiendaBo.model_rebuild()
TiendaMu.model_rebuild()
TiendaCa.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(TiendaS)
    if p:
        if p.id_tienda:
            query = query.filter(TiendaS.id_tienda == p.id_tienda)
        if p.nombre:
            query = query.filter(TiendaS.nombre.ilike(f'%{p.nombre}%'))
        if p.direccion:
            query = query.filter(TiendaS.direccion.ilike(f'%{p.direccion}%'))
        if p.frecuencia_venta:
            query = query.filter(TiendaS.frecuencia_venta == p.frecuencia_venta)
        if p.desac is not None:
            query = query.filter(TiendaS.desac == p.desac)
        if p.cadena:
            r = p.cadena
            query = query.join(CadenaS, CadenaS.id_cadena == TiendaS.id_cadena)
            if r.id_cadena:
                query = query.filter(CadenaS.id_cadena == r.id_cadena)
            if r.nombre:
                query = query.filter(CadenaS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(CadenaS.descripcion.ilike(f'%{r.descripcion}%'))
            if r.siglas:
                query = query.filter(CadenaS.siglas.ilike(f'%{r.siglas}%'))
        if p.municipio:
            r = p.municipio
            query = query.join(MunicipioS, MunicipioS.id_municipio == TiendaS.id_municipio)
            if r.id_municipio:
                query = query.filter(MunicipioS.id_municipio == r.id_municipio)
            if r.nombre:
                query = query.filter(MunicipioS.nombre.ilike(f'%{r.nombre}%'))
            if r.siglas:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.siglas}%'))
            if r.ubicacion:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.ubicacion}%'))
        if p.bodega:
            r = p.bodega
            query = query.join(BodegaS, BodegaS.id_tienda == TiendaS.id_tienda)
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
        if p.responsable:
            r = p.responsable
            query = query.join(ResponsableS, ResponsableS.id_tienda == TiendaS.id_tienda)
            if r.id_responsable:
                query = query.filter(ResponsableS.id_responsable == r.id_responsable)
            if r.fecha_creacion:
                query = query.filter(ResponsableS.fecha_creacion == r.fecha_creacion)
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[TiendaP])
async def read_all(skip: int = 0, limit: int = 100, p: TiendaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=TiendaP)
async def read(p: TiendaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=TiendaP)
async def create(p: TiendaC, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.nombre == p.nombre)
    query = query.filter(TiendaS.id_municipio == p.municipio.id_municipio)
    query = query.filter(TiendaS.id_cadena == p.cadena.id_cadena)
    model = TiendaS(nombre=p.nombre, direccion=p.direccion, frecuencia_venta=p.frecuencia_venta,
                    id_cadena=p.cadena.id_cadena, id_municipio=p.municipio.id_municipio)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=TiendaP)
async def update(up: TiendaU, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.update(up, query, ['id_tienda'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=TiendaE)
async def delete(p: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == p.id_tienda)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=TiendaP)
async def activate(up: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/municipio", response_model=TiendaMu)
async def read_municipio(up: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/cadena", response_model=TiendaCa)
async def read_cadena(up: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/bodegas", response_model=TiendaBo)
async def read_bodegas(up: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/responsables", response_model=TiendaRe)
async def read_responsables(up: TiendaId, db: Session = Depends(get_db)):
    query = db.query(TiendaS).filter(TiendaS.id_tienda == up.id_tienda)
    return await forwards.read(query)
