import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Cargar los datos
df = pd.read_csv('D:/proyecto_rosadw/prediccion-abandono-escolar/datos/crudos/estudiantes.csv')

# Convertir texto a números
df['socioeconomico'] = df['socioeconomico'].map({'baja': 0, 'media': 1, 'alta': 2})
df['abandono'] = df['abandono'].map({'no': 0, 'sí': 1})

# Separar variables
X = df[['edad', 'promedio', 'asistencia', 'reprobadas', 'socioeconomico']]
y = df['abandono']

# Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar el modelo
modelo = RandomForestClassifier()
modelo.fit(X_train, y_train)

# Guardar el modelo entrenado
with open('modelo_abandono.pkl', 'wb') as f:
    pickle.dump(modelo, f)

print("✅ Modelo entrenado y guardado como modelo_abandono.pkl")