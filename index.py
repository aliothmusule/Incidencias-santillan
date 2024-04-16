from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
import database as dbase
from empleado import Empleado

db = dbase.dbConnection()

app = Flask(__name__)



#ALIOTH RUTAS :)
#inicia rutas AÑLIOTHHHHHHHHHH
#Rutas de la aplicacion

@app.route('/eliminarHorario/<nombre_reporte>', methods=['POST'])
def eliminar_horario(nombre_reporte):
    # MongoDB usa el operador $pull para eliminar un elemento del array que coincida con ciertos criterios
    resultado = db.catalogos_horario.update_many(
        {},
        {'$pull': {'Horarios': {'Nombre_horario_reporte': nombre_reporte}}}
    )
    
    if resultado.modified_count > 0:
        # Reporte eliminado con éxito
        return jsonify({'mensaje': 'Reporte eliminado exitosamente'}), 200
    else:
        # Reporte no encontrado o no eliminado por alguna razón
        return jsonify({'mensaje': 'No se encontró el reporte o no se pudo eliminar'}), 404



from datetime import datetime
@app.route('/verHorario/<nombre_reporte>')
def ver_horario(nombre_reporte):
    reportes = db.catalogos_horario.find({'Horarios.Nombre_horario_reporte': nombre_reporte})
    reporte_encontrado = None
    rfc_empleado = None

    # Buscar el reporte específico y el RFC del empleado
    for reporte in reportes:
        for horario in reporte['Horarios']:
            if horario['Nombre_horario_reporte'] == nombre_reporte:
                reporte_encontrado = horario
                rfc_empleado = reporte['RFC']
                break
        if reporte_encontrado:
            break

    if not reporte_encontrado or not rfc_empleado:
        return "Reporte o empleado no encontrado", 404

    empleado = db.datos_generales.find_one({'RFC': rfc_empleado})
    contrato = db.datos_contratacion.find_one({'RFC': rfc_empleado}) or {}

    if not empleado:
        return "Información de empleado no encontrada", 404

    nombre_dia_a_numero = {'LUNES': 1, 'MARTES': 2, 'MIÉRCOLES': 3, 'JUEVES': 4, 'VIERNES': 5, 'SÁBADO': 6, 'DOMINGO': 7}

    # Procesar cada día en el horario encontrado
    horario_procesado = {}
    for dia_nombre, horas in reporte_encontrado.get('DIA', {}).items():
        dia_numero = nombre_dia_a_numero.get(dia_nombre.upper(), dia_nombre)
        horario_procesado[dia_numero] = {
            'Hora_entrada': [hora.split('-')[0] for hora in horas.get('Hora_entrada', [])],
            'Hora_salida': [hora.split('-')[0] for hora in horas.get('Hora_salida', [])],
        }

    datos_horario = {
        'estatus': 'Activo' if reporte_encontrado.get('estatus', '') == 'Activo' else 'Inactivo',
        'horario_actual': reporte_encontrado.get('Nombre_horario_reporte', 'No disponible'),
        'horario': horario_procesado,
        'nombre': empleado.get('nombre', '') + ' ' + empleado.get('apellido_paterno', '') + ' ' + empleado.get('apellido_materno', ''),
        'puesto': contrato.get('puesto', 'Puesto no disponible'),
        'fecha_reporte': reporte_encontrado.get('Fecha_reporte', 'Fecha no disponible')
    }

    datos_contratacion = {
        'fecha_de_ingreso': contrato.get('fecha_de_ingreso', 'Fecha de ingreso no disponible'),
        'departamento_o_area': contrato.get('departamento_o_area', 'Departamento no disponible'),
        'puesto': contrato.get('puesto', 'Puesto no disponible')
    }

    # Renderiza la plantilla HTML con los datos del reporte
    return render_template('horarioshowreporte.html', datos_horario=datos_horario, datos_contratacion=datos_contratacion, datos_generales=empleado)


