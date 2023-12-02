from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional
from service import forwards

router = APIRouter()


class CadenaId(BaseModel):
    id_cadena: int

    class Config:
        from_attributes = True


class CadenaP(CadenaId):
    nombre: str
    descripcion: str | None
    siglas: str | None
    desac: bool
    tiendas: List['TiendaE'] | None


class CadenaU(CadenaId):
    nombre: str | None = None
    descripcion: str | None = None
    siglas: str | None = None


class CadenaE(BaseModel):
    id_cadena: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    siglas: str | None = None
    desac: bool | None = None


class CadenaR(BaseModel):
    id_cadena: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    siglas: str | None = None
    tienda: Optional['TiendaE'] = None


class CadenaC(BaseModel):
    nombre: str
    descripcion: str = ''
    siglas: str = ''


class CadenaTi(CadenaId):
    nombre: str
    tiendas: List['TiendaE']


class CadenaS(Base):
    __tablename__ = "cadenas"
    id_cadena = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    siglas = Column(String, unique=False, nullable=True, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    tiendas: Mapped[List["TiendaS"]] = relationship(back_populates="cadena", cascade="all, delete")


from .tiendas import TiendaE, TiendaS

CadenaP.model_rebuild()
CadenaR.model_rebuild()
CadenaU.model_rebuild()
CadenaC.model_rebuild()
CadenaTi.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(CadenaS)
    if p:
        if p.id_cadena:
            query = query.filter(CadenaS.id_cadena == p.id_cadena)
        if p.nombre:
            query = query.filter(CadenaS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(CadenaS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.siglas:
            query = query.filter(CadenaS.siglas.ilike(f'%{p.siglas}%'))
        if p.desac is not None:
            query = query.filter(CadenaS.desac == p.desac)
        if p.tienda:
            r = p.tienda
            query = query.join(TiendaS, CadenaS.id_cadena == TiendaS.id_cadena)
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
@router.post("/all", response_model=List[CadenaP])
async def read_all(skip: int = 0, limit: int = 100, p: CadenaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=CadenaP)
async def read(p: CadenaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=CadenaP)
async def create(p: CadenaC, db: Session = Depends(get_db)):
    query = db.query(CadenaS).filter(CadenaS.nombre == p.nombre)
    model = CadenaS(nombre=p.nombre, descripcion=p.descripcion, siglas=p.siglas)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=CadenaP)
async def update(up: CadenaU, db: Session = Depends(get_db)):
    query = db.query(CadenaS).filter(CadenaS.id_cadena == up.id_cadena)
    return await forwards.update(up, query, ['id_cadena'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=CadenaE)
async def delete(p: CadenaId, db: Session = Depends(get_db)):
    query = db.query(CadenaS).filter(CadenaS.id_cadena == p.id_cadena)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=CadenaP)
async def activate(up: CadenaId, db: Session = Depends(get_db)):
    query = db.query(CadenaS).filter(CadenaS.id_cadena == up.id_cadena)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.post("/tiendas", response_model=CadenaTi)
async def read_tiendas(p: CadenaId, db: Session = Depends(get_db)):
    query = db.query(CadenaS).filter(CadenaS.id_cadena == p.id_cadena)
    return await forwards.read(query)
