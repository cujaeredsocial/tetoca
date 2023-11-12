import json
import os
import requests
from datetime import date


async def sync_reset():
    """
    Si existe un archivo tetoca.rar eso significa que se empezara un proceso de limpieza de la base de datos,
    por ende se elimina
    """
    archivo_rar = "tetoca.rar"
    if os.path.exists(archivo_rar):
        import psycopg2
        from database import user, dbs, passw, server, port
        conn = psycopg2.connect(dbname=dbs, user=user, password=passw, host=server, port=port)

        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )

            tables = cursor.fetchall()

            for table in tables:
                cursor.execute(f"DROP TABLE {table[0]} CASCADE")

            conn.commit()
            print("Todos los datos en las tablas han sido eliminados.")

        except psycopg2.Error as e:
            conn.rollback()
            print("Error al truncar las tablas:", e)

        finally:
            cursor.close()
            conn.close()


async def sync_import():
    """
    Si el archivo tetoca.rar está en la raíz del proyecto, esta función lo descomprime
    Si se encuentra  un sql o un backups lo ejecuta.
    """
    import patoolib

    archivo_rar = "tetoca.rar"
    if os.path.exists(archivo_rar):
        patoolib.extract_archive(archivo_rar)
        os.remove(archivo_rar)

    from database import user, dbs, passw, server, port

    sql_file_path = 'tetoca.sql'
    if os.path.exists(sql_file_path):
        import psycopg2
        conn = psycopg2.connect(dbname=dbs, user=user, password=passw, host=server, port=port)
        cursor = conn.cursor()

        with open(sql_file_path, 'r') as sql_file:
            sql_query = sql_file.read()

        cursor.execute(sql_query)
        conn.commit()
        conn.close()
        print("La restauración se ha completado exitosamente.")
        os.remove(sql_file_path)
        print(f"Eliminado fichero {sql_file_path}")

    backup_file_path = 'tetoca.backup'
    if os.path.exists(backup_file_path):
        import subprocess
        restore_command = f"pg_restore -h {server} -p {port} -U {user} -d {dbs} -v {backup_file_path}"
        try:
            print("restore_command")
            subprocess.run(restore_command, shell=True, check=True)
            print("La restauración se ha completado exitosamente.")
            os.remove(backup_file_path)
        except subprocess.CalledProcessError as e:
            print(f"Error al restaurar la base de datos: {e}")


async def sync_dpa(entidad, dat=date.today()):
    entidades = []
    try:
        with open(f"async/{dat} {entidad}.json", "r") as file:
            entidades = json.load(file)
    except (Exception,):
        try:
            headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + os.getenv('XUTIL_TOKEN_DPA')}
            url = os.getenv('XUTIL_API_DPA') + entidad + 's?atributos=*'
            response = requests.request("GET", url, headers=headers, data={})
            if response.status_code == 200:
                entidades = response.json()['data']
                with open(f"async/{dat} {entidad}.json", "w") as file:
                    json.dump(entidades, file, ensure_ascii=False, indent=3)
                print(entidad)
        except (Exception,):
            pass
    return entidades


async def sync_dcpr(entidad, contenedor, dat=date.today()):
    entidades = []
    try:
        with open(f"async/{dat} {entidad}.json", "r") as file:
            viejos = json.load(file)
    except (Exception,):
        viejos = []
    try:
        with open(f"async/{dat} {contenedor}.json", "r") as file:
            contenedores = json.load(file)
        entidades = []
        for conten in contenedores:
            conten_id = conten['id']
            existe = False
            for v in viejos:
                if v[f'{contenedor}_id'] == conten_id:
                    existe = True
                    break
            if not existe:
                try:
                    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + os.getenv('XUTIL_TOKEN_DCPR')}
                    url = f"https://apis-fuc.xutil.cu/api-dcpr-consulta/0.1.221112/api/v1/{entidad}s?{contenedor}_id={conten_id}"
                    response = requests.request("GET", url, headers=headers, data={})
                    if response.status_code == 200:
                        for entidada in response.json()['data']:
                            entidada[f'{contenedor}_id'] = conten_id
                            entidades.append(entidada)
                except(Exception,):
                    pass
        with open(f"async/{dat} {entidad}.json", "w") as file:
            json.dump(viejos + entidades, file, ensure_ascii=False, indent=3)

    except (Exception,):
        pass
    return viejos + entidades