@app.route('/horariotabla/<rfc>')
def horariotabla(rfc):
    empleado = db.datos_generales.find_one({'RFC': rfc})
    if not empleado:
        return "Empleado no encontrado", 404

    contrato = db.datos_contratacion.find_one({'RFC': rfc}) or {}
    fecha_ingreso = contrato.get('fecha_de_ingreso', 'Fecha de ingreso no disponible')
    departamento = contrato.get('departamento_o_area', 'Departamento no disponible')
    puesto = contrato.get('puesto', 'Puesto no disponible')

    horario = db.catalogos_horario.find_one({'RFC': rfc})
    if horario and 'Horarios' in horario and horario['Horarios']:
        ultimo_reporte = max(horario['Horarios'], key=lambda x: x['Fecha_reporte'])
        fecha_carga = ultimo_reporte['Fecha_reporte']
        Nombre_horario_reporte = ultimo_reporte['Nombre_horario_reporte']
        
        # Procesar cada día en el horario
        nombre_dia_a_numero = {'LUNES': 1, 'MARTES': 2, 'MIÉRCOLES': 3, 'JUEVES': 4, 'VIERNES': 5, 'SÁBADO': 6, 'DOMINGO': 7}

        # Procesar cada día en el horario
        horario_procesado = {}
        for dia_nombre, horas in ultimo_reporte.get('DIA', {}).items():
            dia_numero = nombre_dia_a_numero.get(dia_nombre.upper())  # Obtener el número correspondiente al nombre del día
            if dia_numero:
                horario_procesado[dia_numero] = {
                    'Hora_entrada': [hora.split('-')[0] for hora in horas.get('Hora_entrada', [])],
                    'Hora_salida': [hora.split('-')[0] for hora in horas.get('Hora_salida', [])],
                }

        datos_horario = {
            'nombre': empleado.get('nombre', ''),
            'apellidos': f"{empleado.get('apellido_paterno', '')} {empleado.get('apellido_materno', '')}",
            'fecha_carga': fecha_carga,
            'puesto': puesto,
            'estatus': 'ACTIVO' if empleado.get('estatus', '') == 'Activo' else 'INACTIVO',
            'horario': horario_procesado,
            'horario_actual': Nombre_horario_reporte
        }
    else:
        datos_horario = {
            'nombre': empleado.get('nombre', ''),
            'apellidos': f"{empleado.get('apellido_paterno', '')} {empleado.get('apellido_materno', '')}",
            'fecha_carga': 'N/H',
            'puesto': puesto,
            'estatus': 'ACTIVO' if empleado.get('estatus', '') == 'Activo' else 'INACTIVO',
            'horario': {},
            'ultimo_reporte': '...'
        }

    return render_template('horariocarga.html', datos_horario=datos_horario, fecha_ingreso=fecha_ingreso, departamento=departamento, datos_contratacion=contrato, datos_generales=empleado)

###################################
@app.route('/guardarHorario', methods=['PUT'])
def guardar_horario():
    horario_data = request.get_json()
    rfc = horario_data.get('RFC')
    puesto = horario_data.get('puesto')
    empleado = horario_data.get('empleado')
    horarios = horario_data.get('horarios')
    estatus = horario_data.get('estatus')
    horario_existente = db.catalogos_horario.find_one({'RFC': rfc})
    #primer if solo agrega reporte de horario dentro de el empleado ya existente, el segundo es para agregar de 0 el horario
    if horario_existente:
        nuevo_horario = {
            'Nombre_horario_reporte': f'{rfc}_{len(horario_existente["Horarios"]) + 1}',
            'Fecha_reporte': datetime.now(),
            'DIA': horarios,
            'puesto': puesto,
            'estatus':estatus,
            'empleado': empleado  # Guarda el nombre completo como empleado
        }
        db.catalogos_horario.update_one({'RFC': rfc}, {'$push': {'Horarios': nuevo_horario}})
        return jsonify({'mensaje': 'Horario actualizado exitosamente'}), 200
    else:
        nuevo_horario = {
            'RFC': rfc,
            'Horarios': [{
                'Nombre_horario_reporte': f'{rfc}_1',
                'Fecha_reporte': datetime.now(),
                'DIA': horarios,
                'puesto': puesto,
                'estatus':estatus,
                'empleado': empleado  # Guarda el nombre completo como empleado
            }]
        }
        db.catalogos_horario.insert_one(nuevo_horario)
        return jsonify({'mensaje': 'Horario guardado exitosamente'}), 200



#Frame con el que se despliega reportes de horario, principal en catalogo-horario- despliega esto...
#Estas rutas se llaman en la parte de index.html o tambien en otros template dependiendo el caso... en este caso 
#solo devuelve la plantilla de horarios.html pero tambien puede hacer una solicitud get o post o etc...


