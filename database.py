from pymongo import MongoClient

MONGO_URI = 'mongodb+srv://tilino:_A1234__5678A_@checador.97iiilw.mongodb.net/?retryWrites=true&w=majority'
def dbConnection():
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database("prueba_checador")
        print('Pas+o con exito try dbConnection')
    except ConnectionError:
        print('Error de conexión a la Base de Datos')
        return None
    return db

# Llamar a la función dbConnection
db = dbConnection()
