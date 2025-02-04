from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pdfplumber
import pandas as pd
import re
from io import BytesIO


class Consulta(Resource):
    def post(self):
        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo PDF"}), 400

        file = request.files['file']
        
        try:
            pdf_bytes = BytesIO(file.read())
            df_total = self.extraer_movimientos(pdf_bytes)
            df_filtrado = df_total[~df_total["Descripción"].str.contains(r"(TRANSFERENCIA|RETIRO)", case=False, na=False)]
            top_5_gastos = df_filtrado.nlargest(5, "Débito").to_dict(orient="records")
            gastos_recurrentes = df_filtrado.groupby("Descripción")["Débito"].sum().reset_index()
            top_3_recurrentes = gastos_recurrentes.nlargest(3, "Débito").to_dict(orient="records")

            return jsonify({
                "top_5_gastos": top_5_gastos,
                "top_3_gastos_recurrentes": top_3_recurrentes
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def anonimizar_descripcion(self, descripcion):
        descripcion = re.sub(r"\d{6,}", "[OCULTO]", descripcion)
        descripcion = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", descripcion)
        descripcion = re.sub(r"\b\d{10}\b", "[TELÉFONO]", descripcion)
        return descripcion

    def extraer_movimientos(self, pdf_bytes):
        movimientos = []
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        match = re.search(r"(\d{2}-[a-zA-Z]{3})\s+[\d\*]+\s+(.+?)\s+([\d]+\.\d{2})", line)
                        if match:
                            fecha = match.group(1).strip()
                            descripcion = self.anonimizar_descripcion(match.group(2).strip())
                            debito = float(match.group(3))
                            movimientos.append((fecha, descripcion, debito))
        return pd.DataFrame(movimientos, columns=["Fecha", "Descripción", "Débito"])