async def sync_dcpr2(entidad='nucleo', contenedor='bodega', supercon='oficina', dat=date.today()):
    entidades = []
    try:
        with open(f"async/{dat} {entidad}.json", "r") as file:
            viejos = json.load(file)
    except (Exception,):
        viejos = []
    try:
        with open(f"async/{dat} {contenedor}.json", "r") as file:
            contenedores = json.load(file)
        entidades = []
        for conten in contenedores:
            conten_id = conten['id']
            supercon_id = conten[f'{supercon}_id']
            existe = False
            for v in viejos:
                if v[f'{contenedor}_id'] == conten_id and v[f'{supercon}_id'] == supercon:
                    existe = True
                    break
            if not existe:
                try:
                    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + os.getenv('XUTIL_TOKEN_DCPR')}
                    url = f"https://apis-fuc.xutil.cu/api-dcpr-consulta/0.1.221112/api/v1/listar-consumidores-{contenedor}?{supercon}_id={supercon_id}&{contenedor}_id={conten_id}"
                    response = requests.request("GET", url, headers=headers, data={})
                    if response.status_code == 200:
                        for entidada in response.json()['data']:
                            entidada[f'{contenedor}_id'] = conten_id
                            entidada[f'{supercon}_id'] = supercon_id
                            entidades.append(entidada)
                except(Exception,):
                    pass
        with open(f"async/{dat} {entidad}.json", "w") as file:
            json.dump(viejos + entidades, file, ensure_ascii=False, indent=3)

    except (Exception,):
        pass
    return viejos + entidades


async def sync_all():
    provincias = await sync_dpa(entidad='provincia')
    municipios = await sync_dpa(entidad='municipio')
    oficinas = await sync_dcpr(entidad='oficina', contenedor='municipio')
    bodegas = await sync_dcpr(entidad='bodega', contenedor='oficina')
    nucleo = await sync_dcpr2(entidad='nucleo', contenedor='bodega', supercon='oficina')


async def sync_all_bd():
    import psycopg2
    from database import user, dbs, passw, server, port
    conn = psycopg2.connect(dbname=dbs, user=user, password=passw, host=server, port=port)

    # Provincia
    """prov = dict()
    cursor = conn.cursor()
    insert_query = "INSERT INTO provincias (id_provincia, nombre, desac, siglas, ubicacion) VALUES (%s, %s,  %s, %s, %s)"

    with open("async/2023-10-22 provincia.json") as file:
        aux = json.load(file)

    for res in aux:
        prov[res['id']] = {'nombre':res['nombre'], 'desac': not res['activo'], 'siglas': res['siglas']}
        values = (res['id'], res['nombre'], not res['activo'], res['siglas'], res['ubicacion'])
        try:
            cursor.execute(insert_query, values)
        except (Exception,):
            print("Error")
    conn.commit()
    cursor.close()

    # Municipio
    muni = dict()
    cursor = conn.cursor()
    insert_query = ("INSERT INTO municipios (id_municipio, nombre, desac, siglas, ubicacion, id_provincia) "
                    "VALUES (%s, %s,  %s, %s, %s, %s)")

    with open("async/2023-10-22 municipio.json") as file:
        aux = json.load(file)

    for res in aux:
        muni[res['id']] = {'nombre': res['nombre'], 'desac': not res['activo'], 'siglas': res['siglas'],
                           'id_provincia': res['provincia_id']}
        values = (res['id'], res['nombre'], not res['activo'], res['siglas'], res['ubicacion'], res['provincia_id'])
        try:
            cursor.execute(insert_query, values)
        except (Exception,):
            print("Error")
    conn.commit()
    cursor.close()

    # Bodega
    bode = dict()
    cursor = conn.cursor()
    insert_query = ("INSERT INTO bodegas (id_bodega, numero, id_oficina, direccion, grupos_rs, es_especial, desac) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    with open("async/2023-10-22 bodega.json") as file:
        aux = json.load(file)

    for res in aux:
        bode[res['id']] = {'numero': res['numero'], 'id_oficina': res['oficina_id'], 'direccion': "",
                           'grupos_rs':"", 'es_especial':False, 'desac': False, }
        values = (res['id'], res['numero'], res['oficina_id'], "", "", False, False)
        try:
            cursor.execute(insert_query, values)
        except (Exception,):
            print("Error")
    conn.commit()
    cursor.close()"""

    # Nucleo
    cursor = conn.cursor()

    ## recorrer el fichero
    with open("async/2023-10-22 nucleo.json") as file:
        aux = json.load(file)

    for res in aux:
        cant = res['cons_cant']
        cant_user = 0
        cant_cons = 0
        ### crear el nucleo ya probado
        insert_query = ("INSERT INTO nucleos (numero, cant_miembros, cant_modulos, id_bodega) "
                        "VALUES (%s, %s, %s, %s) RETURNING id_nucleo")
        values = (res['numero_nucleo'], res['cons_cant'], 0, res['bodega_id'])
        try:
            cursor.execute(insert_query, values)
            id_nucleodb = cursor.fetchone()[0]
            conn.commit()
        except (Exception,):
            conn.rollback()
            select_query = "SELECT id_nucleo FROM nucleos WHERE numero LIKE %s and id_bodega= %s"
            values = (str(res['numero_nucleo']),res['bodega_id'])
            cursor.execute(select_query, values)
            id_nucleodb = cursor.fetchone()[0]
        # con el nucleo en existencia
        if id_nucleodb and res['cons_lista']:
            usuarios = list()
            id_jefenucleo = None

            ### recorrer lista de identificacion
            for user in json.loads(res['cons_lista']):
                ### crear los usuarios
                select_query = ("INSERT INTO usuarios (hash_clave, ci) VALUES (%s, %s) RETURNING id_usuario")
                values = (user['identidad_numero'], user['identidad_numero'])
                try:
                    cursor.execute(select_query, values)
                    usuariodb = cursor.fetchone()[0]
                    conn.commit()
                except (Exception,):
                    conn.rollback()
                    select_query = "SELECT id_usuario FROM usuarios WHERE ci LIKE %s"
                    values = (user['identidad_numero'],)
                    cursor.execute(select_query, values)
                    usuariodb = cursor.fetchone()[0]
                finally:
                    usuarios.append(usuariodb)
                    if user['jefe_nucleo']:
                        id_jefenucleo = usuariodb
            cant_user = len(usuarios)
            cant_cons = 0
            ### crear consumidores
            for user in usuarios:
                insert_query_us = ("INSERT INTO consumidores (id_usuario, id_nucleo, verificado) "
                                   "VALUES (%s, %s, %s) RETURNING id_consumidor")
                values_us = (user, id_nucleodb, True)
                try:
                    cursor.execute(insert_query_us, values_us)
                    id_consumidordb = cursor.fetchone()[0]
                    conn.commit()
                except (Exception,):
                    conn.rollback()
                    select_query = "SELECT id_consumidor FROM consumidores WHERE id_usuario = %s and id_nucleo = %s"
                    values = (user, id_nucleodb)
                    cursor.execute(select_query, values)
                    id_consumidordb = cursor.fetchone()[0]
                finally:
                    cant_cons = cant_cons + 1
                    id_consumidorjefe = id_consumidordb if id_jefenucleo and user == id_jefenucleo else None
            ## consumidor jefe
            if id_consumidorjefe:
                insert_query_us = f"UPDATE nucleos SET id_consumidor_jefe = %s WHERE id_nucleo = %s"
                values_us = (id_consumidorjefe, id_nucleodb)
                try:
                    cursor.execute(insert_query_us, values_us)
                    conn.commit()
                except (Exception,):
                    conn.rollback()
                    print(f"Error con jefe consumidor {id_consumidorjefe} en nucleo {id_nucleodb}")
        if cant != cant_cons or cant != cant_user:
            print(f"Error del sistema no coincide usuario y consumidore para el nucleo {id_nucleodb}");

    cursor.close()


