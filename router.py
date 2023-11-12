from fastapi import APIRouter

from modules import (autenticar, cadenas, provincias, municipios, tiendas, oficinas, bodegas, estados,
                     consumidores, responsables, oficodas, categorias, nucleos, roles,
                     productos, subofertas, ofertas, ciclos, usuarios, compras)

api_router = APIRouter()

api_router.include_router(autenticar.router)
api_router.include_router(provincias.router, prefix="/provincias", tags=["/provincias"])
api_router.include_router(municipios.router, prefix="/municipios", tags=["/municipios"])
api_router.include_router(cadenas.router, prefix="/cadenas", tags=["/cadenas"])
api_router.include_router(tiendas.router, prefix="/tiendas", tags=["/tiendas"])
api_router.include_router(oficinas.router, prefix="/oficinas", tags=["/oficinas"])
api_router.include_router(bodegas.router, prefix="/bodegas", tags=["/bodegas"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["/categorias"])
api_router.include_router(estados.router, prefix="/estados", tags=["/estados"])
api_router.include_router(nucleos.router, prefix="/nucleos", tags=["/nucleos"])
api_router.include_router(roles.router, prefix="/roles", tags=["/roles"])
api_router.include_router(productos.router, prefix="/productos", tags=["/productos"])
api_router.include_router(subofertas.router, prefix="/subofertas", tags=["/subofertas"])
api_router.include_router(ofertas.router, prefix="/ofertas", tags=["/ofertas"])
api_router.include_router(ciclos.router, prefix="/ciclos", tags=["/ciclos"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["/usuarios"])
api_router.include_router(oficodas.router, prefix="/oficodas", tags=["/responsables"])
api_router.include_router(responsables.router, prefix="/responsables", tags=["/responsables"])
api_router.include_router(consumidores.router, prefix="/consumidores", tags=["/consumidores"])
api_router.include_router(compras.router, prefix="/compras", tags=["/compras"])
