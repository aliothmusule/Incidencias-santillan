
from bson import decode_all

def read_bson_file(file_path):
    with open(file_path, 'rb') as file:
        data = decode_all(file.read())
        return data

datos_generales = read_bson_file('sistemachecador/datos_generales.bson')
print("Datos Generales:", datos_generales)
