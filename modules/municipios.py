from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session, relationship, Mapped
from fastapi import Depends, APIRouter
from typing import List, Optional
from service import forwards

router = APIRouter()


class MunicipioId(BaseModel):
    id_municipio: int

    class Config:
        from_attributes = True


class MunicipioP(MunicipioId):
    nombre: str
    siglas: str | None
    ubicacion: str | None
    desac: bool
    provincia: 'ProvinciaE'
    tiendas: List['TiendaE'] | None
    oficinas: List['OficinaE'] | None


class MunicipioU(MunicipioId):
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None
    id_provincia: int | None = None


class MunicipioE(BaseModel):
    id_municipio: int | None = None
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None
    desac: bool | None = None


class MunicipioR(BaseModel):
    id_municipio: int | None = None
    nombre: str | None = None
    siglas: str | None = None
    ubicacion: str | None = None
    desac: bool | None = None
    provincia: Optional['ProvinciaE'] = None
    oficina: Optional['OficinaE'] = None
    tienda: Optional['TiendaE'] = None


class MunicipioC(BaseModel):
    nombre: str
    siglas: str = ''
    ubicacion: str = ''
    provincia: 'ProvinciaId'


class MunicipioPr(MunicipioId):
    nombre: str
    id_provincia: int
    provincia: 'ProvinciaE'


class MunicipioTi(MunicipioId):
    nombre: str
    provincia: 'ProvinciaE'
    tiendas: List['TiendaE']


class MunicipioOf(MunicipioId):
    nombre: str
    provincia: 'ProvinciaE'
    oficinas: List['OficinaE']


class MunicipioBo(MunicipioId):
    nombre: str
    provincia: 'ProvinciaE'
    bodegas: List['BodegaE']


# noinspection PyTypeChecker
class MunicipioS(Base):
    __tablename__ = "municipios"
    id_municipio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    siglas = Column(String, unique=False, nullable=True, index=False)
    ubicacion = Column(String, unique=False, nullable=True, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_provincia = Column(Integer, ForeignKey('provincias.id_provincia', ondelete='CASCADE'),
                          nullable=False, index=True)
    provincia: Mapped['ProvinciaS'] = relationship('ProvinciaS', back_populates="municipios")
    tiendas: Mapped[List["TiendaS"]] = relationship(back_populates="municipio", cascade="all, delete")
    oficinas: Mapped[List["OficinaS"]] = relationship(back_populates="municipio", cascade="all, delete")
    __table_args__ = (UniqueConstraint(nombre, id_provincia, name='u_nombre_provincia'),)


from .provincias import ProvinciaE, ProvinciaS, ProvinciaId
from .tiendas import TiendaE, TiendaS
from .oficinas import OficinaE, OficinaS
from .bodegas import BodegaE

MunicipioP.model_rebuild()
MunicipioR.model_rebuild()
MunicipioU.model_rebuild()
MunicipioC.model_rebuild()
MunicipioPr.model_rebuild()
MunicipioTi.model_rebuild()
MunicipioOf.model_rebuild()
MunicipioBo.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(MunicipioS)
    if p:
        if p.id_municipio:
            query = query.filter(MunicipioS.id_municipio == p.id_municipio)
        if p.nombre:
            query = query.filter(MunicipioS.nombre.ilike(f'%{p.nombre}%'))
        if p.siglas:
            query = query.filter(MunicipioS.siglas.ilike(f'%{p.siglas}%'))
        if p.ubicacion:
            query = query.filter(MunicipioS.siglas.ilike(f'%{p.ubicacion}%'))
        if p.desac is not None:
            query = query.filter(MunicipioS.desac == p.desac)
        if p.provincia:
            r = p.provincia
            query = query.join(ProvinciaS, ProvinciaS.id_provincia == MunicipioS.id_provincia)
            if r.id_provincia:
                query = query.filter(ProvinciaS.id_provincia == r.id_provincia)
            if r.nombre:
                query = query.filter(ProvinciaS.nombre.ilike(f'%{r.nombre}%'))
            if r.siglas:
                query = query.filter(ProvinciaS.siglas.ilike(f'%{r.siglas}%'))
            if r.ubicacion:
                query = query.filter(ProvinciaS.ubicacion.ilike(f'%{r.ubicacion}%'))
        if p.oficina:
            r = p.oficina
            query = query.join(OficinaS, OficinaS.id_municipio == MunicipioS.id_municipio)
            if r.id_oficina:
                query = query.filter(OficinaS.id_oficina == r.id_oficina)
            if r.nombre:
                query = query.filter(OficinaS.nombre.ilike(f'%{r.nombre}%'))
            if r.direccion:
                query = query.filter(OficinaS.direccion.ilike(f'%{r.direccion}%'))
        if p.tienda:
            r = p.tienda
            query = query.join(TiendaS, TiendaS.id_municipio == MunicipioS.id_municipio)
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
@router.get("/all", response_model=List[MunicipioP])
async def read_all(skip: int = 0, limit: int = 100, p: MunicipioR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=MunicipioP)
async def read(p: MunicipioR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=MunicipioP)
async def create(p: MunicipioC, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.nombre == p.nombre)
    query = query.filter(MunicipioS.id_provincia == p.provincia.id_provincia)
    model = MunicipioS(nombre=p.nombre, id_provincia=p.provincia.id_provincia,
                       siglas=p.siglas, ubicacion=p.ubicacion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=MunicipioP)
async def update(up: MunicipioU, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == up.id_municipio)
    return await forwards.update(up, query, ['id_municipio'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=MunicipioE)
async def delete(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == p.id_municipio)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=MunicipioP)
async def activate(up: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == up.id_municipio)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/provincia", response_model=MunicipioPr)
async def read_provincia(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == p.id_municipio)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/tiendas", response_model=MunicipioTi)
async def read_tiendas(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == p.id_municipio)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/oficinas", response_model=MunicipioOf)
async def read_oficinas(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == p.id_municipio)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/bodegas", response_model=MunicipioBo)
async def read_oficinas(p: MunicipioId, db: Session = Depends(get_db)):
    query = db.query(MunicipioS).filter(MunicipioS.id_municipio == p.id_municipio)
    query = await forwards.read(query)
    bodegas = []
    for ofi in query.oficinas:
        bodegas.extend([BodegaE(**i.__dict__) for i in ofi.bodegas])
    return MunicipioBo(id_municipio=query.id_municipio, nombre=query.nombre,
                       provincia=ProvinciaE(**query.provincia.__dict__), bodegas=bodegas)
