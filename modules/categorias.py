from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class CategoriaId(BaseModel):
    id_categoria: int

    class Config:
        from_attributes = True


class CategoriaP(CategoriaId):
    nombre: str
    descripcion: str | None
    productos: List['ProductoE'] | None


class CategoriaU(CategoriaId):
    nombre: str | None = None
    descripcion: str | None = None


class CategoriaE(BaseModel):
    id_categoria: int | None = None
    nombre: str | None = None
    descripcion: str | None = None


class CategoriaR(BaseModel):
    id_categoria: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    producto: Optional['ProductoE'] = None


class CategoriaC(BaseModel):
    nombre: str
    descripcion: str = ''


class CategoriaPr(CategoriaId):
    nombre: str
    productos: List['ProductoE']


class CategoriaS(Base):
    __tablename__ = "categorias"
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    productos: Mapped[List["ProductoS"]] = relationship(back_populates="categoria", cascade="all, delete")


from .productos import ProductoE, ProductoS

CategoriaP.model_rebuild()
CategoriaR.model_rebuild()
CategoriaU.model_rebuild()
CategoriaC.model_rebuild()
CategoriaPr.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(CategoriaS)
    if p:
        if p.id_categoria:
            query = query.filter(CategoriaS.id_categoria == p.id_categoria)
        if p.nombre:
            query = query.filter(CategoriaS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(CategoriaS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.producto:
            r = p.producto
            query = query.join(ProductoS, ProductoS.id_categoria == CategoriaS.id_categoria)
            if r.id_producto:
                query = query.filter(ProductoS.id_producto == r.id_producto)
            if r.nombre:
                query = query.filter(ProductoS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(ProductoS.descripcion.ilike(f'%{r.descripcion}%'))
    return query


# noinspection PyTypeChecker
@router.post("/all", response_model=List[CategoriaP])
async def read_all(skip: int = 0, limit: int = 100, p: CategoriaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=CategoriaP)
async def read(p: CategoriaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=CategoriaP)
async def create(p: CategoriaC, db: Session = Depends(get_db)):
    query = db.query(CategoriaS).filter(CategoriaS.nombre == p.nombre)
    model = CategoriaS(nombre=p.nombre, descripcion=p.descripcion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=CategoriaP)
async def update(up: CategoriaU, db: Session = Depends(get_db)):
    query = db.query(CategoriaS).filter(CategoriaS.id_categoria == up.id_categoria)
    return await forwards.update(up, query, ['id_categoria'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=CategoriaE)
async def delete(p: CategoriaId, db: Session = Depends(get_db)):
    query = db.query(CategoriaS).filter(CategoriaS.id_categoria == p.id_categoria)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.post("/productos", response_model=CategoriaPr)
async def read_productos(p: CategoriaId, db: Session = Depends(get_db)):
    query = db.query(CategoriaS).filter(CategoriaS.id_categoria == p.id_categoria)
    return await forwards.read(query)
