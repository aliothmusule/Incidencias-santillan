from pymongo import MongoClient
from bson import decode_all

MONGO_URI = 'mongodb+srv://tilino:_A1234__5678A_@checador.97iiilw.mongodb.net/?retryWrites=true&w=majority'

def dbConnection():
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database("prueba_checador")
        print('Conexión exitosa a la base de datos')
    except ConnectionError:
        print('Error de conexión a la Base de Datos')
        return None
    return db

# Llamar a la función dbConnection
db = dbConnection()

def read_bson_file(file_path):
    with open(file_path, 'rb') as file:
        data = decode_all(file.read())
        return data

datos_generales = read_bson_file('sistemachecador/datos_generales.bson')
datos_contratacion = read_bson_file('sistemachecador/datos_contratacion.bson')

# Insertar los datos generales en la colección deseada
try:
    resultado_generales = db.datos_generales.insert_many(datos_generales)
    print("Documentos de datos generales insertados con éxito")
except Exception as e:
    print("Error al insertar documentos de datos generales:", e)

# Insertar los datos de contratación en la colección deseada
try:
    resultado_contratacion = db.datos_contratacion.insert_many(datos_contratacion)
    print("Documentos de datos de contratación insertados con éxito")
except Exception as e:
    print("Error al insertar documentos de datos de contratación:", e)
