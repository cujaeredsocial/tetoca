from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import Session, relationship, Mapped
from fastapi import Depends, APIRouter
from typing import List, Optional, Annotated

from service import forwards

router = APIRouter()


class BodegaId(BaseModel):
    id_bodega: int

    class Config:
        from_attributes = True


class BodegaP(BodegaId):
    numero: str
    direccion: str | None
    grupos_rs: str | None
    es_especial: bool
    desac: bool
    oficina: 'OficinaE'
    tienda: 'TiendaE'
    nucleos: List['NucleoE'] | None


class BodegaU(BodegaId):
    numero: str | None = None
    direccion: str | None = None
    grupos_rs: str | None = None
    es_especial: bool | None = None
    id_oficina: int | None = None
    id_tienda: int | None = None


class BodegaE(BaseModel):
    id_bodega: int | None = None
    numero: str | None = None
    direccion: str | None = None
    grupos_rs: str | None = None
    es_especial: bool | None = None
    desac: bool | None = None


class BodegaR(BaseModel):
    id_bodega: int | None = None
    numero: str | None = None
    direccion: str | None = None
    grupos_rs: str | None = None
    es_especial: bool | None = None
    desac: bool | None = None
    oficina: Optional['OficinaE'] = None
    tienda: Optional['TiendaE'] = None
    nucleo: Optional['NucleoE'] = None


class BodegaC(BaseModel):
    numero: str
    direccion: str = ''
    grupos_rs: str = ''
    es_especial: bool = False
    oficina: 'OficinaId'
    tienda: 'TiendaId'


class BodegaTi(BodegaId):
    numero: str
    id_tienda: int
    tienda: 'TiendaE'


class BodegaOf(BodegaId):
    numero: str
    id_oficina: int
    oficina: 'OficinaE'


class BodegaNu(BodegaId):
    numero: str
    oficina: 'OficinaE'
    tienda: 'TiendaE'
    nucleos: List['NucleoE']


class BodegaS(Base):
    __tablename__ = "bodegas"
    id_bodega = Column(Integer, primary_key=True, index=True)
    numero = Column(String, nullable=False, index=True)
    direccion = Column(String, nullable=True, index=True)
    grupos_rs = Column(String, nullable=True, index=False)
    es_especial = Column(Boolean, nullable=False, index=True, default=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_tienda = Column(Integer, ForeignKey('tiendas.id_tienda', ondelete='CASCADE'), nullable=True, index=True)
    tienda: Mapped['TiendaS'] = relationship('TiendaS', back_populates="bodegas")
    id_oficina = Column(ForeignKey('oficinas.id_oficina', ondelete='CASCADE'), nullable=False, index=True)
    oficina: Mapped['OficinaS'] = relationship('OficinaS', back_populates="bodegas")
    nucleos: Mapped[List['NucleoS']] = relationship(back_populates="bodega", cascade="all, delete")
    __table_args__ = (UniqueConstraint(numero, id_oficina, name='u_nombre_oficina'),
                      #UniqueConstraint(numero, tienda, name='u_nombre_tienda')
                      )


from .oficinas import OficinaE, OficinaId, OficinaS
from .tiendas import TiendaE, TiendaId, TiendaS
from .nucleos import NucleoE, NucleoS

BodegaC.model_rebuild()
BodegaU.model_rebuild()
BodegaP.model_rebuild()
BodegaR.model_rebuild()
BodegaTi.model_rebuild()
BodegaOf.model_rebuild()
BodegaNu.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(BodegaS)
    if p:
        if p.id_bodega:
            query = query.filter(BodegaS.id_bodega == p.id_bodega)
        if p.numero:
            query = query.filter(BodegaS.numero.ilike(f'%{p.numero}%'))
        if p.direccion:
            query = query.filter(BodegaS.direccion.ilike(f'%{p.direccion}%'))
        if p.grupos_rs:
            query = query.filter(BodegaS.grupos_rs.ilike(f'%{p.grupos_rs}%'))
        if p.es_especial is not None:
            query = query.filter(BodegaS.es_especial == p.es_especial)
        if p.desac is not None:
            query = query.filter(BodegaS.desac == p.desac)
        if p.oficina:
            r = p.oficina
            query = query.join(OficinaS, BodegaS.id_oficina == OficinaS.id_oficina)
            if r.id_oficina:
                query = query.filter(OficinaS.id_oficina == r.id_oficina)
            if r.nombre:
                query = query.filter(OficinaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(OficinaS.direccion.ilike(f'%{r.direccion}%'))
        if p.tienda:
            r = p.tienda
            query = query.join(TiendaS, BodegaS.id_tienda == TiendaS.id_tienda)
            if r.id_tienda:
                query = query.filter(TiendaS.id_tienda == r.id_tienda)
            if r.nombre:
                query = query.filter(TiendaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(TiendaS.direccion.ilike(f'%{r.direccion}%'))
            if r.frecuencia_venta:
                query = query.filter(TiendaS.frecuencia_venta == r.frecuencia_venta)
        if p.nucleo:
            r = p.nucleo
            query = query.join(NucleoS, BodegaS.id_bodega == NucleoS.id_bodega)
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
@router.get("/all", response_model=List[BodegaP])
async def read_all(skip: int = 0, limit: int = 100, p: BodegaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=BodegaP)
async def read(p: BodegaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=BodegaP)
async def create(p: BodegaC, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.numero == p.numero)
    query = query.filter(BodegaS.id_oficina == p.id_oficina)
    query = query.filter(BodegaS.id_tienda == p.tienda.id_tienda)
    model = BodegaS(numero=p.numero, direccion=p.direccion, grupos_rs=p.grupos_rs, es_especial=p.es_especial,
                    id_tienda=p.tienda.id_tienda, id_oficina=p.oficina.id_oficina)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=BodegaP)
async def update(up: BodegaU, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == up.id_bodega)
    return await forwards.update(up, query, ['id_bodega'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=BodegaE)
async def delete(p: BodegaId, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == p.id_bodega)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=BodegaP)
async def activate(up: BodegaId, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == up.id_bodega)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/nucleos", response_model=BodegaNu)
async def oficina(up: BodegaId, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == up.id_bodega)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/oficina", response_model=BodegaOf)
async def oficina(up: BodegaId, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == up.id_bodega)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/tienda", response_model=BodegaTi)
async def oficina(up: BodegaId, db: Session = Depends(get_db)):
    query = db.query(BodegaS).filter(BodegaS.id_bodega == up.id_bodega)
    return await forwards.read(query)
