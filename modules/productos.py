from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class ProductoId(BaseModel):
    id_producto: int

    class Config:
        from_attributes = True


class ProductoP(ProductoId):
    nombre: str
    descripcion: str | None
    desac: bool
    categoria: 'CategoriaE'
    subofertas: List['SubOfertaE'] | None


class ProductoU(ProductoId):
    nombre: str | None = None
    descripcion: str | None
    id_categoria: int | None = None


class ProductoE(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    desac: bool | None = None


class ProductoR(BaseModel):
    id_producto: int | None = None
    nombre: str | None = None
    descripcion: str | None = None
    desac: bool | None = None
    categoria: Optional['CategoriaE'] = None
    suboferta: Optional['SubOfertaE'] = None


class ProductoC(BaseModel):
    nombre: str
    descripcion: str = ''
    categoria: 'CategoriaId'


class ProductoSu(ProductoId):
    nombre: str
    subofertas: List['SubOfertaE']


class ProductoCa(ProductoId):
    nombre: str
    id_categoria: int
    categoria: 'CategoriaE'


# noinspection PyTypeChecker
class ProductoS(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, nullable=True, index=False)
    desac = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria', ondelete='CASCADE'),
                          nullable=False, index=True)
    categoria: Mapped['CategoriaS'] = relationship('CategoriaS', back_populates="productos")
    subofertas: Mapped[List["SubOfertaS"]] = relationship(back_populates="producto", cascade="all, delete")


from .categorias import CategoriaE, CategoriaId, CategoriaS
from .subofertas import SubOfertaE, SubOfertaS

ProductoP.model_rebuild()
ProductoR.model_rebuild()
ProductoU.model_rebuild()
ProductoC.model_rebuild()
ProductoSu.model_rebuild()
ProductoCa.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(ProductoS)
    if p:
        if p.id_producto:
            query = query.filter(ProductoS.id_producto == p.id_producto)
        if p.nombre:
            query = query.filter(ProductoS.nombre.ilike(f'%{p.nombre}%'))
        if p.descripcion:
            query = query.filter(ProductoS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.desac is not None:
            query = query.filter(ProductoS.desac == p.desac)
        if p.categoria:
            r = p.categoria
            query = query.join(CategoriaS, CategoriaS.id_categoria == ProductoS.id_categoria)
            if r.id_categoria:
                query = query.filter(CategoriaS.id_categoria == r.id_categoria)
            if r.nombre:
                query = query.filter(CategoriaS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(CategoriaS.descripcion.ilike(f'%{r.descripcion}%'))
        if p.suboferta:
            r = p.suboferta
            query = query.join(SubOfertaS, SubOfertaS.id_producto == ProductoS.id_producto)
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
@router.get("/all", response_model=List[ProductoP])
async def read_all(skip: int = 0, limit: int = 100, p: ProductoR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=ProductoP)
async def read(p: ProductoR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=ProductoP)
async def create(p: ProductoC, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.nombre == p.nombre)
    query = query.filter(CategoriaS.id_categoria == p.categoria.id_categoria)
    model = ProductoS(nombre=p.nombre, descripcion=p.descripcion, id_categoria=p.categoria.id_categoria)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=ProductoP)
async def update(up: ProductoU, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.id_producto == up.id_producto)
    return await forwards.update(up, query, ['id_producto'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=ProductoE)
async def delete(p: ProductoId, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.id_producto == p.id_producto)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/activate", response_model=ProductoP)
async def activate(up: ProductoId, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.id_producto == up.id_producto)
    return await forwards.activate(query, db)


# noinspection PyTypeChecker
@router.get("/subofertas", response_model=ProductoSu)
async def read_ofe(p: ProductoId, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.id_producto == p.id_producto)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/categoria", response_model=ProductoCa)
async def read_categoria(p: ProductoId, db: Session = Depends(get_db)):
    query = db.query(ProductoS).filter(ProductoS.id_producto == p.id_producto)
    return await forwards.read(query)
