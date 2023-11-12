import asyncio
import os

import uvicorn
from fastapi import FastAPI
from starlette.responses import FileResponse
from database import engine, Base
from router import api_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from service.uic import actualizar_pass_hash
from service.xutil import sync_all, sync_all_bd, sync_reset, sync_import

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_credentials=True,  allow_methods=["GET", "POST", "DELETE", "PUT"],
                   allow_headers=["*"], allow_origins=["*"])


@app.get('/')
async def read_root():
    return "API TeToca"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('public/tetoca.png')


app.include_router(api_router)


async def main():
    # await actualizar_pass_hash()
    # await sync_all()
    await sync_reset()
    await sync_import()
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    ssl_keyfile = os.getenv('SSLKEY') if os.getenv('SSLKEY') else None
    ssl_certfile = os.getenv('SSLCER') if os.getenv('SSLCER') else None
    config = uvicorn.Config("main:app", host=host, port=port, reload=True, ssl_keyfile=ssl_keyfile,
                            ssl_certfile=ssl_certfile)
    server = uvicorn.Server(config)
    # await sync_all_bd()
    await server.serve()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
