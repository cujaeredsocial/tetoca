from __future__ import annotations
from pydantic import BaseModel
from database import Base, get_db
from sqlalchemy import Column, ForeignKey, DateTime, Integer, func, Boolean, String
from sqlalchemy.orm import Session, Mapped, relationship
from fastapi import Depends, APIRouter
from typing import List, Optional
import datetime

from service import forwards

router = APIRouter()


class CompraId(BaseModel):
    id_compra: int

    class Config:
        from_attributes = True


class CompraP(CompraId):
    fecha: datetime.datetime
    terminado: bool
    pagado: bool
    oferta: 'OfertaE'
    nucleo: 'NucleoE'
    usuario: 'UsuarioE'
    estado: 'EstadoE'
    seleccion: str | None
    notificado: bool


class CompraU(CompraId):
    fecha: datetime.datetime | None = None
    terminado: bool | None = None
    pagado: bool | None = None
    id_oferta: int | None = None
    id_nucleo: int | None = None
    id_usuario: int | None = None
    id_estado: int | None = None
    seleccion: str | None = None


class CompraE(BaseModel):
    id_compra: int | None = None
    fecha: datetime.datetime | None = None
    terminado: bool | None = None
    pagado: bool | None = None
    seleccion: str | None = None


class CompraR(BaseModel):
    id_compra: int | None = None
    fecha: datetime.datetime | None = None
    terminado: bool | None = None
    pagado: bool | None = None
    oferta: Optional['OfertaE'] = None
    nucleo: Optional['NucleoE'] = None
    usuario: Optional['UsuarioE'] = None
    estado: Optional['EstadoE'] = None
    seleccion: str | None = None


class CompraC(BaseModel):
    fecha: datetime.datetime
    terminado: bool
    pagado: bool
    oferta: 'OfertaId'
    nucleo: 'NucleoId'
    usuario: 'UsuarioId'
    estado: 'EstadoId'
    seleccion: str = ''


class CompraOf(CompraId):
    id_oferta: int
    oferta: 'OfertaId'
    nucleo: 'NucleoId'
    usuario: 'UsuarioId'
    estado: 'EstadoId'


class CompraNu(CompraId):
    id_nucleo: int
    nucleo: 'NucleoId'


class CompraUs(CompraId):
    id_usuario: int
    usuario: 'UsuarioId'
    estado: 'EstadoId'


class CompraEs(CompraId):
    id_estado: int
    estado: 'EstadoId'


# noinspection PyTypeChecker
class CompraS(Base):
    __tablename__ = "compras"
    id_compra = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    terminado = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    pagado = Column(Boolean, unique=False, nullable=False, index=False, default=False)
    id_oferta = Column(Integer, ForeignKey('ofertas.id_oferta', ondelete='CASCADE'),
                       nullable=False, index=True)
    oferta: Mapped['OfertaS'] = relationship('OfertaS', back_populates="compras")
    id_nucleo = Column(Integer, ForeignKey('nucleos.id_nucleo', ondelete='CASCADE'),
                       nullable=False, index=True)
    nucleo: Mapped['NucleoS'] = relationship('NucleoS', back_populates="compras")
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
                        nullable=False, index=True)
    usuario: Mapped['UsuarioS'] = relationship('UsuarioS', back_populates="compras")
    id_estado = Column(Integer, ForeignKey('estados.id_estado', ondelete='CASCADE'),
                       nullable=False, index=True)
    estado: Mapped['EstadoS'] = relationship('EstadoS', back_populates="compras")
    seleccion = Column(String, unique=False, nullable=True, index=False)
    notificado = Column(Boolean, unique=False, nullable=True, index=False, default=True)


from .usuarios import UsuarioE, UsuarioId, UsuarioS
from .nucleos import NucleoE, NucleoId, NucleoS
from .ofertas import OfertaE, OfertaId, OfertaS
from .estados import EstadoE, EstadoId, EstadoS

CompraP.model_rebuild()
CompraR.model_rebuild()
CompraU.model_rebuild()
CompraC.model_rebuild()
CompraOf.model_rebuild()
CompraNu.model_rebuild()
CompraUs.model_rebuild()
CompraEs.model_rebuild()


