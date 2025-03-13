import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Configuración de API
api_key = '10c299b6d3f1cff2d270c57cf73e11fe'
URL = f'https://gnews.io/api/v4/search?q=ciudad+de+mexico&lang=es&country=mx&max=50&apikey={api_key}'

# Conectar a la base de datos SQLite
conn = sqlite3.connect('seguimiento.db')
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS seguimiento (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               fecha TEXT,
               encabezado TEXT UNIQUE,
               description TEXT,
               fuente TEXT,
               url TEXT UNIQUE)''')
conn.commit()

# Obtener noticias
respuesta = requests.get(URL)
data = respuesta.json()

# Obtener la fecha actual en formato ISO 8601
hoy = datetime.today().strftime('%Y-%m-%d')

# Crear lista de noticias para guardar en el archivo Excel
noticias = []

# Filtrar noticias solo de hoy
for articulo in data.get('articles', []):
    # Obtener la fecha de la noticia
    fecha_articulo = articulo['publishedAt'][:10]  # Formato de fecha: YYYY-MM-DD
    
    if fecha_articulo == hoy:  # Si la noticia es de hoy
        try:
            cursor.execute('''
            INSERT INTO seguimiento(fecha, encabezado, description, fuente, url)
            VALUES (?, ?, ?, ?, ?)''',
            (articulo['publishedAt'], articulo['title'], articulo['description'], articulo['source']['name'], articulo['url']))
            
            # Agregar a la lista de noticias para el Excel
            noticias.append({
                'fecha': articulo['publishedAt'],
                'encabezado': articulo['title'],
                'descripcion': articulo['description'],
                'fuente': articulo['source']['name'],
                'url': articulo['url']
            })
        except sqlite3.IntegrityError:  # Si ya existe la noticia en la base de datos
            print(f'Noticia duplicada: {articulo["title"]}')

# Guardar cambios antes de cerrar la conexión
conn.commit()

# Cerrar la conexión después de realizar todas las operaciones
conn.close()

print("✅ Noticias almacenadas en la base de datos.")

# Guardar los resultados en un archivo Excel (.xlsx) con pandas
df = pd.DataFrame(noticias)

# Guardar el archivo en la ubicación actual de trabajo
df.to_excel('seguimiento_noticias.xlsx', index=False, engine='openpyxl')

print('El archivo Excel se guardó en:', os.getcwd())