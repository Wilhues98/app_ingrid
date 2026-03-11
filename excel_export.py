from openpyxl import Workbook
from tkinter import filedialog, messagebox


def exportar_a_excel(registros):

    if not registros:
        messagebox.showwarning("Aviso", "No hay registros para exportar.")
        return

    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Archivo Excel", "*.xlsx")],
        title="Guardar reporte"
    )

    if not ruta:
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    encabezados = [
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
    ]

    ws.append(encabezados)

    for fila in registros:
        ws.append(list(fila))

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter

        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    wb.save(ruta)

    messagebox.showinfo("Éxito", "El archivo Excel fue generado correctamente.")