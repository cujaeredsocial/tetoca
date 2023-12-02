from __future__ import annotations

from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, ForeignKey, Integer, Double, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional

from service import forwards

router = APIRouter()


class SubOfertaId(BaseModel):
    id_suboferta: int

    class Config:
        from_attributes = True


class SubOfertaP(SubOfertaId):
    precio: float
    cantidad: int
    descripcion: str | None
    producto: 'ProductoE'
    oferta: 'OfertaE'


class SubOfertaU(SubOfertaId):
    precio: float | None = None
    cantidad: int | None = None
    descripcion: str | None = None
    id_producto: int | None = None
    id_oferta: int | None = None


class SubOfertaE(BaseModel):
    id_suboferta: int | None = None
    precio: float | None = None
    cantidad: int | None = None
    descripcion: str | None = None


class SubOfertaR(BaseModel):
    id_suboferta: int | None = None
    precio: float | None = None
    cantidad: int | None = None
    descripcion: str | None = None
    producto: Optional['ProductoE'] = None
    oferta: Optional['OfertaE'] = None


class SubOfertaC(BaseModel):
    precio: float
    cantidad: int
    descripcion: str = ''
    producto: 'ProductoId'
    oferta: 'OfertaId'


class SubOfertaPr(SubOfertaId):
    id_producto: int
    producto: 'ProductoE'


class SubOfertaOf(SubOfertaId):
    id_oferta: int
    oferta: 'OfertaE'


class SubOfertaS(Base):
    __tablename__ = "subofertas"
    id_suboferta = Column(Integer, primary_key=True, index=True)
    precio = Column(Double, unique=False, nullable=False, index=True)
    cantidad = Column(Integer, unique=False, nullable=False, index=True)
    descripcion = Column(String, unique=False, nullable=True, index=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto', ondelete='CASCADE'),
                         nullable=False, index=True)
    producto: Mapped['ProductoS'] = relationship('ProductoS', back_populates="subofertas")
    id_oferta = Column(Integer, ForeignKey('ofertas.id_oferta', ondelete='CASCADE'),
                       nullable=False, index=True)
    oferta: Mapped['OfertaS'] = relationship('OfertaS', back_populates="subofertas")


from .productos import ProductoE, ProductoId, ProductoS
from .ofertas import OfertaE, OfertaS, OfertaId

SubOfertaP.model_rebuild()
SubOfertaR.model_rebuild()
SubOfertaU.model_rebuild()
SubOfertaC.model_rebuild()
SubOfertaPr.model_rebuild()
SubOfertaOf.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(SubOfertaS)
    if p:
        if p.id_suboferta:
            query = query.filter(SubOfertaS.id_suboferta == p.id_suboferta)
        if p.descripcion:
            query = query.filter(SubOfertaS.descripcion.ilike(f'%{p.descripcion}%'))
        if p.precio:
            query = query.filter(SubOfertaS.precio == p.precio)
        if p.cantidad:
            query = query.filter(SubOfertaS.cantidad == p.cantidad)
        if p.producto:
            r = p.producto
            query = query.join(ProductoS, ProductoS.id_producto == SubOfertaS.id_producto)
            if r.id_producto:
                query = query.filter(ProductoS.id_producto == r.id_producto)
            if r.nombre:
                query = query.filter(ProductoS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(ProductoS.descripcion.ilike(f'%{r.descripcion}%'))
        if p.oferta:
            r = p.oferta
            query = query.join(OfertaS, OfertaS.id_oferta == SubOfertaS.id_oferta)
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
@router.post("/all", response_model=List[SubOfertaP])
async def read_all(skip: int = 0, limit: int = 100, p: SubOfertaR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.post("/read", response_model=SubOfertaP)
async def read(p: SubOfertaR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=SubOfertaP)
async def create(p: SubOfertaC, db: Session = Depends(get_db)):
    query = db.query(SubOfertaS).filter(SubOfertaS.id_suboferta == p.id_suboferta)
    model = SubOfertaS(precio=p.precio, cantidad=p.cantidad, id_producto=p.id_producto,
                       id_oferta=p.id_oferta, descripcion=p.descripcion)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=SubOfertaP)
async def update(up: SubOfertaU, db: Session = Depends(get_db)):
    query = db.query(SubOfertaS).filter(SubOfertaS.id_suboferta == up.id_suboferta)
    return await forwards.update(up, query, ['id_suboferta'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=SubOfertaE)
async def delete(p: SubOfertaId, db: Session = Depends(get_db)):
    query = db.query(SubOfertaS).filter(SubOfertaS.id_suboferta == p.id_suboferta)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.post("/producto", response_model=SubOfertaPr)
async def read_producto(p: SubOfertaId, db: Session = Depends(get_db)):
    query = db.query(SubOfertaS).filter(SubOfertaS.id_suboferta == p.id_suboferta)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/subsubofertas", response_model=SubOfertaOf)
async def read_ofertas(p: SubOfertaId, db: Session = Depends(get_db)):
    query = db.query(SubOfertaS).filter(SubOfertaS.id_suboferta == p.id_suboferta)
    return await forwards.read(query)
