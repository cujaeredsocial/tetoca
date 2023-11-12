from modules.autenticar import get_password_hash


async def actualizar_pass_hash():
        import psycopg2
        from database import user, dbs, passw, server, port
        conn = psycopg2.connect(dbname=dbs, user=user, password=passw, host=server, port=port)

        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT ci FROM usuarios")
            for fila in cursor.fetchall():
                ci = fila[0]
                nuevo_ci = await get_password_hash(ci)
                sql = "UPDATE usuarios SET hash_clave = %s WHERE ci = %s"
                cursor.execute(sql, (nuevo_ci, ci))
                print(ci)
                conn.commit()
            print("Todos los datos en la tabla usuario ha sido actualizado")
        except psycopg2.Error as e:
            conn.rollback()
            print("Error al cambiar datos de la tabla:", e)
        finally:
            cursor.close()
            conn.close()
