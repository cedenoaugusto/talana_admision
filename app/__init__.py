import sqlite3

connection = sqlite3.connect("my_database.db")

cursor = connection.cursor()

#region creacion de tablas
cursor.execute("PRAGMA foreign_keys = ON;") # Para habilitar las llaves foraneas

create_table_query = """
CREATE TABLE IF NOT EXISTS tbl_usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    email TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo'
);
"""

cursor.execute(create_table_query)
create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pregunta TEXT NOT NULL,
    dificultad TEXT NOT NULL,
    categoria TEXT NOT NULL,
    puntaje INTEGER NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo'
);
"""
cursor.execute(create_table_query)

create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    respuesta TEXT NOT NULL,
    es_correcta BOOLEAN NOT NULL,
    pregunta_id INTEGER NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo',
    FOREIGN KEY (pregunta_id) REFERENCES tbl_preguntas(id)
);
"""
cursor.execute(create_table_query)

create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_trivias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NULL,
    estado TEXT NOT NULL DEFAULT 'activo'
);
"""
cursor.execute(create_table_query)

create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_trivias_preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trivia_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    FOREIGN KEY (trivia_id) REFERENCES tbl_trivias(id),
    FOREIGN KEY (pregunta_id) REFERENCES tbl_preguntas(id)
);
"""
cursor.execute(create_table_query)

create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_trivias_usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trivia_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (trivia_id) REFERENCES tbl_trivias(id),
    FOREIGN KEY (usuario_id) REFERENCES tbl_usuarios(id)
);
"""
cursor.execute(create_table_query)

create_table_query ="""
CREATE TABLE IF NOT EXISTS tbl_trivias_respondidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trivia_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    respuesta_id INTEGER NOT NULL,
    puntaje INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (trivia_id) REFERENCES tbl_trivias(id),
    FOREIGN KEY (usuario_id) REFERENCES tbl_usuarios(id),
    FOREIGN KEY (pregunta_id) REFERENCES tbl_preguntas(id),
    FOREIGN KEY (respuesta_id) REFERENCES tbl_respuestas(id)
);
"""
cursor.execute(create_table_query)
#endregion


connection.commit()
connection.close()

