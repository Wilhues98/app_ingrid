import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from config_servicios import SERVICIOS
from database import (
    buscar_paciente_por_dni,
    obtener_o_crear_paciente,
    insertar_atencion,
    insertar_detalle,
    existe_atencion_duplicada,
    actualizar_paciente,
    actualizar_atencion,
    eliminar_detalles_atencion
)


def abrir_ventana_registro(modo="nuevo", datos_atencion=None, callback_actualizacion=None):
    ventana = tk.Toplevel()
    ventana.title("Nuevo registro de paciente" if modo == "nuevo" else "Editar registro de paciente")
    ventana.geometry("800x680")
    ventana.resizable(False, False)

    campos_detalle = {}
    id_atencion_edicion = None
    id_paciente_edicion = None

    def calcular_edad(fecha_nacimiento_str, fecha_consulta_str):
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%d/%m/%Y")
            fecha_consulta = datetime.strptime(fecha_consulta_str, "%d/%m/%Y")

            edad = fecha_consulta.year - fecha_nacimiento.year

            if (fecha_consulta.month, fecha_consulta.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1

            return edad
        except ValueError:
            return ""

    def actualizar_edad(event=None):
        fecha_nacimiento = fecha_nacimiento_entry.get().strip()
        fecha_consulta = fecha_consulta_entry.get().strip()

        edad = calcular_edad(fecha_nacimiento, fecha_consulta)

        entry_edad.config(state="normal")
        entry_edad.delete(0, tk.END)

        if edad != "":
            entry_edad.insert(0, str(edad))

        entry_edad.config(state="readonly")

    def mostrar_mensaje_inicial_detalle():
        for widget in frame_detalle_interno.winfo_children():
            widget.destroy()

        label_info = tk.Label(
            frame_detalle_interno,
            text="Seleccione un servicio para mostrar sus campos específicos.",
            fg="gray"
        )
        label_info.grid(row=0, column=0, sticky="w", padx=5, pady=5)

    def actualizar_campos_detalle(event=None, valores_precargados=None):
        for widget in frame_detalle_interno.winfo_children():
            widget.destroy()

        campos_detalle.clear()

        servicio = combo_servicio.get()
        detalles = SERVICIOS.get(servicio, [])

        if not detalles:
            label_sin_detalle = tk.Label(
                frame_detalle_interno,
                text="Este servicio no tiene campos adicionales.",
                fg="gray"
            )
            label_sin_detalle.grid(row=0, column=0, sticky="w", padx=5, pady=5)
            return

        valores_precargados = valores_precargados or {}

        for i, campo in enumerate(detalles):
            tk.Label(frame_detalle_interno, text=f"{campo}:").grid(
                row=i, column=0, sticky="w", padx=5, pady=5
            )

            entry = tk.Entry(frame_detalle_interno, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)

            if campo in valores_precargados:
                entry.insert(0, valores_precargados[campo])

            campos_detalle[campo] = entry

    def bloquear_datos_paciente():
        entry_nombre.config(state="disabled")
        combo_genero.config(state="disabled")
        fecha_nacimiento_entry.config(state="disabled")
        entry_edad.config(state="readonly")
        entry_ff.config(state="disabled")

    def habilitar_datos_paciente():
        entry_nombre.config(state="normal")
        combo_genero.config(state="readonly")
        fecha_nacimiento_entry.config(state="normal")
        entry_ff.config(state="normal")

    def limpiar_datos_paciente():
        entry_nombre.config(state="normal")
        combo_genero.config(state="readonly")
        fecha_nacimiento_entry.config(state="normal")
        entry_ff.config(state="normal")
        entry_edad.config(state="normal")

        entry_nombre.delete(0, tk.END)
        combo_genero.set("")
        fecha_nacimiento_entry.set_date(fecha_actual)
        entry_edad.delete(0, tk.END)
        entry_ff.delete(0, tk.END)

        entry_edad.config(state="readonly")

    def limpiar_formulario():
        if modo == "editar":
            ventana.destroy()
            return

        entry_dni.config(state="normal")
        entry_dni.delete(0, tk.END)
        limpiar_datos_paciente()

        fecha_consulta_entry.config(state="normal")
        fecha_consulta_entry.set_date(fecha_actual)
        combo_servicio.set("")

        campos_detalle.clear()
        mostrar_mensaje_inicial_detalle()
        bloquear_datos_paciente()
        actualizar_edad()
        entry_dni.focus_set()

    def procesar_dni(event=None):
        if modo == "editar":
            return

        dni = entry_dni.get().strip()

        limpiar_datos_paciente()

        if not dni:
            bloquear_datos_paciente()
            actualizar_edad()
            return

        if not dni.isdigit():
            messagebox.showwarning("Aviso", "El DNI solo debe contener números.")
            entry_dni.focus_set()
            bloquear_datos_paciente()
            actualizar_edad()
            return

        if len(dni) != 8:
            messagebox.showwarning("Aviso", "El DNI debe tener exactamente 8 dígitos.")
            entry_dni.focus_set()
            bloquear_datos_paciente()
            actualizar_edad()
            return

        paciente = buscar_paciente_por_dni(dni)

        if paciente:
            _, apellido_nombre, genero, fecha_nacimiento, edad, ff, _ = paciente

            habilitar_datos_paciente()

            entry_nombre.insert(0, apellido_nombre)
            combo_genero.set(genero)
            fecha_nacimiento_entry.set_date(fecha_nacimiento)
            entry_ff.insert(0, ff if ff else "")

            entry_nombre.config(state="readonly")
            combo_genero.config(state="disabled")
            fecha_nacimiento_entry.config(state="disabled")
            entry_ff.config(state="readonly")
        else:
            habilitar_datos_paciente()

        actualizar_edad()

    def guardar_registro():
        nonlocal id_atencion_edicion, id_paciente_edicion

        apellido_nombre = entry_nombre.get().strip()
        genero = combo_genero.get().strip()
        fecha_nacimiento = fecha_nacimiento_entry.get().strip()
        edad = entry_edad.get().strip()
        ff = entry_ff.get().strip()
        dni = entry_dni.get().strip()
        fecha_consulta = fecha_consulta_entry.get().strip()
        tipo_servicio = combo_servicio.get().strip()

        if not dni:
            messagebox.showerror("Error", "Debe ingresar el DNI.")
            return

        if not dni.isdigit():
            messagebox.showerror("Error", "El DNI solo debe contener números.")
            return

        if len(dni) != 8:
            messagebox.showerror("Error", "El DNI debe tener exactamente 8 dígitos.")
            return

        if not apellido_nombre:
            messagebox.showerror("Error", "Debe ingresar Apellido y nombre.")
            return

        if not genero:
            messagebox.showerror("Error", "Debe seleccionar el género.")
            return

        if not fecha_nacimiento:
            messagebox.showerror("Error", "Debe ingresar la fecha de nacimiento.")
            return

        if not edad:
            messagebox.showerror("Error", "No se pudo calcular la edad.")
            return

        if not fecha_consulta:
            messagebox.showerror("Error", "Debe ingresar la fecha de consulta.")
            return

        if not tipo_servicio:
            messagebox.showerror("Error", "Debe seleccionar el tipo de servicio.")
            return

        try:
            edad_int = int(edad)
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser numérica.")
            return

        try:
            if modo == "nuevo":
                id_paciente = obtener_o_crear_paciente(
                    apellido_nombre,
                    genero,
                    fecha_nacimiento,
                    edad_int,
                    ff,
                    dni
                )

                if existe_atencion_duplicada(id_paciente, fecha_consulta, tipo_servicio):
                    messagebox.showwarning(
                        "Registro duplicado",
                        "Ya existe una atención registrada para este paciente con la misma fecha y tipo de servicio."
                    )
                    return

                id_atencion = insertar_atencion(
                    id_paciente,
                    fecha_consulta,
                    tipo_servicio
                )

                for campo, entry in campos_detalle.items():
                    valor = entry.get().strip()
                    insertar_detalle(id_atencion, campo, valor)

                messagebox.showinfo("Éxito", "Registro guardado correctamente.")
                limpiar_formulario()

            else:
                if existe_atencion_duplicada(id_paciente_edicion, fecha_consulta, tipo_servicio):
                    atencion_original = datos_atencion["fecha_consulta"] == fecha_consulta and datos_atencion["tipo_servicio"] == tipo_servicio
                    if not atencion_original:
                        messagebox.showwarning(
                            "Registro duplicado",
                            "Ya existe una atención registrada para este paciente con la misma fecha y tipo de servicio."
                        )
                        return

                actualizar_paciente(
                    id_paciente_edicion,
                    apellido_nombre,
                    genero,
                    fecha_nacimiento,
                    edad_int,
                    ff,
                    dni
                )

                actualizar_atencion(
                    id_atencion_edicion,
                    fecha_consulta,
                    tipo_servicio
                )

                eliminar_detalles_atencion(id_atencion_edicion)

                for campo, entry in campos_detalle.items():
                    valor = entry.get().strip()
                    insertar_detalle(id_atencion_edicion, campo, valor)

                messagebox.showinfo("Éxito", "Registro actualizado correctamente.")

                if callback_actualizacion:
                    callback_actualizacion()

                ventana.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al guardar:\n{e}")

    titulo = tk.Label(
        ventana,
        text="Registro de Paciente" if modo == "nuevo" else "Edición de Registro",
        font=("Arial", 16, "bold")
    )
    titulo.pack(pady=10)

    frame_general = tk.LabelFrame(ventana, text="Datos generales", padx=10, pady=10)
    frame_general.pack(fill="x", padx=20, pady=10)

    tk.Label(frame_general, text="DNI:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_dni = tk.Entry(frame_general, width=40)
    entry_dni.grid(row=0, column=1, padx=5, pady=5)
    entry_dni.bind("<FocusOut>", procesar_dni)
    entry_dni.bind("<Return>", procesar_dni)

    tk.Label(frame_general, text="Apellido y nombre:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_nombre = tk.Entry(frame_general, width=40)
    entry_nombre.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_general, text="Género:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    combo_genero = ttk.Combobox(frame_general, values=["MASCULINO", "FEMENINO"], state="readonly", width=37)
    combo_genero.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_general, text="Fecha de nacimiento:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    fecha_nacimiento_entry = DateEntry(
        frame_general,
        width=37,
        date_pattern="dd/mm/yyyy"
    )
    fecha_nacimiento_entry.grid(row=3, column=1, padx=5, pady=5)
    fecha_nacimiento_entry.bind("<<DateEntrySelected>>", actualizar_edad)

    tk.Label(frame_general, text="Edad:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    entry_edad = tk.Entry(frame_general, width=40, state="readonly")
    entry_edad.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(frame_general, text="FF:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    entry_ff = tk.Entry(frame_general, width=40)
    entry_ff.grid(row=5, column=1, padx=5, pady=5)

    tk.Label(frame_general, text="Fecha de consulta:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    fecha_consulta_entry = DateEntry(
        frame_general,
        width=37,
        date_pattern="dd/mm/yyyy"
    )
    fecha_consulta_entry.grid(row=6, column=1, padx=5, pady=5)
    fecha_consulta_entry.bind("<<DateEntrySelected>>", actualizar_edad)

    fecha_actual = fecha_consulta_entry.get_date()
    actualizar_edad()

    tk.Label(frame_general, text="Tipo de servicio:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    combo_servicio = ttk.Combobox(
        frame_general,
        values=list(SERVICIOS.keys()),
        state="readonly",
        width=37
    )
    combo_servicio.grid(row=7, column=1, padx=5, pady=5)
    combo_servicio.bind("<<ComboboxSelected>>", actualizar_campos_detalle)

    frame_detalle = tk.LabelFrame(ventana, text="Detalle del servicio", padx=10, pady=10)
    frame_detalle.pack(fill="x", padx=20, pady=10)

    frame_detalle_interno = tk.Frame(frame_detalle)
    frame_detalle_interno.pack(fill="x")

    mostrar_mensaje_inicial_detalle()

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=20)

    btn_guardar = tk.Button(
        frame_botones,
        text="Guardar" if modo == "nuevo" else "Actualizar",
        width=15,
        command=guardar_registro
    )
    btn_guardar.grid(row=0, column=0, padx=10)

    btn_limpiar = tk.Button(
        frame_botones,
        text="Limpiar" if modo == "nuevo" else "Cancelar",
        width=15,
        command=limpiar_formulario
    )
    btn_limpiar.grid(row=0, column=1, padx=10)

    btn_cerrar = tk.Button(frame_botones, text="Cerrar", width=15, command=ventana.destroy)
    btn_cerrar.grid(row=0, column=2, padx=10)

    if modo == "nuevo":
        bloquear_datos_paciente()
        entry_dni.focus_set()

    if modo == "editar" and datos_atencion:
        id_atencion_edicion = datos_atencion["id_atencion"]
        id_paciente_edicion = datos_atencion["id_paciente"]

        habilitar_datos_paciente()

        entry_dni.insert(0, datos_atencion["dni"])
        entry_nombre.insert(0, datos_atencion["apellido_nombre"])
        combo_genero.set(datos_atencion["genero"])
        fecha_nacimiento_entry.set_date(datos_atencion["fecha_nacimiento"])
        entry_ff.insert(0, datos_atencion["ff"] if datos_atencion["ff"] else "")
        fecha_consulta_entry.set_date(datos_atencion["fecha_consulta"])
        combo_servicio.set(datos_atencion["tipo_servicio"])

        actualizar_edad()
        actualizar_campos_detalle(valores_precargados=datos_atencion["detalles"])

        entry_dni.config(state="disabled")