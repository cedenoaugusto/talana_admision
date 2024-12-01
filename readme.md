## Prueba de admision para el ingreso a Talana

Consiste en un desafio de una API para RRHH.

## Database
Usa SQL Lite, y el programa se encarga de crear la BBDD la primera vez, junto con las tablas necesarias.

Dentro de la carpeta database_demo se encuentra el archivo: my_database.db
El cual contiene registros precargados, en caso de querer reutilizar los datos.

## Docker
La aplicacion esta dokerizada.
Puede levantar una version ejecutando el comando:
```
docker compose up -d --build
```

## Postman
Dentro de la carpeta documentos se encuentra una coleccion para hacer pruebas a los diferentes endpoints.
[Postman](https://www.postman.com/downloads/)

## Documentacion
La documentacion esta en swagger, la cual estara disponible una vez que la api se este ejecutando.
http://127.0.0.1:8000/docs