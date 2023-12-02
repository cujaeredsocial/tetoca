from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from typing import List
from service import forwards

router = APIRouter()


class ConfiguracionId(BaseModel):
    nombre: str

    class Config:
        from_attributes = True


class ConfiguracionP(ConfiguracionId):
    valor: str | None


class ConfiguracionU(ConfiguracionId):
    valor: str | None = None


class ConfiguracionE(BaseModel):
    nombre: str | None = None
    valor: str | None = None


class ConfiguracionR(BaseModel):
    nombre: str | None = None
    valor: str | None = None


class ConfiguracionC(BaseModel):
    nombre: str
    valor: str = ''


class ConfiguracionS(Base):
    __tablename__ = "configuracion"
    nombre = Column(String, primary_key=True, index=True)
    valor = Column(String, nullable=False, index=False)


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(ConfiguracionS)
    if p:
        if p.nombre:
            query = query.filter(ConfiguracionS.nombre.ilike(f'%{p.nombre}%'))
        if p.valor:
            query = query.filter(ConfiguracionS.valor.ilike(f'%{p.valor}%'))
    return query


@router.post("/all", response_model=List[ConfiguracionP])
async def read_all(skip: int = 0, limit: int = 100, p: ConfiguracionR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=ConfiguracionP)
async def read(p: ConfiguracionR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=ConfiguracionP)
async def create(p: ConfiguracionC, db: Session = Depends(get_db)):
    query = db.query(ConfiguracionS).filter(ConfiguracionS.nombre == p.nombre)
    model = ConfiguracionS(nombre=p.nombre, valor=p.valor)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=ConfiguracionP)
async def update(up: ConfiguracionU, db: Session = Depends(get_db)):
    query = db.query(ConfiguracionS).filter(ConfiguracionS.nombre == up.nombre)
    return await forwards.update(up, query, ['nombre'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=ConfiguracionE)
async def delete(p: ConfiguracionId, db: Session = Depends(get_db)):
    query = db.query(ConfiguracionS).filter(ConfiguracionS.nombre == p.nombre)
    return await forwards.delete(query, db)