async def sync_json_provincia(conn, entidades):
    cursor = conn.cursor()
    insert_query = "INSERT INTO provincias (id_provincia, nombre, desac, siglas, ubicacion) VALUES (%s, %s,  %s, %s, %s)"
    select_query = "SELECT id_provincia FROM provincias WHERE id_provincia = %s"
    for res in entidades:
        try:
            values = (res['id'], res['nombre'], not res['activo'], res['siglas'], res['ubicacion'])
            cursor.execute(insert_query, values)
            conn.commit()
        except (Exception,):
            conn.rollback()
            values = (res['id'],)
            cursor.execute(select_query, values)
            id_consumer = cursor.fetchone()[0]
            if id_consumer:
                print(f"Provincia ya existe {res['id']}:{res['nombre']}")
            else:
                print(f"Error en provincia {res['id']}:{res['nombre']}")
    cursor.close()

async def sync_json_municipio(conn, entidades):
    cursor = conn.cursor()
    insert_query = ("INSERT INTO municipios (id_municipio, nombre, desac, siglas, ubicacion, id_provincia) "
                    "VALUES (%s, %s,  %s, %s, %s, %s)")

    with open("async/2023-10-22 municipio.json") as file:
        aux = json.load(file)

    for res in aux:
        muni[res['id']] = {'nombre': res['nombre'], 'desac': not res['activo'], 'siglas': res['siglas'],
                           'id_provincia': res['provincia_id']}
        values = (res['id'], res['nombre'], not res['activo'], res['siglas'], res['ubicacion'], res['provincia_id'])
        try:
            cursor.execute(insert_query, values)
        except (Exception,):
            print("Error")
    conn.commit()
    cursor.close()