db = dbase.dbConnection()
@app.route('/framehorario')
def framehorario():
    reportes_horario = db.catalogos_horario.find()

    # Se crea una lista que contendrá todos los horarios con la información complementaria
    horarios_completos = []
    
    for reporte in reportes_horario:
        rfc = reporte.get('RFC')
        
        datos_generales = db.datos_generales.find_one({'RFC': rfc})
        datos_contratacion = db.datos_contratacion.find_one({'RFC': rfc})
        
        # Verifica si el empleado existe en datos_generales y datos_contratacion
        if datos_generales and datos_contratacion:
            # Aquí se extrae el 'estatus' de datos_generales y 'puesto' de datos_contratacion
            estatus = datos_generales.get('estatus','Desconocido')
            puesto = datos_contratacion.get('puesto', 'Desconocido')
            nombre_completo = f"{datos_generales.get('nombre')} {datos_generales.get('apellido_paterno')} {datos_generales.get('apellido_materno')}"
            
            # Invertir el orden de los horarios
            horarios_invertidos = list(reversed(reporte.get('Horarios', [])))
            
            # Crea un nuevo diccionario con toda la información
            horario_completo = {
                'RFC': rfc,
                'Horarios': horarios_invertidos,
                'estatus': estatus,
                'puesto': puesto,
                'nombrecompleto': nombre_completo
            }
            horarios_completos.append(horario_completo)

    # Enviar la lista de horarios completos a la plantilla
    return render_template('horarios.html', reportes_horario=horarios_completos)



@app.route('/framehorarioEmpleados')
def framehorarioEmpleados():
    # Obtener los datos de la colección 'datos_generales'
    datos_generales = list(db.datos_generales.find())

    # Obtener los datos de la colección 'datos_contratacion'
    datos_contratacion = list(db.datos_contratacion.find())

    # Convertir datos_generales en un diccionario para un acceso más rápido
    generales_dict = {item['RFC']: item for item in datos_generales}

    # Combinar los datos
    empleados = []
    for contrato in datos_contratacion:
        rfc = contrato['RFC']
        empleado = generales_dict.get(rfc)
        if empleado:
            empleado.update({
                'Puesto': contrato.get('puesto', ''),  # Corregir a 'puesto'
                'Fecha_Contratación': contrato.get('fecha_de_ingreso', ''),  # Corregir a 'fecha_de_ingreso'
                'estatus': empleado.get('estatus', '')  # Usar el estatus de datos_generales
            })
            empleados.append(empleado)

    return render_template('horarioempleados.html', empleados=empleados)

#Frame incidencias a empleados ENVIAR CORREO CON PDF
@app.route('/incidenciacorreo')
def incidenciacorreo():
  empleados = db['datos_generales']
  empleadosReceived = empleados.find()
  return render_template('horarioincidenciacorreo.html', empleados = empleadosReceived)

#FINALIZA ROUTES ALIOTH

#Frame con Form Agregar Empleado
@app.route('/frameEmpleados')
def frameEmpleados():
  empleados = db['datos_generales']
  empleadosReceived = empleados.find()
  return render_template('empleados.html', empleados = empleadosReceived)
 
#Frame de Form Checador 
@app.route('/frameChecador')
def frameChecador():
  empleados = db['datos_generales']
  empleadosReceived = empleados.find()
  return render_template('checador.html', empleados = empleadosReceived)

#Frame con el que se despliega la tabla de los reportes
@app.route('/frameReportes')
def frameReportes():
  return render_template('reportes.html') 

#Frame para el Reporte Empleado
@app.route('/frameReporteEmpleado')
def frameReporteEmpleado():
  return render_template('reporte_empleado.html') 

#Frame para el Reporte Asistencia
@app.route('/frameReporteAsistencia')
def frameReporteAsistencia():
  return render_template('reporte_asistencia.html') 

#Frame para el Reporte Horario
@app.route('/frameReporteHorario')
def frameReporteHorario():
  return render_template('reporte_horario.html')  

#Frame para Modificar lo Reporte Checador
@app.route('/ventana_modificar')
def ventana_modificar():
    return render_template('ventana_modificar.html')

#Frame para el boton de Cancelar del Reporte Checador
@app.route('/ventana_checador')
def ventana_checador():
    return render_template('checador.html')

@app.route('/checador')
def checador():
    return render_template('checador.html')

#Frame con el que se despliega la tabla de los reportes
@app.route('/frameArchivos')
def frameArchivos():
  return render_template('archivos.html') 

@app.route('/visualizar')
def visualizar():
    # Aquí puedes añadir cualquier lógica que necesites ejecutar antes de la redirección
    return render_template('op_visualizacion.html')


#PoUp Se Agrego Correctamente
@app.route('/empleadoExitoso')
def empleadoExitoso():
  return render_template('empleadoExitoso.html')

@app.route('/')
def principal():
  
  return render_template('horarioincidenciacorreo.html')


@app.errorhandler(404)
def notFound(error=None):
  message ={
    'message': 'No encontrado',
    'status': '404 Not Found'
  }
  response= jsonify(message)
  response.status_code = 404
  return response


if __name__ == '__main__':
  app.run(debug=True, port=5000)