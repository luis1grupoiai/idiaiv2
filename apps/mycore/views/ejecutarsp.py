from django.db import connection
from django.views import View

import json


class CEjecutarSP():

    #Definición y declaración de variables
    #El diccionario parametros debe contener el nombre del parametro y el valor de este, ejemplo:
    #parametros['idUsuario'] = 2
    parametros = {}

    # @staticmethod
    #metodo que almacena los parametros del SP.
    def registrarParametros(self, nombreParametro, valor):
        self.parametros[nombreParametro] = valor
        # print(self.parametros)


    def ejecutarSP(self):
        print("Accede a metodo ejecutarSP.")
        with connection.cursor() as cursor:
            try:

                print(self.parametros)

                cursor.execute("EXEC obtenerPermisosUsuario @idUsuario=%s",[2])

                resultados = cursor.fetchall()
                
                for resultado in resultados:
                    print(resultado)

            except Exception as e:
                 print(f"Error al ejecutar el procedimiento almacenado: {str(e)}")
        