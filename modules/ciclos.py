from __future__ import annotations

import datetime

from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, Date, String, func
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class CicloId(BaseModel):
    id_ciclo: int

    class Config:
        from_attributes = True


class CicloP(CicloId):
    nombre: str
    descripcion: str | None
    fecha_inicio: datetime.date
    fecha_fin: datetime.date | None
    ofertas: List['OfertaE'] | None


class CicloU(CicloId):
    nombre: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None


class CicloE(CicloId):
    nombre: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None


class CicloR(BaseModel):
    id_ciclo: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime.date | None = None
    fecha_fin: datetime.date | None
    oferta: Optional['OfertaE'] = None


class CicloC(BaseModel):
    nombre: str
    descripcion: str = ''
    fecha_inicio: datetime.date
    fecha_fin: datetime.date | None


class CicloOf(CicloId):
    nombre: str
    ofertas: List['OfertaE']


class CicloS(Base):
    __tablename__ = "ciclos"
    id_ciclo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    fecha_inicio = Column(Date, server_default=func.now(), index=True)
    fecha_fin = Column(Date, nullable=True, index=True)
    ofertas: Mapped[List['OfertaS']] = relationship(back_populates="ciclo", cascade="all, delete")


from .ofertas import OfertaS, OfertaE

CicloP.model_rebuild()
CicloR.model_rebuild()
CicloU.model_rebuild()
CicloC.model_rebuild()
CicloOf.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(CicloS)
    if p:
        query = query.filter(CicloS.id_ciclo == p.id_ciclo)
        if p.nombre:
            query = query.filter(CicloS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(CicloS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.fecha_inicio:
            query = query.filter(CicloS.fecha_inicio == p.fecha_inicio)
        if p.fecha_fin:
            query = query.filter(CicloS.fecha_fin == p.fecha_fin)
        if p.oferta:
            r = p.oferta
            query = query.join(OfertaS, OfertaS.id_ciclo == CicloS.id_ciclo)
            if r.id_oferta:
                query = query.filter(OfertaS.id_oferta == r.id_oferta)
            if r.descripcion:
                query = query.filter(OfertaS.descripcion.ilike(f'%{r.descripcion}%'))
            if r.fecha_inicio:
                query = query.filter(OfertaS.fecha_inicio == r.fecha_inicio)
            if r.fecha_fin:
                query = query.filter(OfertaS.fecha_fin == r.fecha_fin)
            if r.cantidad:
                query = query.filter(OfertaS.cantidad == r.cantidad)
    return query


# noinspection PyTypeChecker
@router.post("/all", response_model=List[CicloP])
async def read_all(skip: int = 0, limit: int = 100, p: CicloR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=CicloP)
async def read(p: CicloR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=CicloP)
async def create(p: CicloC, db: Session = Depends(get_db)):
    query = db.query(CicloS).filter(CicloS.nombre == p.nombre)
    model = CicloS(nombre=p.nombre, fecha_inicio=p.fecha_inicio, fecha_fin=p.fecha_fin,
                   descripcion=p.descripcion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=CicloP)
async def update(up: CicloU, db: Session = Depends(get_db)):
    query = db.query(CicloS).filter(CicloS.id_ciclo == up.id_ciclo)
    return await forwards.update(up, query, ['id_ciclo'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=CicloE)
async def delete(p: CicloId, db: Session = Depends(get_db)):
    query = db.query(CicloS).filter(CicloS.id_ciclo == p.id_ciclo)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.post("/ofertas", response_model=CicloOf)
async def read_ofertas(p: CicloId, db: Session = Depends(get_db)):
    query = db.query(CicloS).filter(CicloS.id_ciclo == p.id_ciclo)
    return await forwards.read(query)
