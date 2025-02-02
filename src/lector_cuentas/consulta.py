from flask import Flask, request, jsonify
import pdfplumber
import pandas as pd
import re
import os

app = Flask(__name__)

# Función para anonimizar datos sensibles
def anonimizar_descripcion(descripcion):
    descripcion = re.sub(r"\d{6,}", "[OCULTO]", descripcion)  # Reemplaza números largos
    descripcion = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", descripcion)  # Correos
    descripcion = re.sub(r"\b\d{10}\b", "[TELÉFONO]", descripcion)  # Teléfonos (10 dígitos)
    return descripcion

# Función para extraer datos de un estado de cuenta en PDF
def extraer_movimientos(pdf_path):
    movimientos = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    # Expresión regular para capturar fecha, descripción y monto
                    match = re.search(r"(\d{2}-[a-zA-Z]{3})\s+[\d\*]+\s+(.+?)\s+([\d]+\.\d{2})", line)
                    if match:
                        fecha = match.group(1).strip()
                        descripcion = match.group(2).strip()
                        debito = float(match.group(3))
                        # Anonimizar descripción
                        descripcion = anonimizar_descripcion(descripcion)
                        movimientos.append((fecha, descripcion, debito))

    return pd.DataFrame(movimientos, columns=["Fecha", "Descripción", "Débito"])

@app.route('/analizar_estado_cuenta', methods=['POST'])
def analizar_estado_cuenta():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo PDF"}), 400

    file = request.files['file']

    # Guardar temporalmente el archivo
    pdf_path = os.path.join("temp", file.filename)
    file.save(pdf_path)

    try:
        # Extraer movimientos del PDF
        df_total = extraer_movimientos(pdf_path)

        # Filtrar para excluir "TRANSFERENCIA" y "RETIRO"
        df_filtrado = df_total[~df_total["Descripción"].str.contains(r"(TRANSFERENCIA|RETIRO)", case=False, na=False)]

        # Obtener los 5 mayores gastos
        top_5_gastos = df_filtrado.nlargest(5, "Débito").to_dict(orient="records")

        # Agrupar y sumar los gastos recurrentes
        gastos_recurrentes = df_filtrado.groupby("Descripción")["Débito"].sum().reset_index()

        # Obtener los 3 establecimientos con más gasto acumulado
        top_3_recurrentes = gastos_recurrentes.nlargest(3, "Débito").to_dict(orient="records")

        # Eliminar archivo temporal
        os.remove(pdf_path)

        # Devolver los resultados como JSON
        return jsonify({
            "top_5_gastos": top_5_gastos,
            "top_3_gastos_recurrentes": top_3_recurrentes
        })
    except Exception as e:
        # Manejo de errores
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Crear la carpeta temporal si no existe
    if not os.path.exists("temp"):
        os.makedirs("temp")

    app.run(debug=True, host='0.0.0.0', port=5000)
