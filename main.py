import tkinter as tk
from database import crear_tablas
from registro_ui import abrir_ventana_registro
from reportes_ui import abrir_ventana_reportes


def abrir_ventana_principal():
    ventana = tk.Tk()
    ventana.title("Sistema de Registro de Pacientes")
    ventana.geometry("600x400")
    ventana.resizable(False, False)

    titulo = tk.Label(
        ventana,
        text="Sistema de Registro de Pacientes",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=20)

    subtitulo = tk.Label(
        ventana,
        text="Seleccione una opción",
        font=("Arial", 12)
    )
    subtitulo.pack(pady=10)

    btn_nuevo = tk.Button(
        ventana,
        text="Nuevo registro",
        width=20,
        height=2,
        command=abrir_ventana_registro
    )
    btn_nuevo.pack(pady=10)

    btn_ver = tk.Button(
        ventana,
        text="Ver registros",
        width=20,
        height=2,
        command=abrir_ventana_reportes
    )
    btn_ver.pack(pady=10)

    btn_exportar = tk.Button(
        ventana,
        text="Exportar a Excel",
        width=20,
        height=2
    )
    btn_exportar.pack(pady=10)

    btn_salir = tk.Button(
        ventana,
        text="Salir",
        width=20,
        height=2,
        command=ventana.destroy
    )
    btn_salir.pack(pady=10)

    ventana.mainloop()


def main():
    crear_tablas()
    abrir_ventana_principal()


if __name__ == "__main__":
    main()