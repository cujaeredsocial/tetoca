# tetoca
- Crear una sección para el trabajo con esta api `screen -S TeToca`
- Actualizar el SO `sudo apt update`, luego instalar postgres `sudo apt install postgresql postgresql-contrib` 
- Cambiar el usuario `sudo -i -u postgres`, crear una base de datos `createdb tetoca`,
 para cerrar varias secciones de una base de datos `REVOKE CONNECT ON DATABASE tetoca FROM public;`, 
 para eliminar la base de datos `dropdb tetoca`
- Pone contraseña al usuario postgres `ALTER USER postgres PASSWORD 'postgres';`
- Entrar en el sistema de gestión `psql tetoca`, si queremos restaurar la bd sería 
  `psql -U postgres -W -h 127.0.0.1 tetoca < psql_collection.backup`. Recomendado a leer `https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04-es`
- Ponerse en la carpeta de tetoca y crear maquina virtual `python -m venv .venv`
- Activar la maquina virtual `source .venv/bin/activate`
- Comprobar el entorno virtual `which python` 
- Tener presente que el starlette~=0.27.0 y psycopg2-binary~=2.9.7 debe estar asi en linux
- Instalar los archivos necesario `pip install -r requirements.txt`
- Ejecutar python main.py 
- Será necesario automatizar el trabajo para actualizar la BD dado el script que se guarda llamado psql_collection.backup, luego entrar en el modo virtual de python, instalar las librerias del requirements y por úlitmo mandar a ejecutar el servidor.

- Para certificados https autofirmados, instalar mkcert usando Chocolatey`choco install mkcert`, 
generar el certificado y agregarlo `mkcert -install`, `mkcert localhost 127.0.0.1 ::1`. Con ello el certificado está en 
"localhost+2.pem" y la clave en "localhost+2-key.pem" en nuestra carpeta de proyecto.