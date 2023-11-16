from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, ForeignKey, Integer, func, Date, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional
import datetime

from service import forwards

router = APIRouter()


class OfertaId(BaseModel):
    id_oferta: int

    class Config:
        from_attributes = True


class OfertaP(OfertaId):
    descripcion: str | None
    fecha_inicio: datetime.date
    fecha_fin: datetime.date
    cantidad: int
    ciclo: 'CicloE'
    tienda: 'TiendaE'
    subofertas: List['SubOfertaE'] | None
    compras: List['CompraE'] | None


class OfertaU(OfertaId):
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None = None
    cantidad: int | None = None
    id_ciclo: int | None = None
    id_tienda: int | None = None


class OfertaE(BaseModel):
    id_oferta: int | None = None
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None = None
    cantidad: int | None = None


class OfertaR(BaseModel):
    id_oferta: int | None = None
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None = None
    cantidad: int | None = None
    ciclo: Optional['CicloE'] = None
    tienda: Optional['TiendaE'] = None
    suboferta: Optional['SubOfertaE'] = None
    compra: Optional['CompraE'] = None


class OfertaC(BaseModel):
    descripcion: str = ''
    fecha_inicio: datetime.date
    fecha_fin: datetime.date
    cantidad: int
    ciclo: 'CicloId'
    tienda: 'TiendaId'


class OfertaCi(OfertaId):
    id_ciclo: int
    ciclo: 'CicloE'


class OfertaTi(OfertaId):
    id_tienda: int
    tienda: 'TiendaE'


class OfertaSu(OfertaId):
    subofertas: List['SubOfertaE']


class OfertaCo(OfertaId):
    compras: List['CompraE']


class OfertaS(Base):
    __tablename__ = "ofertas"
    id_oferta = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    fecha_inicio = Column(Date, server_default=func.now())
    fecha_fin = Column(Date, server_default=func.now())
    cantidad = Column(Integer, unique=False, nullable=False, index=True)
    id_ciclo = Column(Integer, ForeignKey('ciclos.id_ciclo', ondelete='CASCADE'), nullable=False, index=True)
    ciclo: Mapped['CicloS'] = relationship('CicloS', back_populates="ofertas")
    id_tienda = Column(Integer, ForeignKey('tiendas.id_tienda', ondelete='CASCADE'), nullable=False, index=True)
    tienda: Mapped['TiendaS'] = relationship('TiendaS', back_populates="ofertas")
    subofertas: Mapped[List['SubOfertaS']] = relationship(back_populates="oferta", cascade="all, delete")
    compras: Mapped[List['CompraS']] = relationship(back_populates="oferta", cascade="all, delete")


from .tiendas import TiendaE, TiendaId, TiendaS
from .ciclos import CicloE, CicloId, CicloS
from .subofertas import SubOfertaE, SubOfertaS
from .compras import CompraE, CompraS

OfertaP.model_rebuild()
OfertaR.model_rebuild()
OfertaU.model_rebuild()
OfertaC.model_rebuild()
OfertaSu.model_rebuild()
OfertaCi.model_rebuild()
OfertaTi.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(OfertaS)
    if p:
        if p.id_oferta:
            query = query.filter(OfertaS.id_oferta == p.id_oferta)
        if p.descripcion:
            query = query.filter(OfertaS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.fecha_inicio:
            query = query.filter(OfertaS.fecha_inicio == p.fecha_inicio)
        if p.fecha_fin:
            query = query.filter(OfertaS.fecha_fin == p.fecha_fin)
        if p.cantidad:
            query = query.filter(OfertaS.cantidad == p.cantidad)
        if p.desac is not None:
            query = query.filter(OfertaS.desac == p.desac)
        if p.ciclo:
            r = p.ciclo
            query = query.join(CicloS, CicloS.id_ciclo == OfertaS.id_ciclo)
            if r.nombre:
                query = query.filter(CicloS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(CicloS.descripcion.ilike(f'%{r.descripcion}%'))
            if r.fecha_inicio:
                query = query.filter(CicloS.fecha_inicio == r.fecha_inicio)
            if r.fecha_fin:
                query = query.filter(CicloS.fecha_fin == r.fecha_fin)
        if p.tienda:
            r = p.tienda
            query = query.join(TiendaS, TiendaS.id_tienda == OfertaS.id_tienda)
            if r.id_tienda:
                query = query.filter(TiendaS.id_tienda == r.id_tienda)
            if r.nombre:
                query = query.filter(TiendaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(TiendaS.direccion.ilike(f'%{r.direccion}%'))
            if r.frecuencia_venta:
                query = query.filter(TiendaS.frecuencia_venta == r.frecuencia_venta)
            if r.desac is not None:
                query = query.filter(TiendaS.desac == r.desac)
        if p.compra:
            r = p.compra
            query = query.join(CompraS, CompraS.id_oferta == OfertaS.id_oferta)
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
        if p.suboferta:
            r = p.suboferta
            query = query.join(SubOfertaS, SubOfertaS.id_oferta == OfertaS.id_oferta)
            if r.id_suboferta:
                query = query.filter(SubOfertaS.id_suboferta == r.id_suboferta)
            if r.descripcion:
                query = query.filter(SubOfertaS.descripcion.ilike(f'%{r.descripcion}%'))
            if r.precio:
                query = query.filter(SubOfertaS.precio == r.precio)
            if r.cantidad:
                query = query.filter(SubOfertaS.cantidad == r.cantidad)
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[OfertaP])
async def read_all(skip: int = 0, limit: int = 100, p: OfertaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=OfertaP)
async def read(p: OfertaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=OfertaP)
async def create(p: OfertaC, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)

    model = OfertaS(descripcion=p.descripcion, fecha_inicio=p.fecha_inicio,
                    fecha_fin=p.fecha_fin, cantidad=p.cantidad, id_ciclo=p.id_ciclo)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=OfertaP)
async def update(up: OfertaU, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == up.id_oferta)
    return await forwards.update(up, query, ['id_oferta'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=OfertaE)
async def delete(p: OfertaId, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.get("/ciclo", response_model=OfertaCi)
async def read_ciclo(p: OfertaId, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/tienda", response_model=OfertaTi)
async def read_tienda(p: OfertaId, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/subofertas", response_model=OfertaSu)
async def read_subofertas(p: OfertaId, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/compras", response_model=OfertaCo)
async def read_compras(p: OfertaId, db: Session = Depends(get_db)):
    query = db.query(OfertaS).filter(OfertaS.id_oferta == p.id_oferta)
    return await forwards.read(query)
