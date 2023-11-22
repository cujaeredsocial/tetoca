import asyncio
import os
import argparse

import uvicorn
from fastapi import FastAPI
from starlette.responses import FileResponse
from database import engine, Base
from router import api_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from service.uic import actualizar_pass_hash, vinculacion
from service.xutil import sync_all, sync_all_bd, sync_reset, sync_import, sync_cerodb, info

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_credentials=True,  allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH"],
                   allow_headers=["*"], allow_origins=["*"])


@app.get('/')
async def read_root():
    return "API TeToca"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('public/tetoca.png')


app.include_router(api_router)


async def main():
    parser = argparse.ArgumentParser(description='Api Tetoca')
    parser.add_argument('--vincularse', action='store_true', help='Toma excel de vinculacion de datos')
    parser.add_argument('--actualizarhash', action='store_true', help='Revisa usuarios aún no activos y crea contraseñas seguras')
    parser.add_argument('--descargaoregi', action='store_true', help='Descarga datos de oregi')
    parser.add_argument('--revisarbd', action='store_true', help='Si existen archivo para poblar base de datos')
    parser.add_argument('--cerobd', action='store_true', help='Elimina el contenido de la base de datos')
    parser.add_argument('--info', action='store_true', help='Información del Sistema')

    args = parser.parse_args()

    if args.vincularse:
        await vinculacion()
    elif args.actualizarhash:
        await actualizar_pass_hash()
    elif args.descargaoregi:
        await sync_all()
        await sync_all_bd()
    elif args.revisarbd:
        await sync_reset()
        await sync_import()
    elif args.cerobd:
        await sync_cerodb()
    elif args.info:
        await info()
    else:
        print("No se proporcionó ninguna bandera")
        host = os.getenv('HOST')
        port = int(os.getenv('PORT'))
        ssl_keyfile = os.getenv('SSLKEY') if os.getenv('SSLKEY') else None
        ssl_certfile = os.getenv('SSLCER') if os.getenv('SSLCER') else None
        config = uvicorn.Config("main:app", host=host, port=port, reload=True, ssl_keyfile=ssl_keyfile,
                                ssl_certfile=ssl_certfile)
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