# noinspection PyTypeChecker
async def _find(p: BaseModel, db: Session):
    query = db.query(CompraS)
    if p:
        if p.id_compra:
            query = query.filter(CompraS.id_compra == p.id_compra)
        if p.fecha:
            query = query.filter(CompraS.fecha == p.fecha)
        if p.terminado is not None:
            query = query.filter(CompraS.terminado == p.terminado)
        if p.pagado is not None:
            query = query.filter(CompraS.pagado == p.pagado)
        if p.notificado is not None:
            query = query.filter(CompraS.notificado == p.notificado)
        if p.seleccion:
            query = query.filter(CompraS.seleccion.ilike(f'%{p.seleccion}%'))
        if p.usuario:
            r = p.usuario
            query = query.join(UsuarioS, CompraS.id_usuario == UsuarioS.id_usuario)
            if r.id_usuario:
                query = query.filter(UsuarioS.id_usuario == r.id_usuario)
            if r.nom_usuario:
                query = query.filter(UsuarioS.nom_usuario.ilike(f'%{r.nom_usuario}%'))
            if r.num_cel:
                query = query.filter(UsuarioS.num_cel.ilike(f'%{r.num_cel}%'))
            if r.ci:
                query = query.filter(UsuarioS.ci.ilike(f'%{r.ci}%'))
            if r.nombre_completo:
                query = query.filter(UsuarioS.nombre_completo.ilike(f'%{r.nombre_completo}%'))
            if r.dir_postal:
                query = query.filter(UsuarioS.dir_postal.ilike(f'%{r.dir_postal}%'))
            if r.usuario_ws:
                query = query.filter(UsuarioS.usuario_wa.ilike(f'%{r.usuario_wa}%'))
            if r.usuario_te:
                query = query.filter(UsuarioS.usuario_te.ilike(f'%{r.usuario_te}%'))
            if r.usuario_to:
                query = query.filter(UsuarioS.usuario_to.ilike(f'%{r.usuario_to}%'))
            if r.dir_correo:
                query = query.filter(UsuarioS.dir_correo.ilike(f'%{r.dir_correo}%'))
            if r.fecha_creacion:
                query = query.filter(UsuarioS.fecha_creacion == r.fecha_creacion)
        if p.nucleo:
            r = p.nucleo
            query = query.join(NucleoS, CompraS.id_nucleo == NucleoS.id_nucleo)
            if r.id_nucleo:
                query = query.filter(NucleoS.id_nucleo == r.id_nucleo)
            if r.numero:
                query = query.filter(NucleoS.numero.ilike(f'%{r.numero}%'))
            if r.cant_miembros:
                query = query.filter(NucleoS.cant_miembros == r.cant_miembros)
            if r.cant_modulos:
                query = query.filter(NucleoS.cant_modulos == r.cant_modulos)
        if p.oferta:
            r = p.oferta
            query = query.join(OfertaS, CompraS.id_oferta == OfertaS.id_oferta)
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
        if p.estado:
            r = p.estado
            query = query.join(EstadoS, CompraS.id_estado == EstadoS.id_estado)
            if r.id_estado:
                query = query.filter(EstadoS.id_estado == r.id_estado)
            if r.nombre:
                query = query.filter(EstadoS.nombre.ilike(f'%{r.nombre}%'))
            if r.descripcion:
                query = query.filter(EstadoS.descripcion.ilike(f'%{r.descripcion}%'))
    return query


# noinspection PyTypeChecker
@router.get("/all", response_model=List[CompraP])
async def read_all(skip: int = 0, limit: int = 100, p: CompraR = None, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return query.offset(skip).limit(limit).all()


# noinspection PyTypeChecker
@router.get("/read", response_model=CompraP)
async def read(p: CompraR, db: Session = Depends(get_db)):
    query = await _find(p, db)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.post("/create", response_model=CompraP)
async def create(p: CompraC, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_nucleo == p.id_nucleo, CompraS.id_usuario == p.id_usuario,
                                     CompraS.id_oferta == p.id_oferta, CompraS.id_estado == p.estado)
    model = CompraS(terminado=p.terminado, pagado=p.pagado,
                    id_usuario=p.id_usuario, id_nucleo=p.id_nucleo, id_oferta=p.id_oferta, id_estado=p.id_estado)
    return await forwards.create(model, query, db)


# noinspection PyTypeChecker
@router.patch("/update", response_model=CompraP)
async def update(up: CompraU, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == up.id_compra)
    return await forwards.update(up, query, ['id_compra'], db)


# noinspection PyTypeChecker
@router.delete("/delete", response_model=CompraE)
async def delete(p: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == p.id_compra)
    return await forwards.delete(query, db)


# noinspection PyTypeChecker
@router.put("/pagado", response_model=CompraP)
async def pagado(up: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == up.id_compra)
    return await forwards.changeTrue(query, db, 'pagado')


# noinspection PyTypeChecker
@router.put("/terminado", response_model=CompraP)
async def terminado(up: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == up.id_compra)
    return await forwards.changeTrue(query, db, 'terminado')


# noinspection PyTypeChecker
@router.put("/notificado", response_model=CompraP)
async def terminado(up: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == up.id_compra)
    return await forwards.changeTrue(query, db, 'notificado')


# noinspection PyTypeChecker
@router.get("/oferta", response_model=CompraOf)
async def read_oferta(p: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == p.id_compra)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/nucleo", response_model=CompraNu)
async def read_nucleo(p: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == p.id_compra)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/usuario", response_model=CompraUs)
async def read_usuario(p: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == p.id_compra)
    return await forwards.read(query)


# noinspection PyTypeChecker
@router.get("/estado", response_model=CompraEs)
async def read_estado(p: CompraId, db: Session = Depends(get_db)):
    query = db.query(CompraS).filter(CompraS.id_compra == p.id_compra)
    return await forwards.read(query)
