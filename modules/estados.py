from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class EstadoId(BaseModel):
    id_estado: int

    class Config:
        from_attributes = True


class EstadoP(EstadoId):
    nombre: str
    descripcion: str | None
    compras: List['CompraE'] | None


class EstadoU(EstadoId):
    nombre: str | None = None
    descripcion: str | None = None


class EstadoE(BaseModel):
    id_estado: int | None = None
    nombre: str | None = None
    descripcion: str | None = None


class EstadoR(BaseModel):
    id_estado: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    compra: Optional['CompraE'] | None


class EstadoC(BaseModel):
    nombre: str
    descripcion: str = ''


class EstadoCo(EstadoId):
    nombre: str
    compras: List['CompraE']


class EstadoS(Base):
    __tablename__ = "estados"
    id_estado = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    compras: Mapped[List['CompraS']] = relationship(back_populates="estado", cascade="all, delete")


from .compras import CompraS, CompraE

EstadoP.model_rebuild()
EstadoR.model_rebuild()
EstadoU.model_rebuild()
EstadoC.model_rebuild()
EstadoCo.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(EstadoS)
    if p:
        if p.id_estado:
            query = query.filter(EstadoS.id_estado == p.id_estado)
        if p.nombre:
            query = query.filter(EstadoS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(EstadoS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.compra:
            r = p.compra
            query = query.join(CompraS, CompraS.id_estado == EstadoS.id_estado)
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
@router.get("/all", response_model=List[EstadoP])
async def read_all(skip: int = 0, limit: int = 100, p: EstadoR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=EstadoP)
async def read(p: EstadoR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=EstadoP)
async def create(p: EstadoC, db: Session = Depends(get_db)):
    query = db.query(EstadoS).filter(EstadoS.nombre == p.nombre)
    model = EstadoS(nombre=p.nombre, descripcion=p.descripcion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=EstadoP)
async def update(up: EstadoU, db: Session = Depends(get_db)):
    query = db.query(EstadoS).filter(EstadoS.id_estado == up.id_estado)
    return await forwards.update(up, query, ['id_estado'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=EstadoE)
async def delete(p: EstadoId, db: Session = Depends(get_db)):
    query = db.query(EstadoS).filter(EstadoS.id_estado == p.id_estado)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.get("/compras", response_model=EstadoCo)
async def read_compras(p: EstadoId, db: Session = Depends(get_db)):
    query = db.query(EstadoS).filter(EstadoS.id_estado == p.id_estado)
    return await forwards.read(query)
