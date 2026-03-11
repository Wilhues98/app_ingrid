import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import obtener_registros, obtener_atencion_por_id
from config_servicios import SERVICIOS
from excel_export import exportar_a_excel
from registro_ui import abrir_ventana_registro


def abrir_ventana_reportes():
    ventana = tk.Toplevel()
    ventana.title("Registros guardados")
    ventana.geometry("1350x650")
    ventana.resizable(True, True)

    def convertir_fecha(texto_fecha):
        try:
            return datetime.strptime(texto_fecha, "%d/%m/%Y")
        except ValueError:
            return None

    def cargar_registros(registros):
        for item in tabla.get_children():
            tabla.delete(item)

        for fila in registros:
            tabla.insert("", "end", values=fila)

    def obtener_registros_filtrados():
        nombre_filtro = entry_nombre.get().strip().lower()
        dni_filtro = entry_dni.get().strip()
        servicio_filtro = combo_servicio.get().strip()
        fecha_desde = convertir_fecha(date_desde.get().strip())
        fecha_hasta = convertir_fecha(date_hasta.get().strip())

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            messagebox.showwarning(
                "Rango inválido",
                "La fecha inicial no puede ser mayor que la fecha final."
            )
            return None

        registros = obtener_registros()
        registros_filtrados = []

        for fila in registros:
            id_atencion = str(fila[0])
            apellido_nombre = str(fila[1])
            genero = str(fila[2])
            fecha_nacimiento = str(fila[3])
            edad = str(fila[4])
            ff = str(fila[5])
            dni = str(fila[6])
            fecha_consulta = str(fila[7])
            tipo_servicio = str(fila[8])
            detalle = str(fila[9])

            fecha_consulta_dt = convertir_fecha(fecha_consulta)

            if nombre_filtro and nombre_filtro not in apellido_nombre.lower():
                continue

            if dni_filtro and dni_filtro not in dni:
                continue

            if servicio_filtro and servicio_filtro != tipo_servicio:
                continue

            if fecha_desde and fecha_consulta_dt and fecha_consulta_dt < fecha_desde:
                continue

            if fecha_hasta and fecha_consulta_dt and fecha_consulta_dt > fecha_hasta:
                continue

            registros_filtrados.append((
                id_atencion,
                apellido_nombre,
                genero,
                fecha_nacimiento,
                edad,
                ff,
                dni,
                fecha_consulta,
                tipo_servicio,
                detalle
            ))

        return registros_filtrados

    def aplicar_filtros():
        registros_filtrados = obtener_registros_filtrados()
        if registros_filtrados is not None:
            cargar_registros(registros_filtrados)

    def limpiar_filtros():
        entry_nombre.delete(0, tk.END)
        entry_dni.delete(0, tk.END)
        combo_servicio.set("")
        date_desde.set_date(fecha_actual)
        date_hasta.set_date(fecha_actual)
        cargar_registros(obtener_registros())

    def refrescar_tabla():
        registros_filtrados = obtener_registros_filtrados()
        if registros_filtrados is None:
            cargar_registros(obtener_registros())
        else:
            cargar_registros(registros_filtrados)

    def ver_detalle():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Debe seleccionar un registro.")
            return

        valores = tabla.item(seleccion[0], "values")

        ventana_detalle = tk.Toplevel(ventana)
        ventana_detalle.title("Detalle de la atención")
        ventana_detalle.geometry("700x500")
        ventana_detalle.resizable(False, False)

        frame = tk.LabelFrame(ventana_detalle, text="Información de la atención", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        etiquetas = [
            ("ID", valores[0]),
            ("APELLIDO Y NOMBRE", valores[1]),
            ("GÉNERO", valores[2]),
            ("FECHA DE NACIMIENTO", valores[3]),
            ("EDAD", valores[4]),
            ("FF", valores[5]),
            ("DNI", valores[6]),
            ("FECHA DE CONSULTA", valores[7]),
            ("TIPO DE SERVICIO", valores[8]),
            ("DETALLE", valores[9]),
        ]

        for i, (campo, valor) in enumerate(etiquetas):
            tk.Label(
                frame,
                text=f"{campo}:",
                font=("Arial", 10, "bold"),
                anchor="w"
            ).grid(row=i, column=0, sticky="nw", padx=5, pady=6)

            if campo == "DETALLE":
                txt_detalle = tk.Text(frame, width=55, height=8, wrap="word")
                txt_detalle.grid(row=i, column=1, sticky="w", padx=5, pady=6)
                txt_detalle.insert("1.0", valor)
                txt_detalle.config(state="disabled")
            else:
                tk.Label(
                    frame,
                    text=valor,
                    anchor="w",
                    justify="left",
                    wraplength=400
                ).grid(row=i, column=1, sticky="w", padx=5, pady=6)

        btn_cerrar_detalle = tk.Button(
            ventana_detalle,
            text="Cerrar",
            width=15,
            command=ventana_detalle.destroy
        )
        btn_cerrar_detalle.pack(pady=10)

    def editar_registro():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Debe seleccionar un registro.")
            return

        valores = tabla.item(seleccion[0], "values")
        id_atencion = valores[0]

        atencion, detalles = obtener_atencion_por_id(id_atencion)

        if not atencion:
            messagebox.showerror("Error", "No se pudo cargar la atención seleccionada.")
            return

        datos_atencion = {
            "id_atencion": atencion[0],
            "id_paciente": atencion[1],
            "apellido_nombre": atencion[2],
            "genero": atencion[3],
            "fecha_nacimiento": atencion[4],
            "edad": atencion[5],
            "ff": atencion[6],
            "dni": atencion[7],
            "fecha_consulta": atencion[8],
            "tipo_servicio": atencion[9],
            "detalles": {campo: valor for campo, valor in detalles}
        }

        abrir_ventana_registro(
            modo="editar",
            datos_atencion=datos_atencion,
            callback_actualizacion=refrescar_tabla
        )

    titulo = tk.Label(
        ventana,
        text="Listado de Registros",
        font=("Arial", 16, "bold")
    )
    titulo.pack(pady=10)

    frame_filtros = tk.LabelFrame(ventana, text="Filtros", padx=10, pady=10)
    frame_filtros.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_filtros, text="Apellido y nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nombre = tk.Entry(frame_filtros, width=25)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_filtros, text="DNI:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    entry_dni = tk.Entry(frame_filtros, width=18)
    entry_dni.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_filtros, text="Tipo de servicio:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
    combo_servicio = ttk.Combobox(
        frame_filtros,
        values=[""] + list(SERVICIOS.keys()),
        state="readonly",
        width=22
    )
    combo_servicio.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(frame_filtros, text="Fecha desde:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    date_desde = DateEntry(
        frame_filtros,
        width=22,
        date_pattern="dd/mm/yyyy"
    )
    date_desde.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_filtros, text="Fecha hasta:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    date_hasta = DateEntry(
        frame_filtros,
        width=22,
        date_pattern="dd/mm/yyyy"
    )
    date_hasta.grid(row=1, column=3, padx=5, pady=5)

    fecha_actual = date_desde.get_date()

    btn_filtrar = tk.Button(frame_filtros, text="Filtrar", width=12, command=aplicar_filtros)
    btn_filtrar.grid(row=1, column=4, padx=10, pady=5)

    btn_limpiar = tk.Button(frame_filtros, text="Limpiar filtros", width=15, command=limpiar_filtros)
    btn_limpiar.grid(row=1, column=5, padx=10, pady=5)

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

    columnas = (
        "ID",
        "APELLIDO Y NOMBRE",
        "GÉNERO",
        "FECHA NACIMIENTO",
        "EDAD",
        "FF",
        "DNI",
        "FECHA CONSULTA",
        "TIPO SERVICIO",
        "DETALLE"
    )

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor="center")

    tabla.column("ID", width=60)
    tabla.column("APELLIDO Y NOMBRE", width=220)
    tabla.column("EDAD", width=60)
    tabla.column("FF", width=100)
    tabla.column("DNI", width=100)
    tabla.column("TIPO SERVICIO", width=140)
    tabla.column("DETALLE", width=350, anchor="w")

    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)

    tabla.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    tabla.pack(side="top", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    cargar_registros(obtener_registros())

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    btn_ver_detalle = tk.Button(
        frame_botones,
        text="Ver detalle",
        width=18,
        command=ver_detalle
    )
    btn_ver_detalle.grid(row=0, column=0, padx=10)

    btn_editar = tk.Button(
        frame_botones,
        text="Editar",
        width=18,
        command=editar_registro
    )
    btn_editar.grid(row=0, column=1, padx=10)

    btn_exportar = tk.Button(
        frame_botones,
        text="Exportar a Excel",
        width=20,
        command=lambda: exportar_a_excel([
            tabla.item(item)["values"] for item in tabla.get_children()
        ])
    )
    btn_exportar.grid(row=0, column=2, padx=10)

    btn_cerrar = tk.Button(frame_botones, text="Cerrar", width=15, command=ventana.destroy)
    btn_cerrar.grid(row=0, column=3, padx=10)