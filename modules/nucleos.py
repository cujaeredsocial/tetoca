from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint, Boolean
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class NucleoId(BaseModel):
    id_nucleo: int

    class Config:
        from_attributes = True


class NucleoP(NucleoId):
    numero: str
    cant_miembros: int
    cant_modulos: int
    desac: bool
    bodega: 'BodegaE'
    consumidor_jefe: 'ConsumidorE'# | None
    consumidores: List['ConsumidorE'] | None
    compras: List['CompraE'] | None
    

class NucleoU(NucleoId):
    numero: str | None = None
    cant_miembros: int | None = None
    cant_modulos: int | None = None
    id_bodega: int | None = None
    id_consumidor_jefe: int | None = None


class NucleoE(BaseModel):
    id_nucleo: int | None = None
    numero: str | None = None
    cant_miembros: int | None = None
    cant_modulos: int | None = None
    desac: bool | None = None


class NucleoR(BaseModel):
    id_nucleo: int | None = None
    numero: str | None = None
    cant_miembros: int | None = None
    cant_modulos: int | None = None
    desac: bool | None = None
    bodega: Optional['BodegaE'] = None
    consumidor_jefe: Optional['ConsumidorE'] = None
    consumidor: Optional['ConsumidorE'] = None
    compra: Optional['CompraE'] = None
    

class NucleoC(BaseModel):
    numero: str
    cant_miembros: int = 0
    cant_modulos: int = 0
    bodega: 'BodegaId'
    consumidor_jefe: 'ConsumidorId' = None


class NucleoCs(BaseModel):
    numero: str
    bodega: 'BodegaE'
    consumidor_jefe: 'ConsumidorE' = None
    consumidores: List['ConsumidorE']


class NucleoCp(BaseModel):
    numero: str
    bodega: 'BodegaE'
    consumidor_jefe: 'ConsumidorE' = None
    compras: List['CompraE']


class NucleoBo(BaseModel):
    numero: str
    id_bodega: int
    bodega: 'BodegaE'


class NucleoJe(BaseModel):
    numero: str
    id_consumidor_jefe: int
    consumidor_jefe: 'ConsumidorE'


# noinspection PyTypeChecker
class NucleoS(Base):
    __tablename__ = "nucleos"
    id_nucleo = Column(Integer, primary_key=True, index=True)
    numero = Column(String, nullable=False, index=True)
    cant_miembros = Column(Integer, nullable=False, index=True, default=0)
    cant_modulos = Column(Integer, nullable=False, index=True, default=0)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_bodega = Column(Integer, ForeignKey('bodegas.id_bodega', ondelete='CASCADE'), nullable=False, index=True)
    bodega: Mapped['BodegaS'] = relationship('BodegaS', back_populates="nucleos")
    #id_consumidor_jefe = Column(Integer, ForeignKey('consumidores.id_consumidor', ondelete='CASCADE'),
    #                            nullable=True, index=True)
    #consumidor_jefe: Mapped['ConsumidorS'] = relationship('ConsumidorS', back_populates="nucleos")
    consumidores: Mapped[List['ConsumidorS']] = relationship(back_populates="nucleo", cascade="all, delete")
    compras: Mapped[List['CompraS']] = relationship(back_populates="nucleo", cascade="all, delete")
    __table_args__ = (UniqueConstraint(numero, id_bodega, name='u_numero_bodega'),)


from .bodegas import BodegaE, BodegaId, BodegaS
from .consumidores import ConsumidorS, ConsumidorE, ConsumidorId
from .compras import CompraS, CompraE

NucleoP.model_rebuild()
NucleoR.model_rebuild()
NucleoU.model_rebuild()
NucleoC.model_rebuild()
NucleoCs.model_rebuild()
NucleoCp.model_rebuild()
NucleoBo.model_rebuild()
NucleoJe.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(NucleoS)
    if p:
        if p.id_nucleo:
            query = query.filter(NucleoS.id_nucleo == p.id_nucleo)
        if p.numero:
            query = query.filter(NucleoS.numero.ilike(f'%{p.numero}%'))
        if p.cant_miembros:
            query = query.filter(NucleoS.cant_miembros == p.cant_miembros)
        if p.cant_modulos:
            query = query.filter(NucleoS.cant_modulos == p.cant_modulos)
        if p.desac is not None:
            query = query.filter(NucleoS.desac == p.desac)
        if p.bodega:
            r = p.bodega
            query = query.join(BodegaS, BodegaS.id_bodega == NucleoS.id_bodega)
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
        if p.consumidor_jefe:
            r = p.consumidor_jefe
            query = query.join(ConsumidorS, ConsumidorS.id_consumidor == NucleoS.id_consumidor_jefe)
            if r.id_consumidor:
                query = query.filter(ConsumidorS.id_consumidor == r.id_consumidor)
            if r.verificado:
                query = query.filter(ConsumidorS.verificado == r.verificado)
            if r.fecha_creacion:
                query = query.filter(ConsumidorS.fecha_creacion == r.fecha_creacion)
        if p.consumidor:
            r = p.consumidor
            query = query.join(ConsumidorS, ConsumidorS.id_nucleo == NucleoS.id_nucleo)
            if r.id_consumidor:
                query = query.filter(ConsumidorS.id_consumidor == r.id_consumidor)
            if r.verificado:
                query = query.filter(ConsumidorS.verificado == r.verificado)
            if r.fecha_creacion:
                query = query.filter(ConsumidorS.fecha_creacion == r.fecha_creacion)
        if p.compra:
            r = p.compra
            query = query.join(CompraS, CompraS.id_nucleo == NucleoS.id_nucleo)
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
@router.get("/all", response_model=List[NucleoP])
async def read_all(skip: int = 0, limit: int = 100, p: NucleoR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=NucleoP)
async def read(p: NucleoR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=NucleoP)
async def create(p: NucleoC, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.numero == p.numero)
    query = query.filter(NucleoS.id_bodega == p.bodega.id_bodega).first()
    model = NucleoS(numero=p.numero, cant_miembros=p.cant_miembros, cant_modulos=p.cant_modulos,
                    id_bodega=p.bodega.id_bodega, id_consumidor_jefe=p.consumidor_jefe.id_consumidor)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=NucleoP)
async def update(up: NucleoU, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == up.id_nucleo)
    return await forwards.update(up, query, ['id_nucleo'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=NucleoE)
async def delete(p: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == p.id_nucleo)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=NucleoP)
async def activate(up: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == up.id_nucleo)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/bodega", response_model=NucleoBo)
async def read_bodega(p: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == p.id_nucleo)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/consumidor_jefe", response_model=NucleoJe)
async def read_consumidor_jefe(p: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == p.id_nucleo)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/consumidores", response_model=NucleoCs)
async def read_consumidores(p: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == p.id_nucleo)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/compras", response_model=NucleoCp)
async def read_compras(p: NucleoId, db: Session = Depends(get_db)):
    query = db.query(NucleoS).filter(NucleoS.id_nucleo == p.id_nucleo)
    return await forwards.read(query)
