from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from flask import send_file
from datetime import datetime
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://michelleOY_db:aixabg@cluster0.xvzenyh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
try:
    client.admin.command('ping')
    print("✅ Conexión a MongoDB Atlas exitosa")
except Exception as e:
    print("❌ Error al conectar con MongoDB Atlas:", e)
db = client ["abandono_escolar"]
coleccion = db["predicciones"]
# Cargar el modelo entrenado
try:
    with open('servidor/modelo/modelo_abandono.pkl', 'rb') as f:
        modelo = pickle.load(f)
except Exception as e:
    print("❌ Error al cargar el modelo:", e)
    modelo = None

@app.route('/')
def inicio():
    return render_template('formulario.html')


@app.route('/predecir', methods=['POST'])
def predecir():
    datos = request.json

    if modelo is None:
     return jsonify({'error': 'Modelo no disponible'}), 500
    # Extraer variables
    edad = datos.get('edad')
    promedio = datos.get('promedio')
    asistencia = datos.get('asistencia')
    reprobadas = datos.get('reprobadas')
    socioeconomico = datos.get('socioeconomico')

    # Convertir socioeconómico a número
    mapa_socio = {'baja': 0, 'media': 1, 'alta': 2}
    socio_num = mapa_socio.get(socioeconomico, 1)  # por defecto 'media'

    # Crear arreglo para el modelo
    entrada = np.array([[edad, promedio, asistencia, reprobadas, socio_num]])

    # Predecir
    prediccion = modelo.predict(entrada)[0]
    riesgo = 'alto' if prediccion == 1 else 'bajo'

    # Guardar en MongoDB Atlas
    registro = {
        "edad": edad,
        "promedio": promedio,
        "asistencia": asistencia,
        "reprobadas": reprobadas,
        "socioeconomico": socioeconomico,
        "riesgo_abandono": riesgo
    }
    coleccion.insert_one(registro)

    # Responder al navegador
    return jsonify({'riesgo_abandono': riesgo})

@app.route('/historial')
def historial():
    registros = list(coleccion.find({}, {'_id': 0}))
    return render_template('historial.html', registros=registros)

from io import BytesIO
import traceback

@app.route('/exportar_excel')
def exportar_excel():
    try:
        registros = list(coleccion.find({}, {'_id': 0}))
        if not registros:
            return jsonify({'error': 'No hay datos para exportar'}), 404

        df = pd.DataFrame(registros)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Historial')
        output.seek(0)

        fecha_actual = datetime.now().strftime('%y-%m-%d')
        nombre_archivo = f'historial_abandono_{fecha_actual}.xlsx'

        return send_file(
            output,
            attachment_filename=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print("❌ Error al exportar Excel:", e)
        traceback.print_exc()
        return jsonify({'error': 'Error interno al generar el archivo'}), 500
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)