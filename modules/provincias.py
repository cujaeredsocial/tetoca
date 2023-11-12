from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter, Query
from typing import List, Optional
from service import forwards

router = APIRouter()


class ProvinciaId(BaseModel):
    id_provincia: int

    class Config:
        from_attributes = True


class ProvinciaP(ProvinciaId):
    nombre: str
    siglas: str | None
    ubicacion: str | None
    desac: bool
    municipios: List['MunicipioE'] | None


class ProvinciaU(ProvinciaId):
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None


class ProvinciaE(BaseModel):
    id_provincia: int | None = None
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None
    desac: bool | None = None


class ProvinciaR(BaseModel):
    id_provincia: int | None = None
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None
    desac: bool | None = None
    municipio: Optional['MunicipioE'] = None


class ProvinciaC(BaseModel):
    nombre: str
    siglas: str = ''
    ubicacion: str = ''


class ProvinciaMu(ProvinciaId):
    nombre: str
    municipios: List['MunicipioE']


class ProvinciaS(Base):
    __tablename__ = "provincias"
    id_provincia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    siglas = Column(String, unique=True, nullable=True, index=False)
    ubicacion = Column(String, unique=False, nullable=True, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    municipios: Mapped[List["MunicipioS"]] = relationship(back_populates="provincia", cascade="all, delete")


from .municipios import MunicipioE, MunicipioS

ProvinciaP.model_rebuild()
ProvinciaR.model_rebuild()
ProvinciaU.model_rebuild()
ProvinciaC.model_rebuild()
ProvinciaMu.model_rebuild()


# noinspection PyTypeChecker
async def _find_provincia(query: Query, p: BaseModel):

    return query


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(ProvinciaS)
    if p:
        if p.id_provincia:
            query = query.filter(ProvinciaS.id_provincia == p.id_provincia)
        if p.nombre:
            query = query.filter(ProvinciaS.nombre.ilike(f'%{p.nombre}%'))
        if p.siglas:
            query = query.filter(ProvinciaS.siglas.ilike(f'%{p.siglas}%'))
        if p.ubicacion:
            query = query.filter(ProvinciaS.ubicacion.ilike(f'%{p.ubicacion}%'))
        if p.desac is not None:
            query = query.filter(ProvinciaS.desac == p.desac)
        if p.municipio:
            r = p.municipio
            query = query.join(MunicipioS, ProvinciaS.id_provincia == MunicipioS.id_provincia)
            if r.id_municipio:
                query = query.filter(MunicipioS.id_municipio == r.id_municipio)
            if r.nombre:
                query = query.filter(MunicipioS.nombre.ilike(f'%{r.nombre}%'))
            if r.siglas:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.siglas}%'))
            if r.ubicacion:
                query = query.filter(MunicipioS.siglas.ilike(f'%{r.ubicacion}%'))
    return query


@router.get("/all", response_model=List[ProvinciaP])
async def read_all(skip: int = 0, limit: int = 100, p: ProvinciaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=ProvinciaP)
async def read(p: ProvinciaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=ProvinciaP)
async def create(p: ProvinciaC, db: Session = Depends(get_db)):
    query = db.query(ProvinciaS).filter(ProvinciaS.nombre == p.nombre)
    model = ProvinciaS(nombre=p.nombre, siglas=p.siglas, ubicacion=p.ubicacion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=ProvinciaP)
async def update(up: ProvinciaU, db: Session = Depends(get_db)):
    query = db.query(ProvinciaS).filter(ProvinciaS.id_provincia == up.id_provincia)
    return await forwards.update(up, query, ['id_provincia'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=ProvinciaE)
async def delete(p: ProvinciaId, db: Session = Depends(get_db)):
    query = db.query(ProvinciaS).filter(ProvinciaS.id_provincia == p.id_provincia)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=ProvinciaP)
async def activate(up: ProvinciaId, db: Session = Depends(get_db)):
    query = db.query(ProvinciaS).filter(ProvinciaS.id_provincia == up.id_provincia)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/municipios", response_model=ProvinciaMu)
async def read_municipios(p: ProvinciaId, db: Session = Depends(get_db)):
    query = db.query(ProvinciaS).filter(ProvinciaS.id_provincia == p.id_provincia)
    return await forwards.read(query)
