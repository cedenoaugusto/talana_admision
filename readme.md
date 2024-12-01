## Prueba de admision para el ingreso a Talana

Consiste en un desafio de una API para RRHH.

## Documentacion
http://127.0.0.1:8000/docs

## Database
Usa SQL Lite, y el programa se encarga de crear la BBDD la primera vez, junto con las tablas necesarias.

Dentro de la carpeta database_demo se encuentra el archivo: my_database.db
El cual contiene registros precargados, en caso de querer reutilizar los datos.

## Database
La aplicacion esta dokerizada.
Puede levantar una version ejecutando el comando:
```
docker compose up -d --build
```