import sqlite3

DB_NAME = "pacientes.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
        apellido_nombre TEXT NOT NULL,
        genero TEXT NOT NULL,
        fecha_nacimiento TEXT NOT NULL,
        edad INTEGER NOT NULL,
        ff TEXT,
        dni TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atenciones (
        id_atencion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        fecha_consulta TEXT NOT NULL,
        tipo_servicio TEXT NOT NULL,
        FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_atencion (
        id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
        id_atencion INTEGER NOT NULL,
        campo TEXT NOT NULL,
        valor TEXT,
        FOREIGN KEY (id_atencion) REFERENCES atenciones(id_atencion)
    )
    """)

    conn.commit()
    conn.close()


def buscar_paciente_por_dni(dni):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id_paciente, apellido_nombre, genero, fecha_nacimiento, edad, ff, dni
    FROM pacientes
    WHERE dni = ?
    """, (dni,))

    paciente = cursor.fetchone()
    conn.close()
    return paciente


def insertar_paciente(apellido_nombre, genero, fecha_nacimiento, edad, ff, dni):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pacientes (apellido_nombre, genero, fecha_nacimiento, edad, ff, dni)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (apellido_nombre, genero, fecha_nacimiento, edad, ff, dni))

    id_paciente = cursor.lastrowid
    conn.commit()
    conn.close()

    return id_paciente


def obtener_o_crear_paciente(apellido_nombre, genero, fecha_nacimiento, edad, ff, dni):
    paciente = buscar_paciente_por_dni(dni)

    if paciente:
        return paciente[0]

    return insertar_paciente(apellido_nombre, genero, fecha_nacimiento, edad, ff, dni)


def insertar_atencion(id_paciente, fecha_consulta, tipo_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO atenciones (id_paciente, fecha_consulta, tipo_servicio)
    VALUES (?, ?, ?)
    """, (id_paciente, fecha_consulta, tipo_servicio))

    id_atencion = cursor.lastrowid
    conn.commit()
    conn.close()

    return id_atencion


def insertar_detalle(id_atencion, campo, valor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO detalle_atencion (id_atencion, campo, valor)
    VALUES (?, ?, ?)
    """, (id_atencion, campo, valor))

    conn.commit()
    conn.close()

def existe_atencion_duplicada(id_paciente, fecha_consulta, tipo_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1
    FROM atenciones
    WHERE id_paciente = ?
      AND fecha_consulta = ?
      AND tipo_servicio = ?
    LIMIT 1
    """, (id_paciente, fecha_consulta, tipo_servicio))

    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def obtener_registros():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        a.id_atencion,
        p.apellido_nombre,
        p.genero,
        p.fecha_nacimiento,
        p.edad,
        p.ff,
        p.dni,
        a.fecha_consulta,
        a.tipo_servicio
    FROM atenciones a
    INNER JOIN pacientes p
        ON a.id_paciente = p.id_paciente
    ORDER BY a.id_atencion DESC
    """)

    registros_base = cursor.fetchall()
    registros_completos = []

    for fila in registros_base:
        id_atencion = fila[0]

        cursor.execute("""
        SELECT campo, valor
        FROM detalle_atencion
        WHERE id_atencion = ?
        """, (id_atencion,))

        detalles = cursor.fetchall()

        detalle_texto = " | ".join([f"{campo}: {valor}" for campo, valor in detalles])

        registros_completos.append(fila + (detalle_texto,))

    conn.close()
    return registros_completos

def obtener_atencion_por_id(id_atencion):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        a.id_atencion,
        p.id_paciente,
        p.apellido_nombre,
        p.genero,
        p.fecha_nacimiento,
        p.edad,
        p.ff,
        p.dni,
        a.fecha_consulta,
        a.tipo_servicio
    FROM atenciones a
    INNER JOIN pacientes p
        ON a.id_paciente = p.id_paciente
    WHERE a.id_atencion = ?
    """, (id_atencion,))

    atencion = cursor.fetchone()

    cursor.execute("""
    SELECT campo, valor
    FROM detalle_atencion
    WHERE id_atencion = ?
    """, (id_atencion,))

    detalles = cursor.fetchall()

    conn.close()
    return atencion, detalles


def actualizar_paciente(id_paciente, apellido_nombre, genero, fecha_nacimiento, edad, ff, dni):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pacientes
    SET apellido_nombre = ?, genero = ?, fecha_nacimiento = ?, edad = ?, ff = ?, dni = ?
    WHERE id_paciente = ?
    """, (apellido_nombre, genero, fecha_nacimiento, edad, ff, dni, id_paciente))

    conn.commit()
    conn.close()


def actualizar_atencion(id_atencion, fecha_consulta, tipo_servicio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE atenciones
    SET fecha_consulta = ?, tipo_servicio = ?
    WHERE id_atencion = ?
    """, (fecha_consulta, tipo_servicio, id_atencion))

    conn.commit()
    conn.close()


def eliminar_detalles_atencion(id_atencion):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM detalle_atencion
    WHERE id_atencion = ?
    """, (id_atencion,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos y tablas creadas correctamente.")