from django.db import connection
from django.views import View

import json


class CEjecutarSP():

    #Clase que se encarga de ejecutar los procedimientos almacenados de la BD IDIAI
    #Definición y declaración de variables
    #El diccionario parametros debe contener el nombre del parametro y el valor de este, ejemplo:
    #parametros['idUsuario'] = 2
    parametros = {}

    # @staticmethod
    #metodo que almacena los parametros del SP.
    def registrarParametros(self, nombreParametro, valor):
        self.parametros[nombreParametro] = valor
        # print(self.parametros)

    #metodo que ejecuta el procedimiento almacenado con los parametros obtenidos de la función registrarParametros.
    def ejecutarSP(self, sNombreSP = ""):
        # print("Accede a metodo ejecutarSP.")

        sQuery = ""
        nCont = 0
        nTot = 0
        resultados = [] #lista que contendra los resultados de la consulta...

        with connection.cursor() as cursor:
            try:
                # print(sNombreSP)
                
                if len(sNombreSP)>0:
                    
                    # print("el Sp no esta vacio")
                    
                    sQuery = "EXEC "+sNombreSP+" "
                    
                    if len(self.parametros)>0:
                        for clave, valor in self.parametros.items():
                        # print(f'Clave: {clave}, Valor: {valor}')
                            nCont= nCont+1
                            if nCont < len(self.parametros):
                                sQuery+= f'@{clave} = "{valor}", '
                            else:
                                sQuery+= f'@{clave} = "{valor}"'
                                # print(nCont)    

                        # print("El valor del query es: " +sQuery)
                        # cursor.execute("EXEC obtenerPermisosUsuario @idUsuario=%s",[2])
                        cursor.execute(sQuery)

                        #Se obtiene el resultado de la consulta en forma de lista
                        resultados = cursor.fetchall()

                        # print("el tipo de dato es: ")
                        # print(type(resultados))

                        # if len(resultados)>0:
                        #     print("El usuario si tiene acceso a este sistema...")
                        #     #En un diccionario se agrega la clave del permiso y la descripción del permiso hacia el sistema.
                        #     for resultado in resultados:
                        #         # print(resultado[6])
                        #         clave = resultado[6]
                        #         dPermisosUsuario[clave] =  resultado[7]
                             

                        #     print(dPermisosUsuario)

                        # else:
                        #     print("El usuario no tiene acceso a este sistema...")
                        
                        
                    else:
                        # print("No se recibieron parametros, por lo tanto se ejecutará el SP sin parametros.")
                        sQuery = "EXEC "+sNombreSP

                        cursor.execute(sQuery)

                        resultados = cursor.fetchall()                       
                else:
                    print("Por favor de pasar el nombre del Procedimiento Almacenado, sin este no se puede ejecutar el SP.")

             
                # else:
                    # print("El nombre del SP esta vacío.")

            except Exception as e:
                 print(f"Error al ejecutar el procedimiento almacenado: {str(e)}")

            #retorna una lista de los registros obtenidos de la consulta.
            # self.parametros = {}

            self.parametros.clear()
            
            return resultados
        