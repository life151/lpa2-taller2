from flask import Flask, render_template, request, send_file
import requests
import io
import os
from fpdf import FPDF

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://backend:8000")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generar-pdf", methods=["POST"])
def generar_pdf():
    numero = request.form.get("numero_factura") or request.form.get("id_factura") or "FAC-2025-001"

    # Pedir datos al backend
    resp = requests.get(f"{API_URL}/facturas/v1/{numero}")
    data = resp.json()

    # Crear PDF - aquí la variable es pdf, no doc
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Factura {data['numero_factura']}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Fecha: {data['fecha_emision']}", ln=True)
    pdf.cell(0, 10, f"Empresa: {data['empresa']['nombre']}", ln=True)
    pdf.cell(0, 10, f"Cliente: {data['cliente']['nombre']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Descripcion", border=1)
    pdf.cell(20, 10, "Cant", border=1)
    pdf.cell(40, 10, "Precio", border=1)
    pdf.cell(40, 10, "Total", border=1, ln=True)

    pdf.set_font("Arial", "", 12)
    for item in data['detalle']:
        pdf.cell(80, 10, item['descripcion'][:35], border=1)
        pdf.cell(20, 10, str(item['cantidad']), border=1)
        pdf.cell(40, 10, str(item['precio_unitario']), border=1)
        pdf.cell(40, 10, str(item['total']), border=1, ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Subtotal: ${data['subtotal']}", ln=True)
    pdf.cell(0, 10, f"Impuesto: ${data['impuesto']}", ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Total: ${data['total']}", ln=True)

    buffer = io.BytesIO(pdf.output())
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{numero}.pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
