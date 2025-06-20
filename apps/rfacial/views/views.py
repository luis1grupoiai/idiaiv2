# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.http import FileResponse, HttpResponse, Http404

# from django.http import HttpResponse
from django.db import models
from django.http.response import JsonResponse
from apps.areas.models import *
from apps.sistemas.models import *
from apps.rfacial.models import *
from apps.AsignarUsuario.models import *
from passlib.hash import django_pbkdf2_sha256 as handler

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils import timezone


from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import datetime,timedelta
from apps.mycore.views.ejecutarsp import CEjecutarSP

from cryptography.fernet import Fernet
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from sys import getsizeof

from django.http import FileResponse, Http404
from apps.AsignarUsuario.models import VallEmpleado
from django.urls import reverse
from ..utils import EnvioCorreos

import json
import os
import base64
import time
import time

# stky = Fernet.generate_key()
stky = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
#stky = force_bytes(os.environ.get('KFNRAPIAUTH'))

# print(stky)

crfr = Fernet(stky)
# from camera import VideoCamera, IPWebCam
# import numpy as np
# import cv2
# import os, urllib
# import mediapipe as mp

# def swagger_json(request):
#         with open('swagger/apiAuth.json', 'r') as json_file:
#             data = json.load(json_file)
#         return JsonResponse(data)

class CAutenticacion(APIView):
        
    oExecSP = CEjecutarSP()
    sNombreSistema = ""
    oUser = ""
    dGruposAsigUsuario = {}
    intTiempoExpira = 0

    # @staticmethod
    def obtenerPermisos(self, p_nIdSistema, p_nIdUsuario):
        dPermisos = {}
        dPermisosUsuario = {}
        # print("Accede a metodo obtenerPermisos.")
        try:
            # dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema, permiso_id__isnull=False).values())
            self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            self.oExecSP.registrarParametros("idSistema",p_nIdSistema)
            dPermisos = self.oExecSP.ejecutarSP("obtenerPermisosUsuario")

            # print("el tipo de dato es: ")
            # print(type(dPermisos))

            if len(dPermisos)>0:
                # print("El usuario si tiene acceso al sistema con clave: "+ str(p_nIdSistema))
                # print(dPermisos[0][12])
                # self.sNombreSistema = dPermisos[0][13]
                for dPermiso in dPermisos:
                    # dPermisosUsuario[dPermiso[6]] = dPermiso[7]
                    dPermisosUsuario[dPermiso[6]] = dPermiso[17]

                # print(dPermisosUsuario)

            
        except ValueError as error:
            sTexto = "Error en el metodo obtenerPermisos: %s" % error
            print(sTexto)

        return dPermisosUsuario
    
    #EMC 08/11/2024 METODO PARA OBTENER ARCHIVO FOTO DEL EMPLEADO.
    # def photo_view(self):
    #     # Obtén el usuario autenticado
    #     usuarioBD = VallEmpleado.objects.filter(username=p_sUsername).first()

    #     entorno = os.environ.get('DJANGO_ENV')

    #     # Verifica si el usuario tiene una ID personal asociada
    #     if usuarioBD and usuarioBD.id_personal:
    #         # Ruta completa del archivo en la red compartida
    #         if entorno == 'development':
    #             file_path = f'//intranet.grupo-iai.com.mx/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.id_personal}.jpg'
    #         elif entorno == 'production':
    #             file_path = f'C:/xampp/htdocs/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.id_personal}.jpg'
    #         else:
    #             raise ValueError("El valor de 'entorno' no es válido")

    #         # Verifica si el archivo existe en la ruta de red
    #         if os.path.exists(file_path):
    #             try:
    #                 # Intenta abrir y devolver la imagen como respuesta de archivo
                   
    #                 return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
    #             except FileNotFoundError:
    #                 # raise Http404("Imagen no encontrada o acceso denegado")
    #                 return None

    def obtenerDatosPersonales(self, p_nIdUsuario=0, p_nIdPersonal=0):
        dDatos = {}
        # dDatosUsuario = {}
        print("Accede a metodo obtenerDatosPersonales, solo devuelve datos si el usuario esta activo.")
        try:
            
            if p_nIdUsuario>0:
                self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            elif p_nIdPersonal>0:
                self.oExecSP.registrarParametros("idPersonal",p_nIdPersonal)
            
            dDatos = self.oExecSP.ejecutarSP("obtenerDatosPersonales")

            # if len(dDatos)>0:
            #    dDatosUsuario = dDatos
                

                # print(dPermisosUsuario)           
        except ValueError as error:
            sTexto = "Error en el metodo obtenerDatosPersonales: %s" % error
            print(sTexto)

        return dDatos

    def obtenerGrupos(self, p_nIdSistema, p_nIdUsuario):
        dGrupos = {}
        dGruposUsuario = {}
        dNombreGrupo = {}
        print("Accede a metodo obtenerGrupos.")
        try:
            # dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema, permiso_id__isnull=False).values())
            self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            self.oExecSP.registrarParametros("idSistema",p_nIdSistema)
            dGrupos = self.oExecSP.ejecutarSP("obtenerGruposUsuario")

            # print("el tipo de dato es: ")
            # print(type(dGrupos))

            if len(dGrupos)>0:
                # print("El usuario si tiene acceso al sistema con clave: "+ str(p_nIdSistema))
                # print(dPermisos[0][12])
                # self.sNombreSistema = dGrupos[0][16]
                for dGrupo in dGrupos:
                    dNombreGrupo[dGrupo[9]] = dGrupo[9]
                    dGruposUsuario[dGrupo[15]] = dGrupo[13]


                
                    

                    #Método encargado de ordenar los permisos por grupos en su correspondiente bloque
                    #Se entregan los permisos de grupo dentro del bloque permisos, ya grupos no tendra un bloque propio
                    #en la respuesta JSON de la api - 15/12/2023
                    # dGruposUsuario = self.ordenarGrupos(sNombreGrupo,dGrupos)

                # print("Nombre de grupos: ")
                # print(dNombreGrupo)
                self.dGruposAsigUsuario = dNombreGrupo

            
        except ValueError as error:
            sTexto = "Error en el metodo obtenerGrupos: %s" % error
            print(sTexto)

        return dGruposUsuario
    
    def ordenarGrupos(self,p_sElementoBuscado, p_dlistas):
        try:
            listas_coincidentes = []
            dGrupoOrdenado = {}
            dGrupoUsuario = {}

            if len(p_sElementoBuscado)>0:
                listas_coincidentes = [lista for lista in p_dlistas if p_sElementoBuscado in lista]
                # print("Listas con el elemento coincidente:", listas_coincidentes)
                
                if len(listas_coincidentes)>0:
                    for dGrupo in listas_coincidentes:
                        dGrupoOrdenado[dGrupo[15]] = dGrupo[13]


                dGrupoUsuario[p_sElementoBuscado] = dGrupoOrdenado

                # print(dGrupoUsuario)

            else:
                print("El nombre del grupo no es el correcto.")
        except ValueError as error:
            sTexto = "Error en el metodo ordenarGrupos: %s" % error
            print(sTexto)

        return dGrupoUsuario

    def get_custom_auth_token(self, p_sUsuario, p_sTiempoExp = 3):
        # Generamos token para autenticación del usuario :) 
        sTexto = ""
        sToken_encoded = ""
        expiration_time= 0
        expiration_hours = int(p_sTiempoExp) # 3 horas por defecto en caso de que no se asigne un tiempo en la app.

        try:
            user = User.objects.get(username=p_sUsuario) 
            timestamp = int(timezone.now().timestamp())
            #print(timezone.now())
            # Calcular la fecha de expiración del token
            expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
            # expiration_time = timestamp + (expiration_hours * 60)  # 60 segundos en un minuto, solo para terminos de prueba ...
            # print(expiration_time)
            #ARSI 10072024
            self.intTiempoExpira = expiration_time
            # print("======== > Tiempo de expiración ====> ")
            # print(self.intTiempoExpira)
            
            token = default_token_generator.make_token(user)+ ',' + str(expiration_time)
   
            # sToken_encoded = urlsafe_base64_encode(force_bytes(token))
            # .encode()).decode()
            sToken_encoded = crfr.encrypt(token.encode()).decode()

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Ocurrió un error al generar el token para el usuario. ', "error": sTexto}

        # print(type(sToken_encoded))
        return sToken_encoded

    def generarTKGlobal(self, p_sUsuario, p_sTiempoExp = 3, p_nIdSistema = 0):
        # Generamos token Global para autenticación del usuario :) 
        sTexto = ""
        sToken_encoded = ""
        expiration_time= 0
        expiration_hours = int(p_sTiempoExp) # 3 horas por defecto en caso de que no se asigne un tiempo en la app.

        try:
            user = User.objects.get(username=p_sUsuario) 
            timestamp = int(timezone.now().timestamp())

            # Calcular la fecha de expiración del token
            expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
           
            # expiration_time = timestamp + (expiration_hours * 60)  # 60 segundos en un minuto, solo para terminos de prueba ...
            
            token = default_token_generator.make_token(user)+ ',' + str(expiration_time)+','+str(p_nIdSistema)+','+os.environ.get('SIGNAL')

            sTam = len(token)

            token = token+str(sTam)

            # print(token)
   
            # sToken_encoded = urlsafe_base64_encode(force_bytes(token))
            sToken_encoded = crfr.encrypt(token.encode()).decode()

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Ocurrió un error al generar el token para el usuario. ', "error": sTexto}

        # print(type(sToken_encoded))
        return sToken_encoded
    
    def obtenerSistemasUsuario(self, p_nIdUsuario):
        # dSistemasGrupos = {}
        # dSistemasPermisos = {}
        dAccesoSistemaUsuario = []
        dSistPermUser = []
        dSistGrupoUser = []

        print("Accede a metodo obtenerSistemasUsuario.")
        print("El id de usuario es: "+str(p_nIdUsuario))
        try:
            # dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema, permiso_id__isnull=False).values())
            self.oExecSP.registrarParametros("idUser",p_nIdUsuario)
            self.oExecSP.registrarParametros("pNoption",1)
            dSistemasPermisos = self.oExecSP.ejecutarSP("obtenerListadoSistemas")
            
            if len(dSistemasPermisos)>0:
            
                for dPermiso in dSistemasPermisos:
                    # sNombreGrupo = dGrupo[9]
                    dSistPermUser.append(dPermiso[0])

            print(dSistPermUser)

            self.oExecSP.registrarParametros("idUser",p_nIdUsuario)
            self.oExecSP.registrarParametros("pNoption",2)
            dSistemasGrupos = self.oExecSP.ejecutarSP("obtenerListadoSistemas")

            if len(dSistemasGrupos)>0:
            
                for dGrupo in dSistemasGrupos:
                    # sNombreGrupo = dGrupo[9]
                    dSistGrupoUser.append(dGrupo[0])

            print(dSistGrupoUser)
           
            print("El usuario puede acceder a los sistemas: ")

            lista_sin_repetidos = list(set(dSistPermUser + dSistGrupoUser))
            # print(lista_sin_repetidos)

            # print("el tipo de dato es: ")
            # print(type(dPermisos))
            # dSistemasGrupos.update(dSistGrupoUser)

            # dAccesoSistemaUsuario = list(set(dAccesoSistemaUsuario))


            # print(dSistemasGrupos)

            
        except ValueError as error:
            sTexto = "Error en el metodo obtenerSistemasUsuario: %s" % error
            print(sTexto)

        return lista_sin_repetidos
    
    
    @staticmethod
    def prueba():
        print("Accede a metodo prueba...")

    def decodificarB64(self, p_decodificado):
        sTexto = ""
        print("Accede a metodo decodificarB64.")
        try:
            sTextFinal = base64.b64decode(p_decodificado)
            sTextFinal = sTextFinal.decode('utf-8')
            sTextFinal = str(sTextFinal)

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error al convertir de base64. ', "error": sTexto}

            print(datos)
        #print(sTextFinal)

    
        return sTextFinal
    
    def consultarSistema(self, idSistema):
        sTexto = ""
        try:
            dSistema = list(Sistemas.objects.filter(id=idSistema).values())
            if len(dSistema)>0:
                # sistema = dSistema[0]['id']
                self.sNombreSistema = dSistema[0]['nombre']

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error al ejecutar query. ', "error": sTexto}

            print(datos)

    
        return dSistema
    
    def obtenerProyectoAsignadosEmpleado(self, idPersonal):
        # ARSI 25092024 Se obtendrá el listado de todos los proyectos donde el empleado estuvo involucrado.
        sTexto = ""
        dProyectosInvolucrados = []
        dHistoricoProyectos = {}
        nPos = 0
        clave = ""

        try:
            self.oExecSP.registrarParametros("idPersonal",idPersonal)
            # self.oExecSP.registrarParametros("pNoption",2)
            dProyectosInvolucrados = self.oExecSP.ejecutarSP("obtenerProyectosContratadoEmpleado")

            # dProyectosInvolucrados = list(Sistemas.objects.filter(id=idSistema).values())
            if len(dProyectosInvolucrados)>0:
                # print(dProyectosInvolucrados)
                
                for item in dProyectosInvolucrados:
                    # print(item[0])
                    # print(item[1])

                    if(item[0]== None):
                        clave = 'SIN_ID_'+str(nPos)
                    else:
                        clave = item[0]

                    dHistoricoProyectos[clave] = item[1]

                    nPos = nPos+1


                # self.sNombreSistema = dSistema[0]['nombre']
            else:
                 print("Al parecer el empleado con id personal "+str(idPersonal)+" no tiene ningun proyecto en el que este involucrado.")

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error al ejecutar query. ', "error": sTexto}

            print(datos)

    
        return dHistoricoProyectos

    def consultarExisteUsuario(self, nameUser):
        print("Accede a metodo  consultarExisteUsuario:")
        #print(nameUser)
        sTexto = ""
        datos = {}
        oUser = {}
        try:
           oUser = User.objects.filter(username=nameUser)
        #    dUsuario = list(User.objects.filter(username=nameUser, is_active=1).values())
           dUsuario = list(oUser.values())
        #    print(dUsuario)

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'El usuario buscado no existe. ', "error": sTexto}

            print(datos)

    
        return dUsuario

    def consultarUsuarioActivo(self, nameUser):
        # print("Accede a metodo  consultarUsuarioActivo:")
        # print(nameUser)
        sTexto = ""
        datos = {}
        try:
           self.oUser = User.objects.filter(username=nameUser, is_active=1)
        #    dUsuario = list(User.objects.filter(username=nameUser, is_active=1).values())
           dUsuario = list(self.oUser.values())
        #    print(dUsuario)

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error al ejecutar query de consultarUsuarioActivo. ', "error": sTexto}

            print(datos)

    
        return dUsuario
    
    def verificarPswd(self, sPsw):
        print("Accede a metodo  verificarPswd:")
        # print(nameUser)
        sTexto = ""
        datos = {}
        bCorrecto = False
        try:

            if self.oUser.exists():
                user_obj = self.oUser.first()

                if user_obj.check_password(sPsw):
                    print("password correcta.")
                    bCorrecto = True
                else:
                    print("password incorrecta.")
            else:
                print("El usuario no existe.")
          

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error al ejecutar query de consultarUsuarioActivo. ', "error": sTexto}

            print(datos)
    
        return bCorrecto
    

    #ARSI  19/03/2025 SE ACTUALIZA METODO REGISTRAR ACCESO se valida token
    def registrarAcceso(self, username, idSistema, observaciones, opc, bConsultaBloqueo = False, bSaveTk = 0, tk= ""):
            print("----- Accede a metodo registrar accesos -----")

            #Se declaran e Inicializan variables
            bExisteRegAccess = True
            idReg = 0
            NumIntentos = 0
            regAcceso = False
            nTotIntentos = 0
            fechaCad = None
            fecha_con_zona_horaria = False
            fecha_modificada = False
            intFechaCad = 0 #Fecha/hora de caducidad del intento registrado
            timestamp = 0 #Fecha/hora actual  
            actualizaReg = False
            bValido = True
            fechaUpd = False

            sTexto = ""
            message = ""
            datos = {}            
            nReg = 0 #ARSI 19/03/2025 VARIABLE QUE ALMACENA ID DE REG DE TOKEN ACTIVO
            dDatosTk = [] #ARSI 19/03/2025 VARIABLE QUE ALMACENA los datos de los token activos
            nTotAfectadas = 0  #ARSI 19/03/2025 VARIABLE QUE ALMACENA total de filas afectadas para inactivar el registro de token.
            # print(username)
            # zona_horaria = timezone()
            # print("zona_horaria")
            # print(zona_horaria)
            
            try:
                idReg = intentos.objects.get(username=username,activo=1, idSistema=idSistema).id
                NumIntentos = intentos.objects.get(username=username,activo=1, idSistema=idSistema).numintentos
                fechaCad = intentos.objects.get(username=username,activo=1, idSistema=idSistema).fechaCadReg
                fechaUpd = intentos.objects.get(username=username,activo=1, idSistema=idSistema).updated_at

            except intentos.DoesNotExist:
                bExisteRegAccess = False
            else:
                if int(NumIntentos) == 3:
                    print("Este usuario posiblemente este bloqueado por 10 min. y no podrá iniciar sesión.")

                    if fechaCad != None:
                        intFechaCad = int(fechaCad.timestamp()) #Fecha/hora de caducidad del intento registrado
                        timestamp = int(timezone.now().timestamp()) #Fecha/hora actual

                        # print(intFechaCad)
                        # print(timestamp)

                        if timestamp  > intFechaCad: 
                            bExisteRegAccess = False
                            actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now())

                            if bConsultaBloqueo:
                                message = "libre"
                                sTexto = "El usuario puede loggearse" 
                        else:
                            bValido = False
                            print("El usuario alcanzo un limite de 3 intentos de inicio de sesión, por lo que esta bloqueado por 10 min.")
                            
                            message = "bloqueado"
                            sTexto = "El usuario alcanzo un limite de 3 intentos de inicio de sesión, por lo que esta bloqueado por 10 min."                            
                    else:
                        # fecha_con_zona_horaria = timezone.now() 
                        # print(fecha_con_zona_horaria)
                        print("Al parecer no se guardo la fecha/hora de caducidad del registro. Se calculara el tiempo de caducidad del registro por medio de la fecha update.")
                                    
                        fechaCad = fechaUpd + timedelta(minutes=10)

                        intFechaCad = int(fechaCad.timestamp()) #Fecha/hora de caducidad del intento registrado
                        timestamp = int(timezone.now().timestamp()) #Fecha/hora actual

                        if timestamp  > intFechaCad: 
                            bExisteRegAccess = False
                            actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now(),fechaCadReg=fechaCad)

                            if bConsultaBloqueo:
                                message = "libre"
                                sTexto = "El usuario puede loggearse"
                        else:
                            bValido = False
                            print("El usuario alcanzo un limite de 3 intentos de inicio de sesión, por lo que esta bloqueado por 10 min.")
                            
                            message = "bloqueado"
                            sTexto = "El usuario alcanzo un limite de 3 intentos de inicio de sesión, por lo que esta bloqueado por 10 min."

            #ARSI 20/03/2025 BLOQUE DE CODIGO PARA INACTIVAR TODOS LOS TOKENS EN CASO DE QUE EL USUARIO configure a no guardar TOKEN
            if bSaveTk == 0:
                dDatosTk = self.obtenerTokenActivo(username,idSistema)
            
                nTotReg = dDatosTk['TotReg']

                print("1. nTotReg")
                print(nTotReg)

                if nTotReg > 0:
                    nTotAfectadas = self.inactivarTokens(username,idSistema)
                    print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")
                else:
                    print("CAutenticacion - registrarAccesos - No Se inactivaron tokens")



            if bValido and not bConsultaBloqueo:                       
                if bExisteRegAccess:
                    print("Si existe registro de historial de acceso en los sistemas para el usuario : "+username)

                    if opc == 1:
                        #ARSI 19/03/2025 SE GUARDA EL TOKEN SOLO SI bSaveTk ES 1
                        print("caso exitoso, el usuario se loggeo sin problemas : "+username)
                        message = "Success"
                        sTexto = "Caso exitoso, el usuario se loggeo sin problemas : "+username

                        if bSaveTk == 0:
                            actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now(),observaciones=observaciones)
                        elif bSaveTk == 1:
                            
                            dDatosTk = self.obtenerTokenActivo(username,idSistema)

                            nReg = dDatosTk['idReg']
                            nTotReg = dDatosTk['TotReg']

                            # print(nReg)
                            # print(nTotReg)

                            if nTotReg>1:
                                nTotAfectadas = self.inactivarTokens(username,idSistema)

                                if nTotAfectadas>0:
                                   print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")

                            elif nReg > 0:
                               nTotAfectadas = self.inactivarToken(nReg)

                               if nTotAfectadas>0:
                                   print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")

                            actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now(),observaciones=observaciones,token=tk,tokenActivo=1)


                        
                    elif opc == 2:
                        print("Error en el password o usuario dado, existe registro activo de intento de inicio de sesión :O")
                        
                        #Calculo entre intentos de inicio de sesión:
                        #Realizar calculo si el registro de inicio de sesión aun no caduca.
                        intFechaCad = int(fechaCad.timestamp()) #Fecha/hora de caducidad del intento registrado
                        timestamp = int(timezone.now().timestamp()) #Fecha/hora actual
                        print(intFechaCad)
                        print(timestamp)

                        if intFechaCad > timestamp:                                                
                            NumIntentos= int(NumIntentos)+1

                            if NumIntentos < 4: 
                                # NumIntentos= int(NumIntentos)+1
                                print("El registro de intento aun no caduca, por lo que el num. de intento debe iterar +1.")

                                fecha_con_zona_horaria = timezone.now() 
                                print(fecha_con_zona_horaria)
                                    
                                if NumIntentos == 3:
                                    fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=10)
                                else:
                                    fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=5)

                                

                                actualizaReg = intentos.objects.filter(id=idReg).update(activo=1,updated_at=timezone.now(),fechaCadReg=fecha_modificada,numintentos=NumIntentos, observaciones=observaciones)

                            
                                nTotIntentos = 3 - NumIntentos;
                                if nTotIntentos == 0:
                                    sTexto = "Ha alcanzado el limite de intentos, su usuario quedara bloqueado por 10 minutos."
                                else:
                                    sTexto = "Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión."

                                print("Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión.")
                                message = "error"
                                # sTexto = "Usuario o contraseña incorrectos, le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión."
                            else:
                                print("Alcanzo el limite de intentos de iniciar sesión...")

                                message = "bloqueado"
                                sTexto = "El usuario alcanzo un limite de 3 intentos de inicio de sesión, por lo que esta bloqueado por 10 min." 

                                # fecha_con_zona_horaria = timezone.now() 
                                # print(fecha_con_zona_horaria)
                                    
                                # fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=10)

                                # actualizaReg = intentos.objects.filter(id=idReg).update(activo=1,updated_at=timezone.now(),fechaCadReg=fecha_modificada)


                        else:
                            print("El registro de intento ya caduco, por lo que se actualiza el registro a inactivo.")
                            # actualizaRegReac = Reacciones.objects.using('intranet').filter(id=idRegReaccion).update(reaccion=reaccionActualUsuario,activo=activo)
                            actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now())

                            fecha_con_zona_horaria = timezone.now() 
                            print(fecha_con_zona_horaria)
                                
                            fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=5)

                            regAcceso = intentos(
                            username= username,
                            numintentos = 1,
                            idSistema = idSistema,
                            fechaCadReg = fecha_modificada,
                            activo = 1,
                            observaciones = observaciones
                            )

                            regAcceso.save()

                            nTotIntentos = 3 - 1

                            if nTotIntentos == 0:
                                sTexto = "Ha alcanzado el limite de intentos, su usuario quedara bloqueado por 10 minutos."
                            else:
                                sTexto = "Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión."

                            print("Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión.")

                            message = "error"
                            # sTexto = "Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión." 
                        

                    else:
                        print("Errores generales")

                        regAcceso = intentos(
                            username= username,
                            numintentos = 0,
                            idSistema = idSistema,
                            activo = 0,
                            observaciones = observaciones
                        )

                        regAcceso.save()

                        message = "Alert"
                        sTexto = "Se inserto un error generico de inicio de sesión. "

                else:
                    print("No existe registro de historial de acceso en los sistemas para el usuario : "+username)

                    if opc == 1:
                        #ARSI 19/03/2025 SE GUARDA EL TOKEN SOLO SI bSaveTk ES 1
                        print("caso exitoso, el usuario se loggeo sin problemas : "+username)

                        if bSaveTk == 0:
                            regAcceso = intentos(
                                username= username,
                                numintentos = 0,
                                idSistema = idSistema,
                                activo = 0,
                                observaciones = observaciones
                            )
                        elif bSaveTk == 1:
                            
                            #nReg = self.obtenerTokenActivo(username,idSistema)
                            dDatosTk = self.obtenerTokenActivo(username,idSistema)

                            nReg = dDatosTk['idReg']
                            nTotReg = dDatosTk['TotReg']

                            # print(nReg)
                            # print(nTotReg)

                            if nTotReg>1:
                                nTotAfectadas = self.inactivarTokens(username,idSistema)

                                if nTotAfectadas>0:
                                   print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")

                            elif nReg > 0:
                               nTotAfectadas = self.inactivarToken(nReg)

                               if nTotAfectadas>0:
                                   print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")

                            regAcceso = intentos(
                                username= username,
                                numintentos = 0,
                                idSistema = idSistema,
                                activo = 0,
                                observaciones = observaciones,
                                token=tk,
                                tokenActivo=1
                            )

                        regAcceso.save()

                        message = "Success"
                        sTexto = "Caso exitoso, el usuario se loggeo sin problemas : "+username

                    elif opc == 2:
                        print("Error en las credenciales del usuario")
                        
                        fecha_con_zona_horaria = timezone.now() 
                        print(fecha_con_zona_horaria)

                        # fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=10)
                        fecha_modificada = fecha_con_zona_horaria + timedelta(minutes=5)
                        print(fecha_modificada)
                        
                        # pruebaFecha = intentos.objects.get(id=1).created_at
                        # pruebaFecha = intentos.objects.get(username=username).created_at

                        # print("pruebaFecha")
                        # print(pruebaFecha)

                        # Solo son pruebas
                        # testDate1 = pruebaFecha + timedelta(minutes=10)
                        # testDate2 = pruebaFecha - timedelta(minutes=10)
                        # print(testDate1)
                        # print(testDate2)

                        regAcceso = intentos(
                            username= username,
                            numintentos = 1,
                            idSistema = idSistema,
                            fechaCadReg = fecha_modificada,
                            activo = 1,
                            observaciones = observaciones
                        )

                        regAcceso.save()

                        nTotIntentos = 3 - 1
                        if nTotIntentos == 0:
                            sTexto = "Ha alcanzado el limite de intentos, su usuario quedara bloqueado por 10 minutos."
                        else:
                            sTexto = "Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión."

                        print("Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión.")

                        message = "error"
                        # sTexto = "Le queda(n) "+str(nTotIntentos)+" intento(s) para volver a iniciar sesión." 

                    else:
                        print("Errores generales")

                        regAcceso = intentos(
                            username= username,
                            numintentos = 0,
                            idSistema = idSistema,
                            activo = 0,
                            observaciones = observaciones
                        )

                        regAcceso.save()

                        message = "Alert"
                        sTexto = "Se inserto un error generico de inicio de sesión. "
                    
                                
            datos = {'message':message, 'texto':sTexto}

            return datos
       
        # instancia.registrarParametros("idUsuario",2)
        # sSP = "obtenerPermisosUsuario"
        # instancia.registrarParametros("usuario","ana.sanchez")
        # instancia.registrarParametros("edad","14")

        # resultado = instancia.ejecutarSP(sSP)

 
    #ARSI 19/03/2025 SE CONSULTA SI EL USUARIO TIENE TOKEN ACTIVO PARA EL SISTEMA AL QUE INTENTA ACCEDER.
    def obtenerTokenActivo(self, username, idSistema):
        bExisteRegTokenActivo = True
        idReg = 0
        nTotReg = 0
        dResult = []
        token = ""
        
        try:
            idReg = intentos.objects.get(username=username,tokenActivo=1, idSistema=idSistema).id                
            token = intentos.objects.get(username=username,tokenActivo=1, idSistema=idSistema).token                
            #nTotReg = intentos.objects.get(username=username,tokenActivo=1, idSistema=idSistema).count()
            nTotReg = intentos.objects.filter(username=username,tokenActivo=1, idSistema=idSistema).count()
            # print("obtenerTokenActivo :")
            # print(nTotReg)
        except intentos.DoesNotExist:
            bExisteRegTokenActivo = False
            idReg = 0
            nTotReg = 0
            token = ""

        dResult = {"idReg": idReg, "TotReg": nTotReg,"token": token}

        return dResult
    

    #ARSI 19/03/2025 INACTIVAR TOKEN ACTIVO, actualiza el registro del token activo que encuentre y devuelve el numero de filas
    #actualizadas.
    def inactivarToken(self, idReg):
        
        actualizaReg = 0
        
        try:
            #idReg = intentos.objects.get(username=username,tokenActivo=1, idSistema=idSistema).id                
            actualizaReg = intentos.objects.filter(id=idReg).update(token="",tokenActivo=0,updated_at=timezone.now())

            print(f"Se actualizaron {actualizaReg} registros.")
        except intentos.DoesNotExist:
            #bExisteRegTokenActivo = False
            actualizaReg = 0

        return actualizaReg


    #ARSI 19/03/2025 INACTIVAR TOKEN ACTIVO, actualiza el registro del token activo que encuentre y devuelve el numero de filas
    #actualizadas.
    def inactivarTokens(self, username,idSistema):
        
        actualizaReg = 0
        
        try:
            #idReg = intentos.objects.get(username=username,tokenActivo=1, idSistema=idSistema).id                
            actualizaReg = intentos.objects.filter(username=username,idSistema=idSistema,tokenActivo=1).update(token="",tokenActivo=0,updated_at=timezone.now())

            print(f"Se actualizaron {actualizaReg} registros.")
        except intentos.DoesNotExist:
            #bExisteRegTokenActivo = False
            actualizaReg = 0

        return actualizaReg

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

    def get(self,request):
        # usuarios = list(User.objects.values())
        datos = {'message': 'Conexion exitosa a API AUTH :)'}
        # dDatosPersonales = self.obtenerDatosPersonales("2")

        # empleados = VallEmpleado.objects.filter(id=2)
        # self.prueba()
        # if len(usuarios)>0:
        #     # datos = {'message': 'Success','usuarios':usuarios}
        #     datos = {'message': 'Conexión exitosa :)'}
        # else:
        #     datos = {'message': 'Usuarios no encontrados.'}

        return JsonResponse(datos)
    
    # @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Llave que identifica el sistema, en base 64.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='contraseña en base64.'),
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema donde el usuario esta iniciando sesión.'),
                'timeExp': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número de horas de la vigencia del token; si número de horas es 0, entonces por default el token durara 3 hrs.'),
                'saveTk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Indica si se desea guardar el token en la base de datos, por defecto su valor es 0 (No se almacena Token).'),
            },
            required=['token', 'user', 'password','idSistema','timeExp']
        ),
        responses={200: 'Usuario loggeado exitosamente'},
    )    


    def post(self,request):
        """
        Realiza la validación de las credenciales de los usuarios.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        #Metodo Post
        #Este metodo se encarga de validar las credenciales del ususario que se esta loggeando al sistema,
        # como resultado obtiene (mediante el userName, password, idSistema y Token) los permisos y grupos del usuario.

        try:
            #1. Carga los valores del json obtenido por el metodo post.
            jd = json.loads(request.body)
            # print(jd)
            datos = {}
            info = {}
            
            #Declaración y asignación de variables
            bValido = True
            
            bKey = False
            bKeyTkG = False
            bKeyRF = False

            #ARSI 19/03/2025 SE AGREGA saveTk A CAMPOS A VERIFICAR DEL JSON ENVIADO EN LA SOLICITUD.
            dCamposJson = ['token', 'user', 'password','idSistema', 'timeExp', 'saveTk']

            sTexto = ""
            pwdD64 = ""
            dUsuario = ""
            existeUsuario = ""
            dSistema = ""
            dDatosPersonales = {}
            dPermisos = {}
            dGrupos = {}
            password = ""
            sistema = 0
            idPersonal = 0
            sNombreCompleto = ""
            sUserName = ""
            dFechaNac = ""
            sRutaFoto =  ""
            nNoEmpleado = 0
            sProyectoActual = "" #Se crea  variable de proyecto actual
            sPuestoActual = ""  #Se crea variable de puesto actual
            idPuestoActual = 0  #Se crea variable de id del puesto actual
            idProyectoActual = 0 #Se crea variable de id proyecto actual
            idArea= "" #ARSI 30/11/2024 SE CREA VARIABLE QUE CONTENDRA ID AREA RELACIONADO A LA CATEGORIA DEL EMPLEADO.
            sNombreArea = "" #ARSI 30/11/2024 SE CREA VARIABLE QUE CONTENDRA NOMBRE DEL AREA RELACIONADO A LA CATEGORIA DEL EMPLEADO.
            nDir = 0 #ARSI 15/03/2025 SE CREA VARIABLE QUE CONTENDRA EL ID DE DIRECCION RELACIONADO A LA CATEGORIA DEL EMPLEADO.
            sNombreDir = "" #ARSI 15/03/2025 SE CREA VARIABLE QUE CONTENDRA EL NOMBRE DE DIRECCION RELACIONADO A LA CATEGORIA DEL EMPLEADO.
            idCor = "" #ARSI 22/03/2025 SE CREA VARIABLE QUE CONTENDRA EL ID DE COORDINACION 
            sNombreCor = "" #ARSI 22/03/2025 SE CREA VARIABLE QUE CONTENDRA EL NOMBRE DE COORDINACION
            idGer = "" #ARSI 22/03/2025 SE CREA VARIABLE QUE CONTENDRA EL ID DE GERENCIA
            sNombreGer = "" #ARSI 22/03/2025 SE CREA VARIABLE QUE CONTENDRA EL NOMBRE DE GERENCIA
            tokenApi = ""
            nItemJson = 0
            keySis = ""
            #total de items permitidos en la API, definidos en la diccionario dCamposJson
            nLenDef = len(dCamposJson) 
            #Variable que almacenara el numero de items del json recibido por la API.
            numero_de_items = 0 
            bPasswordCorrecta = False
            bParametroCorrecto = False
            sListSistemasPermitidos = {}
            gtkg = ""
            nStatus = 0
            opc = 3
            sTextoTkg = ""
            dUsTk = ""
            tkgbl = ""
            infoTkg = {}
            bExisteTkg = False   
            dListaProyectos = {} #ARSI 25092024 VARIABLE QUE ALMACENA EL LISTADO DE PROYECTOS DONDE EL EMPLEADO ESTUVO INVOLUCRADO

           
            #ARSI 19/03/2025 SE VALIDA SI EXISTE LA CLAVE SAVETK, en caso de no existir (porque no es obligatoria, se agrega al diccionario
            #y se asigna valor de 0).
            #Validación de las claves json, si alguna clave no se encuentra en el objeto, entonces
            #el valor de bValido es Falso y regresa un mensaje de error indicando el identificador
            #  faltante.
            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    if item == 'saveTk':
                        print("CAutenticacion - El campo saveTk no se encuentra en el JSON, se asigna valor de 0.")
                        jd['saveTk'] = 0
                        continue
                    else:
                        sTexto += "El campo faltante es: "+item+". "
                        bValido = False
                        break

            #ARSI 19/03/2025 se valida tamaño de claves del JSON enviado a la API
            #Valida que el numero de claves del JSON enviado a la API
            #coincida con el numero de claves declaras en el diccioario dCamposJson
            nItemJson = len(jd)
            
            if nItemJson != nLenDef:
                sTexto += "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False
            
            #si las claves estan correctas, continuara realizando el resto del proceso
            # de autenticación
            if bValido:
                print("1 ) Tamaño y nombre de claves de JSON obtenido, validos.")

                print("1.1 ) Validando saveTk: "+str(jd['saveTk']))
                
                #ARSI 19/03/2025 SE CREA VARIABLE nSaveTk
                nSaveTk = int(jd['saveTk'])

                # IMPORTANTE!
                # Intranet tiene el id de sistema 3, Reconocimiento facial tiene el id de sistema 4.

                #2. Compara el token obtenido del json contra el secretKey de la aplicación.
                # 2.1. Para el sistema de RF (Reconocimiento Facial) el  token =4  - KEY_RF
                # keySis = base64.b64decode(jd['token'])
                # keySis = keySis.decode('utf-8')
                skTk = str(jd['token'])
                # keySis = self.decodificarB64(jd['token'])
                keySis = self.decodificarB64(skTk)
                #print(keySis)

                # print(keySis)
                # print(os.environ.get('KEY_RF'))

                if keySis == str(os.environ.get('SECRET_KEY')):
                    bKey = True
                elif keySis == str(os.environ.get('KEY_RF')):
                    bKeyRF = True
                elif keySis == str(os.environ.get('KEY_GTKG')):
                    bKeyTkG = True
                elif keySis == str(os.environ.get('KEYVALIDADJG')):
                    sTextoTkg += ". Intento de loggeo por Token Global."
                    bKeyTkG = True
                else:
                    sTexto += 'El key del sistema es incorrecto.'
                    nStatus = 404
                    bValido = False
                    
               
                 #ARSI 20/02/2024 valida llaves: Llave que permite consumir api, llave para reconocimiento facial y la llave para Token Global
                #  ARSI 22/04/2024 Reutilizar variable bValido, si bValido hasta aqui es correcto, entonces quiere decir que paso los filtros de tamaño de json y que la secret key es correcta
                # if((keySis == str(os.environ.get('SECRET_KEY'))) or (keySis == str(os.environ.get('KEY_RF'))) or (keySis == str(os.environ.get('KEY_GTKG')))):
                if bValido:
                    
                    print("2 ) Secret key valida.")
                    #Valida si el sistema existe en el catalogo de sistemas.
                    # consultarSistema
                    # dSistema = list(Sistemas.objects.filter(id=jd['idSistema']).values())
                    dSistema = self.consultarSistema(jd['idSistema'])
                    if len(dSistema)>0:
                        sistema = dSistema[0]['id']
                        # self.sNombreSistema = dSistema[0]['nombre']
                    
                    #Si el sistema obtenido se encuentra en el catalogo de sistemas...
                    if sistema>0:
                        print("3 ) Id de sistema valido. ")

                        #Anter de continuar con las validaciones del usuario, verificamos que el usuario no este bloqueado 
                        #por intentos de sesión fallidos.
                        info = self.registrarAcceso(jd['user'],jd['idSistema'],"","",True)

                        
                        if info['message'] == "bloqueado":
                            nStatus = 404
                            sTexto = info['texto']
                            datos = {'message': info['message'], 'error': sTexto} 
                        else:
                            # pass
                            if keySis!=os.environ.get('KEY_RF'):
                                print("4.1 ) En caso de que el Key sea básico, Token Global o llave de credenciales validadas por django se debe validar la contraseña y el usuario.")
                            
                            
                                #Obtiene el registro del usuario mediante el userName.
                                # dUsuario = list(User.objects.filter(username=jd['user'], is_active=1).values())
                                existeUsuario = self.consultarExisteUsuario(jd['user'])
                                dUsuario = self.consultarUsuarioActivo(jd['user'])


                                if len(existeUsuario)>0:
                                    if len(dUsuario):
                                        # password = dUsuario[0]['password']
                                        idUsuario = dUsuario[0]['id']
                                        
                                        #print("paso 2")

                                        # Si la clave obtenida NO es la llave de validado por django, entonces verifica la password.
                                        if keySis!=os.environ.get('KEYVALIDADJG'):
                                            #3. Decodifica el password en base64
                                            # pwdD64 = base64.b64decode(jd['password'])
                                            #decodificarB64
                                            sPwd = str(jd['password'])
                                            # pwdD64 = self.decodificarB64(jd['password'])
                                            pwdD64 = self.decodificarB64(sPwd)

                                            bPasswordCorrecta = self.verificarPswd(pwdD64)
                                        else:                                            
                                            bPasswordCorrecta = True

                                        if not bPasswordCorrecta:
                                            opc = 2
                                            sTexto += "¡Ups! la contraseña es incorrecta."
                                            info = self.registrarAcceso(jd['user'],sistema,sTexto+" Desde el sistema "+self.sNombreSistema+sTextoTkg,opc)
                                            bValido = False
                                            sTexto += " "+info['texto']
                                            
                                            
                                    else:
                                        bValido = False
                                        sTexto += "Usuario inactivo"
                                else:
                                    bValido = False
                                    sTexto += "No existe el usuario proporcionado."
                            else:
                                try:
                                    idPersonal = int(jd['user'])   
                                except ValueError:
                                    bValido = False
                                    nStatus = 404
                                    sTexto += "Ingreso un Id de personal invalido, debe ser un numero entero."                       
                                else:
                                    # if idPersonal <= 0:
                                    bParametroCorrecto = True
                                                        
                            if  bValido:
                                    # print("Las contraseñas son iguales")
                                    
                                    #Listado de permisos
                                    # dPermisos = list(SistemaPermiso.objects.filter(sistema_id=sistema).values())
                                    if bPasswordCorrecta: 
                                        dDatosPersonales = self.obtenerDatosPersonales(idUsuario,0)
                                    elif bParametroCorrecto:
                                        dDatosPersonales = self.obtenerDatosPersonales(0,idPersonal)
                                    else:
                                        print("No se recuperaron datos del usuario.")
                                    
                                    if len(dDatosPersonales)>0:
                                        #print(dDatosPersonales[0][1])
                                        idPersonal = dDatosPersonales[0][1]
                                        sNombreCompleto = dDatosPersonales[0][9]
                                        idUsuario = dDatosPersonales[0][0]                               
                                        sUserName = dDatosPersonales[0][3]
                                        dFechaNac = dDatosPersonales[0][22]
                                        sRutaFoto =  dDatosPersonales[0][12]
                                       

                                        nNoEmpleado = dDatosPersonales[0][2]
                                        sProyectoActual = dDatosPersonales[0][20]
                                        sPuestoActual = dDatosPersonales[0][13]
                                        idPuestoActual = dDatosPersonales[0][23]
                                        idProyectoActual = dDatosPersonales[0][24]

                                        #ARSI 30/11/2024 
                                        idArea= dDatosPersonales[0][25]
                                        sNombreArea = dDatosPersonales[0][26]

                                        #ARSI 15/03/2025
                                        sNombreDir = dDatosPersonales[0][14]
                                        nDir = dDatosPersonales[0][27]

                                        #ARSI 22/03/2025
                                        idCor = dDatosPersonales[0][28]
                                        sNombreCor = dDatosPersonales[0][29]
                                        idGer = dDatosPersonales[0][30]
                                        sNombreGer = dDatosPersonales[0][31]


                                        
                                        dUsuario = self.consultarUsuarioActivo(sUserName)
                                         #ARSI 08/11/2024 
                                        # sRutaFoto = self.photo_view(sUserName)

                                        if len(dUsuario):
                                            dPermisos = self.obtenerPermisos(sistema,idUsuario)
                                            dGrupos = self.obtenerGrupos(sistema,idUsuario)

                                            if len(dPermisos)==0 & len(dGrupos)==0:
                                                bValido = False
                                                sTexto += "El usuario no cuenta con permisos para acceder a este sistema."

                                            if bValido:
                                                # print("Nombre de grupos a los que pertenece el usuario: ")
                                                # print(self.dGruposAsigUsuario)

                                                #El listado de permisos de grupos se unen al bloque permisos, todo junto.
                                                dPermisos.update(dGrupos)
                                                

                                            
                                                # resultados = vUsuarioPermiso.objects.all()

                                                # if len(dPermisos)>0:
                                                #     print("resultados :) ")  
                                                    
                                                # else:
                                                
                                                #     sTexto += "Este sistema no tiene permisos"

                                                
                                                # datos = {'message': 'Success', 'datos': dUsuario}
                                                # datos = {'message': 'Success', 'sistema':self.sNombreSistema,'permisos': dPermisos, 'grupos':dGrupos}
                                                # token, created = Token.objects.get_or_create(username=jd['user'])
                                                if jd['timeExp'] == 0:
                                                    print("El tiempo de expiración es 0, por lo tanto por default el token durara 3 horas.")
                                                    # tokenApi = self.get_custom_auth_token(jd['user'])
                                                    tokenApi = self.get_custom_auth_token(sUserName)
                                                else:
                                                    print("El tiempo de expiración no es igual 0, por lo tanto por default el token durara "+str(jd['timeExp'])+" horas.")
                                                    # tokenApi = self.get_custom_auth_token(jd['user'],jd['timeExp'])
                                                    tokenApi = self.get_custom_auth_token(sUserName,jd['timeExp'])

                                                # print(tokenApi)

                                                # Cuando el sistema sea el sistema intranet de la empresa entonces...
                                                # Obtener listado de sistemas a los que tiene acceso el usuario, dado que
                                                # en intranet esta el listado completo de los sistemas.

                                                # print(type(os.environ.get('ID_INTRANET')))
                                                # print(type(sistema))
                                                if(sistema == int(os.environ.get('ID_INTRANET'))):
                                                    print("El sistema de intranet es el mismo...")
                                                    sListSistemasPermitidos = self.obtenerSistemasUsuario(idUsuario)


                                                #Generar el tokenGlobal :) si la key es de token global o si el sistema es intranet se crea el Token global.
                                                if (keySis == os.environ.get('KEY_GTKG')) | (sistema == int(os.environ.get('ID_INTRANET'))):
                                                    print(">> Se solicita generar TKG.")      

                                                                                              

                                                    #Se consulta si existe token global asignado al usuario y que ademas este sea valido.
                                                    dUsTk = list(TokenGlobal.objects.filter(username=sUserName, caduco=0).values())

                                                    #ARSI 04062024 Se agrega validación para verificar e inactivar el TKGLOBAL cuando el usuario inicie sesión en intranet.
                                                    #o pase el key para generar token Global.
                                                    if len(dUsTk)>0:
                                                        print("Si devuelve datos de la consulta.")
                                                        tkgbl = dUsTk[0]['token']
                                                        infoTkg = CVerificaTokenGlobal.validarTokenGlobal(sUserName,tkgbl);
                                                    else:
                                                        infoTkg['message'] = 'Error'
                                                    
                                                    if len(infoTkg)>0:
                                                        if infoTkg['message']=="Error":                                                                                                                                                    
                                                                # if len(dUsTk) == 0:
                                                                # insertar TKG en BD 05/03/2024
                                                                # sTimeExp = 0
                                                                if jd['timeExp'] == 0:
                                                                    sTimeExp = 3
                                                                else:
                                                                    sTimeExp = jd['timeExp']

                                                                # gtkg = self.generarTKGlobal(jd['user'],sTimeExp,sistema)
                                                                # insertTkG = TokenGlobal(username=jd['user'], token=gtkg,sistemaOrigen=sistema, caduco=0)

                                                                #ARSI 04062024 Que el sistema origen para generar TK global sea siempre el de intranet
                                                                gtkg = self.generarTKGlobal(jd['user'],sTimeExp,int(os.environ.get('ID_INTRANET')))
                                                                insertTkG = TokenGlobal(username=sUserName, token=gtkg,sistemaOrigen=int(os.environ.get('ID_INTRANET')), caduco=0)
                                                                insertTkG.save()
                                                        else:
                                                                print(">> Si existe token Global registrado...")      
                                                                gtkg = dUsTk[0]['token']
                                                    
                                                                                            
                                                    
                                                    

                                                    
                                                    #Si el consumo de la Api tiene el key para generar Token Global
                                                    #paso 1) Se consulta en Base de datos si el usuario cuenta con TKG activo
                                                    #paso 2) En caso de que el usuario no cuente con TKG activo, entonces se inserta uno
                                                    #paso 3) En caso de que exista un TKG en base de datos, se verifica que este aun activo, si no lo esta, entonces borrar.
                                                    #paso 4) En caso de que exista un TKG en BD, y si aun esta activo, entonces permanecer con dicho TKG.
                                    
                                                    # is_token_valid = default_token_generator.check_token(jd['user'], tokenApi)
                                                #ARSI 25092024 SE AGREGA CONSULTA PARA OBTENER TODOS LOS PROYECTOS EN LOS QUE EL EMPLEADO ESTUVO INVOLUCRADO. 
                                                dListaProyectos = self.obtenerProyectoAsignadosEmpleado(idPersonal)
                                                
                                                #ARSI 19/03/2025 ALMACENAR TOKEN EN LA BASE DE DATOS
                                                opc = 1
                                                print("Valor de nSaveTk es igual a:")
                                                print(nSaveTk)
                                                if nSaveTk==0:
                                                    print("No Guardar el token en la base de datos.")
                                                    info = self.registrarAcceso(sUserName,sistema,"Inicio de sesión exitoso al sistema "+self.sNombreSistema+sTextoTkg,opc)
                                                elif nSaveTk == 1:
                                                    print("Guardar el token en la base de datos.")
                                                    info = self.registrarAcceso(sUserName,sistema,"Inicio de sesión exitoso al sistema "+self.sNombreSistema+sTextoTkg,opc,False,1,tokenApi)

                                                nStatus = 200
                                                datos = {'message': 'Success','idPersonal':idPersonal,
                                                         'nNoEmpleado':nNoEmpleado,'usuario': sUserName, 
                                                         'sistema':self.sNombreSistema,
                                                         'nombreCompleto':sNombreCompleto,
                                                         'token': tokenApi,
                                                         'grupos':self.dGruposAsigUsuario,
                                                         'permisos': dPermisos,'sistemas':sListSistemasPermitidos, 
                                                         'tkg':gtkg, 'fechaNac':dFechaNac, 'rutaFoto':sRutaFoto, 
                                                         'expira':self.intTiempoExpira,'idProyectoActual':idProyectoActual ,
                                                         'proyectoActual':sProyectoActual,'idPuestoActual':idPuestoActual,
                                                         'puestoActual':sPuestoActual,'dHistoricoProyectosAsignados':dListaProyectos,
                                                         'idArea':idArea,'sNombreArea':sNombreArea, 'idDir':nDir,
                                                         'sNombreDir':sNombreDir,
                                                         'idCor':idCor,'sNombreCor':sNombreCor,
                                                         'idGer':idGer,'sNombreGer':sNombreGer
                                                         }
                                            else:
                                                nStatus = 404
                                                datos = {'message': 'Acceso denegado', 'error':sTexto}
                                        else:
                                            nStatus = 404
                                            sTexto = 'Usuario inactivo'
                                            datos = {'message': 'Sin datos', 'error':sTexto}
                                    else:
                                        nStatus = 404
                                        sTexto = '¡Ups! Al parecer no existen registros de este empleado, por favor de verificar los datos proporcionados. '
                                        datos = {'message': 'Sin datos', 'error': sTexto}
                            else:
                                nStatus = 404                            
                                datos = {'message': 'Dato Invalidos', 'error':sTexto}

                        # elif  sistema==4 and keySis==os.environ.get('KEY_RF'):
                        #TODO de aqui hacia abajo se comento la 2da opcion de validaciones para toke de Reconocimiento facial...
                        # elif  keySis==os.environ.get('KEY_RF'):

                        #     print("Petición recibida por parte del API de reconocimiento facial.")

                        #     idPersonal = int(jd['user'])
                        #     dDatosPersonales = self.obtenerDatosPersonales(0,idPersonal)

                        #     if len(dDatosPersonales)>0:
                        #             print(dDatosPersonales[0][1])
                        #             idUsuario = dDatosPersonales[0][0]
                        #             sNombreCompleto = dDatosPersonales[0][9]                                   
                        #             sUserName = dDatosPersonales[0][3]

                        #             dPermisos = self.obtenerPermisos(sistema,idUsuario)
                        #             dGrupos = self.obtenerGrupos(sistema,idUsuario)

                        #             dPermisos.update(dGrupos)

                         

                        #             if jd['timeExp'] == 0:
                        #                 print("El tiempo de expiración es 0, por lo tanto por default el token durara 3 horas.")
                        #                 tokenApi = self.get_custom_auth_token(sUserName)
                        #             else:
                        #                 print("El tiempo de expiración no es igual 0, por lo tanto por default el token durara "+str(jd['timeExp'])+" horas.")
                        #                 tokenApi = self.get_custom_auth_token(sUserName,jd['timeExp'])

                        #             datos = {'message': 'Success','idPersonal':idPersonal,'usuario': sUserName, 'sistema':self.sNombreSistema,'nombreCompleto':sNombreCompleto,'token': tokenApi,'grupos':self.dGruposAsigUsuario,'permisos': dPermisos}                        
                        #     else:
                        #         datos = {'message': 'Sin datos', 'error':'¡Ups! Al parecer no existen registros de este usuario, por favor de verificar los datos proporcionados. '}                        
                    else:
                        nStatus = 404
                        sTexto = 'Id de sistema invalido'
                        datos = {'message': 'Dato Invalidos', 'error': sTexto}                   
                else:
                    # datos = {'message': 'Dato invalido.', 'error': 'El key del sistema es incorrecto.'}
                    nStatus = 404
                    datos = {'message': 'Dato invalido.', 'error': sTexto}
            else:
                nStatus = 404
                datos = {'message': 'JSON invalido.', 'error': sTexto}

            if opc == 3:
                info = self.registrarAcceso(jd['user'],jd['idSistema'],sTexto+sTextoTkg,opc)
                print(info)
            
        except ValueError as error:
            nStatus = 404
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}
        except json.JSONDecodeError as e:
            nStatus = 404
            sTexto = "%s" % e
            print('Error al decodificar JSON:', e)
            datos = {'message': 'JSON invalido. ', "error": sTexto}
            # return False
        

        
        # elif opc == 2:
        #     #El usuario se equivoco en la contraseña.
        #     info = self.registrarAcceso(jd['user'],jd['idSistema'],sTexto,opc)

        #     datos = {'message': 'Dato Invalidos', 'error':sTexto}

        #     if info['message'] == 'bloqueado':
        #         pass
        #     else:
        #         pass
        # else:
        #     pass
        

       # print(datos)

        return JsonResponse(datos,status= nStatus)
    
    
    # def put(self,request):
    #     pass

    # def delete(self,request):
    #     pass


# EMC 09/11/24 :
# La clase `CPhotoView` es una API basada en `APIView` que responde a solicitudes POST para obtener la foto de perfil de un usuario.
# A través del parámetro `username` en el cuerpo de la solicitud, la API verifica si el usuario existe en la base de datos y, si tiene una ID personal asociada, intenta localizar su imagen en una ruta predefinida.
class CPhotoView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
            },
            required=[ 'username' ]
        ),
        responses={200: 'Usuario loggeado exitosamente'},
    )  

    def post(self, request, *args, **kwargs):
        """
        Obtiene la foto del usuario.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        username = request.data.get('username')
        if not username:
            print("Error: No se proporcionó el nombre de usuario en la solicitud.")
            return HttpResponse("Nombre de usuario no proporcionado.", status=400)
        
        print(f"Intentando obtener la foto del usuario: {username}")

        # Buscar el usuario en la base de datos
        usuarioBD = VallEmpleado.objects.filter(username=username).first()
        if usuarioBD:
            print(f"Usuario encontrado: {usuarioBD.username}, ID Personal: {usuarioBD.Id_personal}")
        else:
            print("Error: Usuario no encontrado en la base de datos.")
            return HttpResponse("Usuario no encontrado.", status=404)

        # Validar si tiene una ID personal asociada
        if not usuarioBD.Id_personal:
            print(f"El usuario '{username}' no tiene ID personal asociada.")
            return HttpResponse("El usuario no tiene una ID personal asociada.", status=404)

        # Determinar la ruta del archivo en función del entorno
        entorno = os.environ.get('DJANGO_ENV')
        if entorno == 'development':
            file_path = f'//intranet.grupo-iai.com.mx/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.Id_personal}.jpg'
        elif entorno == 'production':
            file_path = f'C:/xampp/htdocs/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.Id_personal}.jpg'
        else:
            print("Error: Valor de entorno no válido.")
            return HttpResponse("El valor de 'entorno' no es válido", status=400)

        print(f"Ruta del archivo determinada: {file_path}")

        # Verificar si el archivo existe en la ruta especificada
        if os.path.exists(file_path):
            try:
                print(f"El archivo existe. Preparando para enviar la imagen de {username}.")
                return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
            except FileNotFoundError:
                print("Error: Archivo no encontrado al intentar abrirlo.")
                return HttpResponse("Imagen no encontrada o acceso denegado", status=404)
        else:
            print(f"Error: El archivo no existe en la ruta especificada: {file_path}")
            return HttpResponse("Imagen no encontrada en la ruta especificada", status=404)


# EMC 11/11/24 : La clase `EnviarCorreoAPIView` es una API basada en `APIView` que responde a solicitudes POST para obtener el envio de correos.
class EnviarCorreoAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'asunto': openapi.Schema(type=openapi.TYPE_STRING, description='Asunto del correo.'),
                'destinatarios': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='Lista de destinatarios (correos electrónicos).'
                ),
                'contexto_html': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Contenido HTML del correo',
                    properties={
                        "sistema": openapi.Schema(type=openapi.TYPE_STRING, description="Sistema que envía el correo"),
                        "contenido": openapi.Schema(type=openapi.TYPE_STRING, description="Contenido del mensaje en HTML"),
                        "URL": openapi.Schema(type=openapi.TYPE_STRING, description="URL para incluir en el correo")
                    }
                ),
                'cco': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='Lista de destinatarios en copia oculta (opcional).',
                )
            },
            required=['asunto', 'destinatarios', 'contexto_html']
        ),
        responses={200: 'Correo enviado exitosamente'},
    )
    def post(self, request):
        """
        Se encarga de enviar correos.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
        """
        # Obtener los datos de la solicitud
        asunto = request.data.get("asunto")
        destinatarios = request.data.get("destinatarios")
        mensaje_html = request.data.get("contexto_html")
        cco = request.data.get("cco", [])  # Lista de CCO opcional

        # Validar los campos requeridos
        if not (asunto and destinatarios and mensaje_html):
            return Response(
                {"error": "Asunto, destinatario y contexto_html son obligatorios"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Crear instancia de EnvioCorreos y enviar
        correo = EnvioCorreos(asunto, destinatarios, mensaje_html, cco=cco)
        resultado = correo.enviar()

        # Responder según el resultado del envío
        if resultado["status"] == "success":
            return Response({"status": "success", "message": resultado["message"]}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "message": resultado["message"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Protegida(APIView):
    # permission_classes = [IsAuthenticated]
    
    # def get(self, request):
        
    #     datos = {'content': 'Esta vista está protegida'}
    #     # return Response({"content": "Esta vista está protegida"})  
    #     return JsonResponse(datos)  

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.')
            },
            required=['user']
        ),
        responses={200: 'Token invalido'},
    ) 
    def post(self,request):
        """
        Realiza la revocación del token dado por la api de autenticación.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """

        nLenDef = 0
        nItemJson = 0
        sTexto = ""
        bValido = True
        sToken_encoded = ""
        sUserName = ""

        dCamposJson = ['user']
            
        jd = json.loads(request.body)

        nLenDef = len(dCamposJson) 

        nItemJson = len(jd)
            
        if nItemJson != nLenDef:
            sTexto = "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
            bValido = False

        for item in dCamposJson:
            if item in jd:
                continue
            else:
                sTexto += " El campo faltante es: "+item+". "
                bValido = False
                break

        try:
            if bValido:
                sUserName = jd['user']
                user = User.objects.get(username=sUserName) 
                timestamp = int(timezone.now().timestamp())

                # Calcular la fecha de expiración del token
                expiration_time = timestamp + (1 * 1)  # El tipo de vida del token una vez que se cierre sesión será de 1 minuto.
                
                token = default_token_generator.make_token(user)+ ',' + str(expiration_time)
    
                sToken_encoded = urlsafe_base64_encode(force_bytes(token))

                # print("Token de 1 minuto: ")
                # print(sToken_encoded)

                datos = {'message': 'Success'}
            else:
                datos = {'message': 'Error en la recepción de datos.', "error": sTexto}
        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Ocurrió un error al generar el token para el usuario. ', "error": sTexto}

        return JsonResponse(datos)
    

class CVerificaToken(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token asignado por la aplicación.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'saveTk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Valor que determina si basar la verificación del token en el que este almacenado y activo en la BD, opcional'),
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema de donde viene el token; colocar NA en caso de que no aplique.')
            },
            required=['token', 'user']
        ),
        responses={200: 'Token Validado', 403: 'Json invalido o problemas internos en el server.', 404:'Datos invalidos'},
    ) 
    def post(self,request):
        """
        Realiza la validación del token dado por la api de autenticación.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        #ARSI 20/03/2025 se agrega el parametro saveTk para verificar en BD si existe el token activo correspondiente a la sesión del usuario.
        try:
            bValido = True
            sToken_encoded = ""
            sUserName = ""
            tk = ""
            is_token_valid = False
            is_token_expired = True
            sTexto = ""
            nLenDef = 0
            nItemJson = 0
            nStatus = 0

            dCamposJson = ['token', 'user','saveTk','idSistema']
            
            jd = json.loads(request.body)

            nLenDef = len(dCamposJson) 

           
            dDatos = []
            dDatosValidarTkBD = []
            bSistInvalid = False #ARSI 20/03/2025 VARIABLE QUE ALMACENA SI EL TIPO DE DATO PARA EL PARAMETRO ID SISTEMA ES VALIDO
            bSistNA = False  #ARSI 20/03/2025 VARIABLE QUE ALMACENA SI EL ID SISTEMA VIENE DEFINIDO COMO NA
            bStkValid = False
            
            #ARSI 20/03/2025 se valida si existen los parametros savetk e idSistema, en caso de que no, se asigna valores entendibles para el sistema.
            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    # if item == 'saveTk':
                    #     pass
                    # sTexto += " El campo faltante es: "+item+". "
                    # bValido = False
                    # break

                    #ARSI 20/03/2025 
                    if item == 'saveTk':
                        print("CVerificaToken - El campo saveTk no se encuentra en el JSON, se asigna valor de 0.")
                        jd['saveTk'] = 0
                        continue
                    elif item == 'idSistema':
                        print("CVerificaToken - El campo idSistema no se encuentra en el JSON, se asigna valor de NA.")
                        jd['idSistema'] = "NA"
                        continue
                    else:
                        
                        sTexto += "El campo faltante es: "+item+". "
                        bValido = False
                        break

            nItemJson = len(jd)
            


            if (jd['token'].isspace() or len(jd['token']) <= 1):
                sTexto += "El item token es muy corto o viene vacio. "
                nStatus = 404
                bValido = False

            if (jd['user'].isspace() or len(jd['user']) <= 1):
                sTexto += "El item de usuario es muy corto o viene vacio. "
                nStatus = 404
                bValido = False


            # print("Valor de saveTk: bueno tipo: ")
            # print(type(jd['saveTk']))

            if isinstance(jd['saveTk'],int):
                if ((jd['saveTk'] !=0 and jd['saveTk'] !=1)):
                    sTexto += "El item de saveTk debe contener el valor entero 0 o 1. "
                    nStatus = 404
                    bValido = False

                if (jd['saveTk'] ==1):
                    bStkValid = True

            elif isinstance(jd['saveTk'],str):
                if (jd['saveTk']== "" or jd['saveTk'].isspace() or jd['saveTk'] !="0" or jd['saveTk'] !="1"):
                    sTexto += "El item de saveTk debe contener el valor entero 0 o 1; no caracteres alfanumericos. "
                    nStatus = 404
                    bValido = False

            
            if isinstance(jd['idSistema'],int):                       
                if (jd['idSistema']<=0):
                    sTexto += "El item de idSistema debe contener algún id de sistema valido o si no aplica, colocar NA. "
                    nStatus = 404
                    bValido = False
                    bSistInvalid = True
            if isinstance(jd['idSistema'],str):
                if (jd['idSistema'] !='NA' or jd['idSistema'] == '' or jd['idSistema'].isspace()):
                    sTexto += "El item de idSistema debe contener algún valor numerico que indique el Id del sistema valido o si no aplica, colocar NA. "
                    nStatus = 404
                    bValido = False
                    bSistInvalid = True
                elif(jd['idSistema'] == "NA"):
                    bSistNA = True

            #bStkValid                        
            #if jd['saveTk'] ==1 and ((bSistInvalid) or bSistNA ):
            if bStkValid and ((bSistInvalid) or bSistNA ):

                sTexto += "El item saveTk es igual a 1, por lo tanto el valor de idSistema debe estar definido. "
                nStatus = 404
                bValido = False

            if nItemJson != nLenDef:
                sTexto += "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False


        
            if bValido:
                print("CVerificaToken - Verificar token ...")
                
                oAuth = CAutenticacion()
                sToken_encoded = jd['token']
                sUserName = jd['user']
                # nVerifyTk = jd['saveTk']
                # nIdSistema = jd['idSistema']
                
                #arsi 20/03/2025 se valida que el verifiTK sea 1 y que el sistema sea valido y no igual a NA
                if bStkValid and not bSistInvalid and not bSistNA:
                    print("CVerificacionToken - Requiere obtener token desde BD y validar el token");

                    dDatosValidarTkBD = self.validarTokenBD(sUserName,sToken_encoded,jd['idSistema'])

                    if dDatosValidarTkBD['valido'] == 1:
                       dDatos = self.validarToken(sUserName,sToken_encoded)
                    else:
                        
                        # dDatos["valido"] = dDatosValidarTkBD['valido']
                        # dDatos["Resultado"] = dDatosValidarTkBD['Resultado']
                        dDatos = dDatosValidarTkBD
                        #ARSI 23/03/2025 SI EL TOKEN DE LA BASE DE DATOS EN INVALIDO ELIMINA EL TOKEN DE LA bd.
                        oAuth.inactivarTokens(sUserName,jd['idSistema']);
                        
                else:
                    #ARSI 18/03/2025 COLOCAR ESTA LÓGICA DENTRO DE OTRO METODO...
                    print("CVerificacionToken - No requiere obtener token desde BD, solo validar el token");
                    dDatos = self.validarToken(sUserName,sToken_encoded)

                print("Datos obtenidos de validarToken: ");
                print(dDatos["valido"]);
                print(dDatos["Resultado"]);            

                # user = User.objects.get(username=sUserName) 
                
                # # tk = urlsafe_base64_decode(sToken_encoded)                
                # # tk = tk.decode('utf-8')
                # # print("Entra a decrypt ...")
                # tk = crfr.decrypt(sToken_encoded.encode()).decode()

                # # print(tk)
                #  # Separar el token y la marca de tiempo
                # parts = tk.split(',')

                # # print("Token ... :( por favor funciona: ")
                # # print(parts[0])
                
                # token_without_timestamp = '-'.join(parts[:-1])
                # timestamp = int(parts[-1])
                # # print("timestamp: ")
                # # print(timestamp)

                # # Calcular la fecha de expiración del token
                # # expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
                # expiration_time = timestamp  # 3600 segundos en una hora
                # # expiration_time = timestamp + (1 * 60)  # 60 segundos prueba de 1 min.

                # print(expiration_time)
                # print(timezone.now().timestamp())

                # if expiration_time > timezone.now().timestamp():
                #     print("Aun no expira el token")
                #     is_token_expired = False
                # # else:
                # #     print("El token ya expiro...")
                #     # is_token_expired = True

                # # is_token_valid = default_token_generator.check_token(user, tk)
                # is_token_valid = default_token_generator.check_token(user, parts[0])
                

                #if is_token_valid and not is_token_expired:
                if dDatos["valido"] == 1: #ARSI 18/03/2025
                    print("El token es válido y no ha expirado para este usuario...")
                    # is_token_expired = self.is_token_expired(tk)
                    # print(type(is_token_expired))
                    nStatus = 200
                    datos = {'message': 'Success', "descripcion":'El token es válido y no ha expirado.'}
                else:
                    
                    nStatus = 404
                    datos = {'message': 'Error', "descripcion":'El token ya no es válido y posiblemente ya expiro'}
                    print("El token no es válido.")
            else:
                nStatus = 404
                datos = {'message': 'Datos Invalidos ', 'Error': sTexto}


            
         
            # is_token_valid = default_token_generator.check_token(user, token)

            

        except ValueError as error:
            nStatus = 404
            
            sTexto += "%s" % error
            datos = {'message': 'JSON invalido 1. ', "error": sTexto}
            # return False
        except KeyError as error:
            nStatus = 403
            sTexto += "%s" % error
            datos = {'message': 'JSON invalido 2. ', "error": sTexto}

       
        print(datos)

        return JsonResponse(datos,status=nStatus)  
    
    #ARSI 18/03/2025 METODO PARA VERIFICAR SI EL TOKEN ES VALIDO.
    @staticmethod
    def validarToken(p_suser,p_token):
        sTexto = ""
        nValido = 0
        dDatos = []
        is_token_valid = False
        is_token_expired = True
        dDesencriptarTk = []

        try:
            print("Accede a metodo validarToken.")
        
                           
            #tk = crfr.decrypt(p_token.encode()).decode()
            #ARSI 21/03/2025 SE APLICA DESENCRIPTADO DE TOKENS
            dDesencriptarTk = CVerificaToken.desencriptarTk(p_token,True);

            if dDesencriptarTk['estado'] == "Success":
                

            # # Separar el token y la marca de tiempo               
            # parts = tk.split(',')

            
            # token_without_timestamp = '-'.join(parts[:-1])
            # timestamp = int(parts[-1])

                timestamp = dDesencriptarTk['expTime']
               
                # Calcular la fecha de expiración del token               
                expiration_time = timestamp  # 3600 segundos en una hora
                # expiration_time = timestamp + (1 * 60)  # 60 segundos prueba de 1 min.

                print(expiration_time)
                print(timezone.now().timestamp())
                user = User.objects.get(username=p_suser) 
                
                if expiration_time > timezone.now().timestamp():
                    print("validarToken - Aun no expira el token")
                    is_token_expired = False
                
                is_token_valid = default_token_generator.check_token(user, dDesencriptarTk['tokenDj'])
                    

                if is_token_valid and not is_token_expired:
                    print("validarToken - El token es válido y no ha expirado para este usuario...")
                    nValido = 1
                    sTexto = "El token es válido y no ha expirado."
            else:
                nValido = 0           
                sTexto += "Error en desencriptación del Token. "

        except ValueError as error: 
            nValido = 0           
            sTexto = "%s" % error
        except KeyError as error:
            nValido = 0
            sTexto = "%s" % error

        dDatos = {'valido': nValido, 'Resultado': sTexto}

        return dDatos


    #ARSI 21/03/2025 VALIDAR TOKEN DESDE BASE DE DATOS.
    @staticmethod
    def validarTokenBD(p_suser,p_token, idSistema):
        try:
            
            print("CVerificaToken - validarTokenBD  - Accede a método..")
            
            oAuth = CAutenticacion()
            dDatosTk = []
            dDesencriptarTkCliente = []
            dDesencriptarTkBD = []
            nValido = 0
            sTexto = ""
            dDatos = []

            #ARSI 21/03/2025 OBTENER TOKEN ACTIVO DE LA BASE DE DATOS
            dDatosTk = oAuth.obtenerTokenActivo(p_suser, idSistema)
            
            #ARSI 21/03/2025 verificar que el id de registro de token activo es mayor a 0 
            if dDatosTk['idReg']>0:
                print("CVerificaToken - validarTokenBD  - Se encontró registro de token activo en la BD.")

                if len(dDatosTk['token'])>0:
                    
                    #se desencripta token que viene del cliente y el token activo en la BD
                    dDesencriptarTkCliente = CVerificaToken.desencriptarTk(p_token,True);
                    dDesencriptarTkBD = CVerificaToken.desencriptarTk(dDatosTk['token'],True);
        
                    if dDesencriptarTkCliente['estado'] == "Success" and dDesencriptarTkBD['estado'] == "Success" :
                        print("CVerificaToken - validarTokenBD  - Token de cliente y token de BD desencriptado : OK ")

                        if dDesencriptarTkCliente['tk'] == dDesencriptarTkBD['tk']:
                            print("CVerificaToken - validarTokenBD  - Token de cliente y token de BD desencriptado coinciden : OK ")
                            nValido = 1
                            sTexto +="Token de cliente y token de BD coinciden. "
                        else:
                            sTexto +="Token de cliente y token de BD no coinciden. "
                            print("CVerificaToken - validarTokenBD  - Token de cliente y token de BD desencriptado coinciden : Error ")
                            

                    else:
                        sTexto +=" Error en desencriptación de Token. "
                        print("CVerificaToken - validarTokenBD  - Token de cliente y token de BD desencriptado : ERROR ")
                else:
                    sTexto +="No se encuentra token almacenado en BD. "
            else:
                 sTexto +="No se encuentra token activo en BD. "


        except ValueError as error: 
            nValido = 0           
            sTexto = "%s" % error
        except KeyError as error:
            nValido = 0
            sTexto = "%s" % error

        dDatos = {'valido': nValido, 'Resultado': sTexto}

        return dDatos

        

    @staticmethod
    def desencriptarTk(p_token, bSeparaTk =False):
        tk = ""
        dDatos = []
        estado = "Error"
        timestamp = 0
        tokenDj = ""
        sTexto = ""

        try:
            print("CVerificaToken - Accede a desencriptarTK. ")
            
            tk = crfr.decrypt(p_token.encode()).decode()

            if bSeparaTk:

                print("CVerificaToken - desencriptarTK - Solicita separar token y marca de tiempo")
                # Separar el token y la marca de tiempo               
                parts = tk.split(',')
                                  
                timestamp = int(parts[-1])
                tokenDj = parts[0]

                estado = "Success"
                sTexto+="Token desencriptado y separado con exito."
            else:
                estado = "Success"

                sTexto+="Token desencriptado con exito."
        
        except TypeError as error:
            tk = ""  
            sTexto += "- TypeError - "         
            sTexto += "%s" % error
        except ValueError as error: 
            tk = ""          
            sTexto += "- ValueError - " 
            sTexto += "%s" % error
        except KeyError as error:
            tk = ""  
            sTexto += "- KeyError - " 
            sTexto += "%s" % error
        except Exception as error:
            tk = ""  
            sTexto += "- Exception - " 
            sTexto += "%s" % error

        dDatos= {'estado':estado,'message': sTexto,'tk': tk, 'expTime': timestamp, 'tokenDj':tokenDj}

        print("CVerificaToken - desencriptarTK - Resultado final: "+estado+' - '+sTexto)

        return dDatos

class CVerificaTokenGlobal(APIView):

    tkgb = ""
    @staticmethod
    # def validarTokenGlobal(self,p_suser,p_token):
    def validarTokenGlobal(p_suser,p_token):
        print("--- Accede a metodo validarTokenGlobal ---")
        print("usuario: "+ p_suser)
        print("token: "+ p_token)

        datos = {}
        bValido = True
        sTexto = ""
        tkg= ""
        user = ""
        sUserName = ""
        nSistemaOrigen = 0
        ntam = 0
        nTamTot = 0
        ltam = []
        sSl = ""
        dUsTk = ""

        is_token_valid = False
        is_token_expired = True
        is_system_origin = False
        is_len = False
        is_signal = False

        sUserName = p_suser
        tkg = p_token  
        
        try:
            if sUserName=="":
                bValido = False
                sTexto += "El valor de usuario esta vacio."

            if tkg=="":
                bValido = False
                sTexto += "El valor de token esta vacio."

            if bValido:
                # sUserName = user
                # tkg = token           
                print("Los valores no vienen vacios...")     

                dUsTk = list(TokenGlobal.objects.filter(username=sUserName, caduco=0).values())

                if len(dUsTk)==1:
                    print("Se obtuvo token existente en la Base de datos.")     
                    #1. Obtenemos el id del sistema autorizado con el que se expiden los TKGLB
                    nSistemaOrigen = int(dUsTk[0]['sistemaOrigen'])

                    #2. Decodifica token Global.
                    tkDpt = crfr.decrypt(tkg.encode()).decode()

                    print(">> Se decodifica TKGBL : "+tkDpt) 

                    #3. Una vez decodificado el token, se obtiene el tamaño del token Global para compararlo con el tamaño registrado del token recibido.
                    ltam = tkDpt.split(os.environ.get('USGL'))
                    ntam = int(ltam[1])
                    nTamTot = len(ltam[0]+os.environ.get('USGL'))

                    #4. Se valida el tamaño del tokenGlobal.
                    if ntam == nTamTot:
                        is_len = True
                        print(">>tamaño de token OK : ")

                        #5. Se divide el token por su correspondiente separador
                        parts = tkDpt.split(',')

                        if len(parts)>0:
                            #6. Se valida el token generado por django.
                            user = User.objects.get(username=sUserName)
                            is_token_valid = default_token_generator.check_token(user,parts[0])

                            if is_token_valid:
                                print(">>valido para django :) ")

                            #7. Se verifica el tiempo de expiración del token Global.
                            timestamp = int(parts[1])
                            expiration_time = timestamp

                            if expiration_time > timezone.now().timestamp():    
                                print(">>TOken aun no expira.. ")                
                                is_token_expired = False #Si es false entonces el token aun no expira.


                            #8. Se verifica si el sistema origen ingresado al token sea el mismo con el que esta insertado en la BD,
                            if  int(parts[2]) == nSistemaOrigen and int(parts[2]) == int(os.environ.get('ID_INTRANET')) :
                                #TODO ahora mostrar si valida correctamente el id origen...
                                print(">>el id del sistema es valido :)")     
                                is_system_origin = True #Si es true entonces el sistema origen es el correcto.

                            #9. Se verifica si la marca agregada al token sea correcta.
                            sSl = parts[3]
                            
                            if sSl[:3] == os.environ.get('SIGNAL'):
                                is_signal = True
                                print(">>La señal existe en el token.")  

                            if is_len and is_token_valid and not is_token_expired and is_system_origin and is_signal:
                                sTexto = "El token Global es valido."
                                datos = {'message': 'Success', 'Resultado': sTexto}
                            else:
                                sTexto = "El token Global no es valido."

                                #Se actualiza registro de token. campo token vacio y campo caduco igual a 1
                                regAct = TokenGlobal.objects.get(username=sUserName, caduco=0)

                                regAct.caduco = 1
                                regAct.token = ""
                                regAct.save()
                                
                                datos = {'message': 'Error', 'Resultado': sTexto}

                else:
                     sTexto = "No existe Token Global para este usuario."
                     datos = {'message': 'Error', 'Resultado': sTexto}
            else:
                datos = {'message': 'Error', "error": sTexto}          
                            
        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Error', "Resultado": sTexto}
            # datos = {'message': 'Ocurrió un error al generar el token para el usuario. ', "error": sTexto}
        # else:
        #     pass

        print(datos)

        return datos

    

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={               
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'tkgbl': openapi.Schema(type=openapi.TYPE_STRING, description='Token asignado por la aplicación.'),            
            },
            required=['user', 'tkgbl']
        ),
        responses={200: 'Token Validado', 403: 'Json invalido o problemas internos en el server.', 404:'Datos invalidos', 401:'Token invalido, por lo tanto dicho token ha perdido autorización para acceder a diferentes sistemas o no existe.'},
    )
    
    def post(self,request):
        # datos = {'message': 'Success'}
        # 05/03/2024 Validación de TKG.
        """
        Realiza la validación del token global dado por la api de autenticación.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        try:
            jd = json.loads(request.body)
            nStatus = 403
            tkg = ""
            bValido = True
            dCamposJson = ['user','tkgbl']
            user = ""
            sUserName = ""
            nSistemaOrigen = 0
            ntam = 0
            nTamTot = 0
            ltam = []
            sSl = ""
            datos = {}

            is_token_valid = False
            is_token_expired = True
            is_system_origin = False
            is_len = False
            is_signal = False

            nLenDef = len(dCamposJson) 

            nItemJson = len(jd)
            
            if nItemJson != nLenDef:
                sTexto = "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False

            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    sTexto += " El campo faltante es: "+item+". "
                    bValido = False
                    break

            if bValido:
                print("CVerificaTokenGlobal - Se recibe user: "+jd['user'])
                print("CVerificaTokenGlobal - Se recibe Token: ")
                sUserName = jd['user']
                tkg = jd['tkgbl']

                datos = self.validarTokenGlobal(sUserName,tkg)

                if len(datos)>0:
                    # print(type(datos))

                    # print(datos['message'])

                    if datos['message'] == 'Success':
                        nStatus = 200
                    else:
                        nStatus = 401
                    



                
                #Inicio - validaciones de TKGBL
                # dUsTk = list(TokenGlobal.objects.filter(username=sUserName, caduco=0).values())

                
                # if len(dUsTk)==1:
                                    
                #     tkg = dUsTk[0]['token']
                #     nSistemaOrigen = int(dUsTk[0]['sistemaOrigen'])
                #     user = User.objects.get(username=sUserName) 

                #     # print("Se obtiene el token.")

                #     tkDpt = crfr.decrypt(tkg.encode()).decode()

                #     # print(tkDpt)
                    
                #     ltam = tkDpt.split(os.environ.get('USGL'))

                #     ntam = int(ltam[1])

                #     nTamTot = len(ltam[0]+os.environ.get('USGL'))

                #     if ntam == nTamTot:
                #         is_len = True

                #         parts = tkDpt.split(',')

                #         if len(parts)>0:
                #             # print(parts[0])
                            
                #             is_token_valid = default_token_generator.check_token(user,parts[0])
                #             # if is_token_valid:
                #             #     print("el token si es valido...")

                #             timestamp = int(parts[1])
                #             expiration_time = timestamp

                #             # print(expiration_time)
                #             # print( timezone.now().timestamp())

                #             if expiration_time > timezone.now().timestamp():                    
                #                 is_token_expired = False #Si es false entonces el token aun no expira.
                #             # else:
                #             #     print("Expirto token...")

                #             if nSistemaOrigen == int(parts[2]):
                #                 is_system_origin = True #Si es true entonces el sistema origien es el correcto.

                #             sSl = parts[3]

                #             if sSl[:3] == os.environ.get('SIGNAL'):
                #                 is_signal = True


                #         if is_len and is_token_valid and not is_token_expired and is_system_origin and is_signal:
                #             sTexto = "El token Global es valido."

                #             datos = {'message': 'Success', 'Resultado': sTexto}
                #         else:
                #             sTexto = "El token Global no es valido."

                #             #Se actualiza registro de token. campo token vacio y campo caduco igual a 1
                #             regAct = TokenGlobal.objects.get(username=sUserName, caduco=0)

                #             regAct.caduco = 1
                #             regAct.token = ""
                #             regAct.save()
                            
                #             datos = {'message': 'Error', 'Resultado': sTexto}


                # else:
                #      sTexto = "No existe Token Global para este usuario."
                #      datos = {'message': 'Error', 'Resultado': sTexto}

                #Fin - validaciones de TKGBL


            else:
                nStatus = 404
                datos = {'message': 'JSON invalido.', 'Resultado': sTexto}


        except ValueError as error:
            nStatus = 404
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "Resultado": sTexto}
        except KeyError as error:
            nStatus = 403
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}

        
        print(datos)
        print(nStatus)
        # return JsonResponse(datos)
    
        return JsonResponse(datos,status=nStatus)  
 
     
class CInactivaTkg():

    oExecSP = CEjecutarSP()
    returnValue = 0
    asunto =""
    titulo = ""
    subtitulo = ""
    contenido = ""
    
    def inactivarRegistrosTkg(self):

        try:
            self.oExecSP.ejecutarSP("inactivarTkg")
            print("pruebas...")
           

        except ValueError as error:
            sTexto = "Error en el metodo inactivarRegistrosTkg: %s" % error
            print(sTexto)
        else:
            print("Ejecucicón Correcta. ")
            
            returnValue = self.oExecSP.ejecutarSP("obtenerInactivos")

            if returnValue[0][0] == 0:
                print("OK: Los registros de Token Global se inactivaron exitosamente.")
                asunto ="Resultados de la ejecución del procedimiento Inactivar registros del TKG."
                titulo = "Registros inactivos exitosamente."
                subtitulo = ""
                contenido = "El siguiente correo es para notificar que el procedimiento para inactivar registros de TKG a media noche fue ejecutado con exito."
                self.enviarCorreo(asunto,titulo,contenido,subtitulo)
               
            else:
                print("FAIL: Favor de ejecutar nuevamente este script...")
                asunto ="Resultados de la ejecución del procedimiento Inactivar registros del TKG."
                titulo = "Problemas en la ejecución del proceso de registros inactivos."
                subtitulo = ""
                contenido = "El siguiente correo es para notificar que el procedimiento para inactivar registros de TKG a media noche no fue ejecutado con exito, por favor de ejecutar nuevamente el procedimiento manualmente."
                self.enviarCorreo(asunto,titulo,contenido,subtitulo)

            # print(os.environ.get('EMAIL_HOST'))     

            print(returnValue)

        return returnValue
    

    def enviarCorreo(self,asunto,titulo,contenido,subtitulo):
        current_year = datetime.now().year

        context = {
                'year': current_year,
                'titulo' : titulo,
                'Subtitulo' : subtitulo,
                'contenido' :contenido,                
                }
        
        html_content = render_to_string('NotificacionCorreoExterna.html', context)
        text_content = strip_tags(html_content)  # Esto crea una versión en texto plano del HTML

        email = EmailMultiAlternatives(
            asunto,  # Asunto
            text_content,  # Contenido en texto plano
            'sistemas.iai@grupo-iai.com.mx',  # Email del remitente
            ['ana.sanchez@grupo-iai.com.mx', 
             'eloy.mendoza@grupo-iai.com.mx', 
             'luis.dominguez@grupo-iai.com.mx',
             'manuel.zarate@grupo-iai.com.mx', 
             'jorge.torres@grupo-iai.com.mx' ]  # Lista de destinatarios
        )
        
        email.attach_alternative(html_content, "text/html")

        try:
            time.sleep(1) #para evitar que envie un moton de solicitudes 
            email.send()
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {e}")

        
class CMigraPermisos():

    idSistema = 0
    listaPermisosv1 = []

    def migrarPermisos(self,p_sSistema = None, p_Usuario = None,p_sListadoPermiso = None, p_sPermisoIdiaiv1 = None):
        sMsg = ""
        # sMsg +="Proceso automatico de insertado de permisos .\n"

        sMsg1 = ""
        sMsg2 = ""
        sMsg3 = ""

        # Inicializar/declarar variables
        oCAute = CAutenticacion()
        sPermisosAfter = ""        
        dInfoPermisosUbicados = dict()
        lPermisoUsuario = []
        dUsuariosxSistema =[]

        # print(type(p_sSistema))
        # print("Tamaño del texto: ")
        # print(getsizeof(p_sSistema))

        if p_sSistema != None and p_sSistema!="":                

            if p_Usuario == None and p_sListadoPermiso == None:                                            
                #Consulta los usuarios activos de IDIAIV1 para el sistema X
                sMsg = "Se migran TODOS los permisos de TODOS los usuarios del sistema "+p_sSistema+" de IDIAI v1 al IDIAI v2 <br>"
                oExecSP = CEjecutarSP()
                oExecSP.registrarParametros("nombreSistema",p_sSistema)
                dUsuariosActivos = oExecSP.ejecutarSP('obtenerUsuariosActivos')

                if len(dUsuariosActivos)>0:
                
                    print("Total de usuarios activos:" +str(len(dUsuariosActivos)))
                    # print(dUsuariosActivos[0][6])

                    # obtener el listado completo de los permisos originales del sistema desde IDIAI v1
                    sPermisosAfter = dUsuariosActivos[0][6]
                    dInfoPermisosUbicados = self.obtenerPermisosAfter(p_sSistema, sPermisosAfter)

                    # Relación de permisos originales del sistema desde IDIAI v1 y el ID del permiso del IDIAI v2
                    # print(dInfoPermisosUbicados)

                    # lPermiso = p_sListPermisos.split(",")
                    # sMsg1 +="Listado de usuarios que no se encuentran en IDIAIV2:\n"
                    
                    for dUsuario in dUsuariosActivos:
                        # print(dUsuario[2])

                        dActivoidIai2 = oCAute.consultarUsuarioActivo(dUsuario[2])

                        if len(dActivoidIai2)==0:
                            # print("El usuario si existe en IDIAI v2.")
                            print("El usuario "+dUsuario[2]+" no existe en IDIAI V2")
                            sMsg1 += "El usuario "+dUsuario[2]+" no existe en IDIAI V2 <br>"
                        
                        else:
                            # print("id de usuario: ")
                            # print(dActivoidIai2[0]["id"])
                            # print(self.idSistema)

                            if int(self.idSistema)>0 and int(dActivoidIai2[0]["id"])>0:
                                lPermisoUsuario = oCAute.obtenerPermisos(self.idSistema,dActivoidIai2[0]["id"])

                                print("Lista de permisos del usuario: ")
                                print(lPermisoUsuario)

                                if len(lPermisoUsuario)==0:
                                    pass
                                    
                                    sPermisoMayusulas = sPermisosAfter.upper()
                                    # print(sPermisoMayusulas)

                                    lPermisoMayus = sPermisoMayusulas.split(",")

                                    # print("Los permisos del IDIAI V1 del usuario: ")
                                    # print(dInfoPermisosUbicados)
                                    # print(dUsuario[3])
                                    # print("El id del usuario es: ")
                                    # print(dActivoidIai2[0]["id"])
                                    # print(self.listaPermisosv1)

                                    nInsert = self.insertarPermiso(dActivoidIai2[0]["id"], self.listaPermisosv1, dUsuario[3],dInfoPermisosUbicados)

                                    if nInsert == 1:
                                        print("Permisos insertados para el usuario: "+dUsuario[2])
                                    else:
                                        print("No se insertaron Permisos para el usuario: "+dUsuario[2])
                                        sMsg3 += "No se insertaron permisos en IDIAI v2 para el usuario: "+dUsuario[2]+"<br> "
                                        

                                    #TODO: Buscar mediante lista.index("nombrePermiso") obtener la posicion del permiso y ver si en la lista de permisos del usuario ese permiso es 1.                                
                                    # print("El usuario "+dUsuario[2]+" no tiene permisos asignados en el IDIAI v2 para el sistema "+p_sSistema)git
                                else:
                                    sMsg2 += "El usuario "+dUsuario[2]+" tiene permisos asignados en el IDIAI v2 para el sistema "+p_sSistema+"<br>"
                                    print("El usuario "+dUsuario[2]+" tiene permisos asignados en el IDIAI v2 para el sistema "+p_sSistema)
            else:
                print("El parametro usuario recibe: "+p_Usuario)
                print("El parametro listado de permisos o permiso recibe: "+p_sListadoPermiso)

                if p_Usuario == 'Allkn': #todos los usuarios conocidos es decir que ya cuenten con acceso al sistema señalado en p_sSistema
                    #Si el parametro p_Usuario es Allkn entonces solo buscara los usuarios  que ya tengan asignados permisos al sistema p_sSistema

                    #obtenemos Id de lo usuarios:
                    oExecSP = CEjecutarSP()
                    oExecSP.registrarParametros("sistema",p_sSistema)                                  
                    dUsuariosxSistema = oExecSP.ejecutarSP('obtenerRelacionUsuarioSistemaIdiaiv2')

                    if len(dUsuariosxSistema)>0:
                        print("Se encontrarón "+str(len(dUsuariosxSistema))+" registrados con permisos del sistema "+p_sSistema)
                        print("Por lo tanto a estos usuarios se les asignara el permiso: "+p_sListadoPermiso+" (solo si aun no lo tienen asignado).")

                        #Verificamos si los permisos obtenidos por argumetos pertenecen al sistema ingresado; DEVUELVE UNA RELACIÓN DE NOMBRE PERMISO : ID PERMISO
                        dInfoPermisosUbicados = self.obtenerPermisosAfter(p_sSistema, p_sListadoPermiso)

                        print(dInfoPermisosUbicados)
                        sMsg1 = self.insertarPermisosEspecificos(dUsuariosxSistema, dInfoPermisosUbicados,'Allkn')

                        # lPermisoUsuario = oCAute.obtenerPermisos(self.idSistema,idUsuario)
                    
                elif p_Usuario == 'PE' and p_sPermisoIdiaiv1 != None and p_sListadoPermiso!=None:
                    #Se insertara un permiso especifico existente en IDIAIv1, cuyo nombre de permiso puede ser diferente o igual

                    usuariosConPermiso = []
                    permisosIdIaiV1 = []
                    permisoIdIaiv2 = []
                    dActivoidIai2 = []

                    sMsg = "Obtenemos todos los usuarios activos de "+p_sSistema+" de IDIAI v1 <br>"
                    oExecSP = CEjecutarSP()
                    oExecSP.registrarParametros("nombreSistema",p_sSistema)
                    dUsuariosActivos = oExecSP.ejecutarSP('obtenerUsuariosActivos')

                    permisoIdIaiv2 = self.obtenerPermisosAfter(p_sSistema, p_sListadoPermiso)

                    print(permisoIdIaiv2)

                    if len(dUsuariosActivos)>0:
                        
                        print("Total de usuarios activos:" +str(len(dUsuariosActivos)))
                        print("El permiso en IDIAI v1 se llama "+p_sPermisoIdiaiv1)
                        print("El permiso en IDIAI v2 se llama "+p_sListadoPermiso)
                        print("Aqui termina... :0 ")

                        sPermisosAfter = dUsuariosActivos[0][6]
                        print(sPermisosAfter)

                        lPermiso = sPermisosAfter.split(",")
                        nPos = lPermiso.index(p_sPermisoIdiaiv1)

                        print("Posicion del permiso "+p_sPermisoIdiaiv1+" la cual es: "+str(nPos))
                        dUsuariosActivos[0]
                        nCont = 0
                        for item in dUsuariosActivos:
                            # print(item[3])
                            
                            permisosIdIaiV1 = item[3].split(",")

                            # print(permisosIdIaiV1[nPos])

                            if(permisosIdIaiV1[nPos] == "1"):
                                print("El usuario "+item[2]+" tiene el permiso "+p_sPermisoIdiaiv1+" en ID IAI v1")
                                dActivoidIai2 = oCAute.consultarUsuarioActivo(item[2])

                                print (dActivoidIai2[0]["id"])
                                usuariosConPermiso.append(dActivoidIai2[0]["id"])
                    
                    print(usuariosConPermiso)

                    self.insertarPermisosEspecificos(usuariosConPermiso, permisoIdIaiv2,'PE')
                    

                            
                            
                            
                        




                        





                

            sAsunto = "Resultado final de proceso migrarPermisos"
            sTitulo = "Insertado automático de permisos."
            contenido = sMsg1+" <br><br> "+sMsg2+" <br> "+sMsg3
            sSubtitulo = sMsg+"<br>"

            oCItkg = CInactivaTkg()
            oCItkg.enviarCorreo(sAsunto,sTitulo,contenido,sSubtitulo)






                                
                        
    def obtenerPermisosAfter(self,p_sNombreSistema ,p_sListPermisos):
            sTexto= ""
            sPermisosNoEncontrados = ""
            # dDatosPerm = []
            dInfoPermisosUbicados = dict()
            posicion = 0
            print("> Inicio al proceso de relación de permisos de IDIAI v1 vs IDIAIV2.")
            try:
                if p_sListPermisos !=None and p_sListPermisos.strip() != "" and p_sNombreSistema!=None and p_sNombreSistema!= "":
                    if p_sListPermisos == 'todos':
                        oExecSP = CEjecutarSP()
                        oExecSP.registrarParametros("nombreSistema",p_sNombreSistema)
                        oExecSP.registrarParametros("TODOS",1)
                        dDatosPerm = oExecSP.ejecutarSP('consultarPermisosIdiai2')

                        if len(dDatosPerm)>0:
                            #TODO urgente concluir esta validación para la obtención general de permisos para Alluk
                            self.idSistema = dDatosPerm['sistema_id'][3]

                            for item in dDatosPerm:
                                lPermiso.append(item[5])

                                print(lPermiso)


                    else:                        
                        lPermiso = p_sListPermisos.split(",")
                        
                        self.listaPermisosv1 = lPermiso
                    
                        for item in lPermiso:
                            # print(item)
                            p_sNombreSistema = p_sNombreSistema.upper().strip()
                            item = item.upper().strip()

                            oExecSP = CEjecutarSP()
                            oExecSP.registrarParametros("nombreSistema",p_sNombreSistema)
                            oExecSP.registrarParametros("nombrePermiso",item)
                            dDatosPerm = oExecSP.ejecutarSP('consultarPermisosIdiai2')

                            if len(dDatosPerm)==0:
                                sPermisosNoEncontrados += item+", "
                                dInfoPermisosUbicados.update({item:0})
                            else:
                                # print(type(dDatosPerm))

                                for dato in dDatosPerm:
                                    # print(dato[2])
                                    self.idSistema = dato[3]
                                    dInfoPermisosUbicados.update({item:dato[2]})
                            

                            posicion = posicion+1
                                
                    
                if sPermisosNoEncontrados!= "":
                    print("No se encontraron los siguientes permisos: "+ sPermisosNoEncontrados)
                else:
                    print("Relación de Permisos : OK ")


                # print(dInfoPermisosUbicados)

            except ValueError as error:
                sTexto = "Error en el metodo obtenerPermisosAfter: %s" % error
                print(sTexto)
            
            print("> Concluye proceso de relación de permisos de IDIAI v1 vs IDIAIV2.")
            
            return dInfoPermisosUbicados

        # print("Hola :)")


    def insertarPermiso(self, idUsuario ,listadoPermisov1 = None, permisosUsuariov1 = None, lPermisosCorrelacion = None):
        
        sTexto = ""
        nNumitera=0
        sPerm = ""
        idPerm = 0
        oExecSP = False
        dDatosPerm = False
        nInsert = 0
        oCAute = CAutenticacion()
        lPermisoUsuario = []

       
        print("Inicio al método para insertar permiso(s) a usuario.")
   
        
        try:
            pass
            
            if listadoPermisov1 != None and permisosUsuariov1 != None and lPermisosCorrelacion != None:
                # print("Listado de permisos de IDIAI V1: ")
                # print(listadoPermisov1)

                # print("Listado de permisos de IDIAI V1 asignados al usuario: ")
                # print(permisosUsuariov1)

                # print("Listado de Permisos Correlacionados ")
                # print(lPermisosCorrelacion)

                lPermiso = permisosUsuariov1.split(",")

                for item in lPermiso:
                    # print(item)

                    if int(item) == 1:
                        
                        sPerm = listadoPermisov1[nNumitera].upper().strip()
                        idPerm = lPermisosCorrelacion[sPerm]
                        print('El usuario con id '+str(idUsuario)+' Tiene asignado el permiso: '+sPerm+' - '+str(idPerm))

                        if idPerm != 0:
                            pass
                            oExecSP = CEjecutarSP()
                            oExecSP.registrarParametros("idUsuario",idUsuario)
                            oExecSP.registrarParametros("idPermiso",idPerm)
                            dDatosPerm = oExecSP.ejecutarSP('InsertarPermisoUsuario')
                        else:
                            print('El permiso: '+sPerm+' no esta registrado en IDIAV2, por favor de revisar.')
                            
                            # time.sleep(3)

                    nNumitera = nNumitera+1

                lPermisoUsuario = oCAute.obtenerPermisos(self.idSistema,idUsuario)

                if len(lPermisoUsuario)>0:
                    nInsert = 1
                    print("El usuario ya cuenta con permisos al sistema .")
                else:
                    print("El usuario aun no cuenta con permisos al sistema .")            

                    

                # for item in permisosUsuariov1:
                    # print(item.upper().strip())
                    # print(item)


            else:
                print("Al parecer olvidaste pasar algun parametro, por favor verifica que estes pasando todos los datos solicitados para este metodo.")


        except ValueError as error:
            sTexto = "Error en el metodo obtenerPermisosAfter: %s" % error
            print(sTexto)

        print("Concluye el método para insertar permiso(s) a usuario.")

        return nInsert
    

    def insertarPermisosEspecificos(self,idUsuario,lPermisosCorrelacion, tipoOperacion = None):
        print("==>METODO insertarPermisosEspecificos ")
        sTexto = ""
        lPermisoUsuario = []
        oCAute = CAutenticacion()
        sPermiso =""
        idPerm = 0
        dPermUsuario = []
        dPermUsuario1 = []
        nInsert = 0
        nUidUser = 0
        bValido = False

        try:
            # lPermisoUsuario = oCAute.obtenerPermisos(self.idSistema,idUsuario)

            # self.listaPermisosv1 = listado de los nombres de los permisos que se desean asignar al o los usuarios.
            for item in self.listaPermisosv1:
                print(item) 
                sPermiso = item.upper().strip() #nombre del permiso en mayusculas...
                print("Nombre del permiso ===> ")
                print(sPermiso)
                print(lPermisosCorrelacion[sPermiso]) #ubica el permiso en el diccionario, ya que las claves son los nombres de los permisos, devuelve el id del permiso.
                idPerm = lPermisosCorrelacion[sPermiso]

                if tipoOperacion == 'Allkn':

                    for nIdUser in idUsuario:
                        print("1.-"+tipoOperacion)
                        # print(nIdUser)
                        # print(nIdUser[0])
                        nUidUser = nIdUser[0]

                        oExecSP = CEjecutarSP()
                        oExecSP.registrarParametros("idUsuario",nUidUser)
                        oExecSP.registrarParametros("idPermiso",idPerm)
                        oExecSP.registrarParametros("idSistema",self.idSistema)
                        dPermUsuario = oExecSP.ejecutarSP('consultarPermisoEspecificoUsuario')
                                  
                        print(dPermUsuario)
                            
                        if len(dPermUsuario)==0:
                                        print("El usuario "+str(nUidUser)+" no tiene asignado el permiso "+sPermiso+", se intentara insertar.")
                                        oExecSP = CEjecutarSP()
                                        oExecSP.registrarParametros("idUsuario",nUidUser)
                                        oExecSP.registrarParametros("idPermiso",idPerm)
                                        dDatosPerm = oExecSP.ejecutarSP('InsertarPermisoUsuario')

                                        oExecSP = CEjecutarSP()
                                        oExecSP.registrarParametros("idUsuario",nUidUser)
                                        oExecSP.registrarParametros("idPermiso",idPerm)
                                        oExecSP.registrarParametros("idSistema",self.idSistema)
                                        dPermUsuario1 = oExecSP.ejecutarSP('consultarPermisoEspecificoUsuario')

                                        if len(dPermUsuario1)>0:
                                            nInsert = 1
                                            print("El permisos "+str(idPerm)+" se asigno al id usuario "+str(nUidUser))
                                            sTexto += "Se asigno al usuario "+str(nUidUser)+" el permiso "+sPermiso+" <br>"
                                        
                        else:
                                        print("El usuario "+str(nUidUser)+" ya tiene asignado el permiso "+sPermiso)
                                        print("El permiso "+str(idPerm)+" ya esta asignado al id usuario "+str(nUidUser))

                                        sTexto += "El usuario "+str(nUidUser)+" ya tiene asignado el permiso "+sPermiso+" <br>"                        



                        

                elif tipoOperacion == 'PE':
                        print("2.- "+tipoOperacion)
                        for nIdUser in idUsuario:
                           
                            nUidUser = nIdUser
                            print(nUidUser)
                        # if bValido:
                                
                            oExecSP = CEjecutarSP()
                            oExecSP.registrarParametros("idUsuario",nUidUser)
                            oExecSP.registrarParametros("idPermiso",idPerm)
                            oExecSP.registrarParametros("idSistema",self.idSistema)
                            dPermUsuario = oExecSP.ejecutarSP('consultarPermisoEspecificoUsuario')
                                    
                            print(dPermUsuario)
                            
                            if len(dPermUsuario)==0:
                                        print("El usuario "+str(nUidUser)+" no tiene asignado el permiso "+sPermiso+", se intentara insertar.")
                                        oExecSP = CEjecutarSP()
                                        oExecSP.registrarParametros("idUsuario",nUidUser)
                                        oExecSP.registrarParametros("idPermiso",idPerm)
                                        dDatosPerm = oExecSP.ejecutarSP('InsertarPermisoUsuario')

                                        oExecSP = CEjecutarSP()
                                        oExecSP.registrarParametros("idUsuario",nUidUser)
                                        oExecSP.registrarParametros("idPermiso",idPerm)
                                        oExecSP.registrarParametros("idSistema",self.idSistema)
                                        dPermUsuario1 = oExecSP.ejecutarSP('consultarPermisoEspecificoUsuario')

                                        if len(dPermUsuario1)>0:
                                            nInsert = 1
                                            print("El permisos "+str(idPerm)+" se asigno al id usuario "+str(nUidUser))
                                            sTexto += "Se asigno al usuario "+str(nUidUser)+" el permiso "+sPermiso+" <br>"
                                        
                            else:
                                        print("El usuario "+str(nUidUser)+" ya tiene asignado el permiso "+sPermiso)
                                        print("El permiso "+str(idPerm)+" ya esta asignado al id usuario "+str(nUidUser))

                                        sTexto += "El usuario "+str(nUidUser)+" ya tiene asignado el permiso "+sPermiso+" <br>"

                        

            sTexto+="Total de registros insertados: "+str(len(idUsuario))+"<br>"
        except ValueError as error:
            sTexto = "Error en el metodo insertarPermisosEspecificos: %s" % error
            print(sTexto)  


        return sTexto   
    

class CRelacionPermisos():

    def listarPermisos(self,p_sSistema = None):
        
        sPermisosAfter = ""
        lPermiso = []

        if p_sSistema != None and p_sSistema!="":
            oExecSP = CEjecutarSP()
            oExecSP.registrarParametros("nombreSistema",p_sSistema)
            dUsuariosActivos = oExecSP.ejecutarSP('obtenerUsuariosActivos')
            print("El sistema a consultar es: "+p_sSistema)
            
            sTexto = ""


            if len(dUsuariosActivos)>0:
                # print("Total de usuarios activos:" +str(len(dUsuariosActivos)))
                # print("Valor de registros devueltos: " +str(len(dUsuariosActivos)))
                

                    # obtener el listado completo de los permisos originales del sistema desde IDIAI v1
                sPermisosAfter = dUsuariosActivos[0][6]
                # print(sPermisosAfter)

                if(sPermisosAfter != ""):
                    self.lPermiso = sPermisosAfter.split(",")

                    # print("Total de permisos: "+str(len(self.lPermiso)))
                    
                    for item in dUsuariosActivos:
                        # print(item[2])

                        sTexto += "|"+item[2]

                        lista1 = item[3].split(",")

                        sTexto += self.convertirPermiso(lista1)+"\n"

                    print(sTexto)


    def convertirPermiso(self, permisosAsignados= None):
            # print("Accede a convertirPermiso")
            # print("Total de permisos: "+str(len(self.lPermiso)))
            # print("Permisos asignados:"+str(len(permisosAsignados)))
            
            sTexto = ""
            nPos = 0

            # print(self.lPermiso[0])

            for item in permisosAsignados:
                # print(item)

                if item == "1":
                    # print(self.lPermiso[nPos])
                    sTexto += "|"+self.lPermiso[nPos]
                else:
                    pass

                nPos = nPos +1

            
            return sTexto

#ARSI 17/03/2025 CREAR CLASE QUE HAGA LA CONSULTA DE PERMISOS DE UN USUARIO Y VALIDE EL TOKEN
# obtenerPermisos, obtenerGrupos y crear otro metodo que valide el token y que devuelva los permisos del usuario. (CValidaToken)            
class CVerificarTokenPermiso(APIView):

    oExecSP = CEjecutarSP()
    oVeficarTk = CVerificaToken()
    oAuth = CAutenticacion()

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)    

    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token asignado por la aplicación.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'idSistema' :  openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema.'),
                'permisoGrupo' : openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del permiso o grupo a validar.'),
                'tipoPerGp' : openapi.Schema(type=openapi.TYPE_STRING, description='Por favor de especificar que valor es el indicado en "permisoGrupo", si es un Grupo colocar G, si es un Permiso colocar P.'),
                'saveTk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Valor que determina si basar la verificación del token en el que este almacenado y activo en la BD, opcional'),
            },
            required=['token', 'user','idSistema','permisoGrupo','tipoPerGp']
        ),
        responses={200: 'Token Validado', 400:'JSON INVALIDO' , 404:'Datos invalidos',401: 'Sin autorización,El servidor ha recibido la solicitud, pero no se ha podido autenticar al usuario.', 403:'Prohibido, El servidor entiende la solicitud, pero el usuario no tiene permiso para acceder al recurso, aunque sí está autenticado'},
    )   

    def post(self,request):
        """
        Realiza la validación del token dado por la api de autenticación y la validación del permisos al usuario.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        #ARSI 22/03/2025 SE AGREGA PARAMETRO OPCIONAL SAVE TOKEN PARA VALIDAR EL TOKEN ALMACENADO EN LA BASE DE DATOS.
        try:
            print("CVerificarTokenPermiso - Accede a la validación de token y permisos.")
            bValido = True
            sToken_encoded = ""
            sUserName = ""
            nSistemaOrigen = 0
            sPermGp = ""
            tk = ""
            is_token_valid = False
            is_token_expired = True
            sTexto = ""
            nLenDef = 0
            nItemJson = 0
            nStatus = 0

            #22/03/2025 ARSI SE AGREGA PARAMETRO OPCIONAL SAVE TOKEN
            dCamposJson = ['token', 'user','idSistema','permisoGrupo','tipoPerGp','saveTk']
            
            jd = json.loads(request.body)

            nLenDef = len(dCamposJson) 

            nItemJson = len(jd)
            dDatos = []
            dUsuario = []
            bStkValid = False #ARSI 22/03/2025
            dDatosValidarTkBD = [] #ARSI 22/03/2025
            bValidoTk = False #ARSI 23/03/2025
            #datos = []

            if nItemJson != nLenDef:
                sTexto += "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False

            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    #ARSI 22/03/2025 
                    if item == 'saveTk':
                        print("CVerificaTokenPermiso - El campo saveTk no se encuentra en el JSON, se asigna valor de 0.")
                        jd['saveTk'] = 0
                        continue
                    else:
                        sTexto += " El campo faltante es: "+item+". "
                        bValido = False
                        break


            # if (jd['token'].isspace() or len(jd['token']) <= 1):
            #     sTexto += "El item token es muy corto o viene vacio. "
            #     nStatus = 400
            #     bValido = False

            if (jd['user'].isspace() or len(jd['user']) <= 1):
                sTexto += "El item de usuario es muy corto o viene vacio. "
                nStatus = 400
                bValido = False

            if (jd['token'].isspace() or len(jd['token']) <= 1):
                sTexto += "El item token es muy corto o viene vacio. "
                nStatus = 400
                bValido = False

            if (jd['idSistema']== 0 or jd['idSistema']== ""):
                sTexto += "El item de sistema es muy corto o viene vacio. "
                nStatus = 400
                bValido = False

            if (jd['permisoGrupo'].isspace() or len(jd['permisoGrupo']) < 0):
                sTexto += "El item de permisoGrupo es muy corto o viene vacio. "
                nStatus = 400
                bValido = False

            if (jd['tipoPerGp'].isspace() or len(jd['tipoPerGp']) > 1):
                sTexto += "El item de tipoPerGp es muy largo o contiene espacios en blanco. "
                nStatus = 400
                bValido = False

            if (jd['tipoPerGp'] != "G" and jd['tipoPerGp'] != "P"):
                sTexto += "El item de tipoPerGp debe tener los valores G o P. "
                nStatus = 400
                bValido = False

            #ARSI 22/03/2025 SE VALIDA EL VALOR DE SAVETK
            if isinstance(jd['saveTk'],int):
                if ((jd['saveTk'] !=0 and jd['saveTk'] !=1)):
                    sTexto += "El item de saveTk debe contener el valor entero 0 o 1. "
                    nStatus = 404
                    bValido = False

                if (jd['saveTk'] ==1):
                    bStkValid = True

            elif isinstance(jd['saveTk'],str):
                if (jd['saveTk']== "" or jd['saveTk'].isspace() or jd['saveTk'] !="0" or jd['saveTk'] !="1"):
                    sTexto += "El item de saveTk debe contener el valor entero 0 o 1; no caracteres alfanumericos. "
                    nStatus = 404
                    bValido = False

            

            if bValido:
                print("CVerificarTokenPermiso - Verificar token ...")
                
                sToken_encoded = jd['token']
                sUserName = jd['user']
                nSistemaOrigen = jd['idSistema']
                sPermGp  = jd['permisoGrupo']
                sTipo = jd['tipoPerGp']
                idPersonal = 0
                oAuth = CAutenticacion()
               

                dDatos = self.oVeficarTk.validarToken(sUserName,sToken_encoded)

                #ARSI 22/03/2025 SE VALIDA QUE EL PARAMETRO SAVETOKEN SEA 1 PARA VALIDAR EL TOKEN EN LA BASE DE DATOS
                if bStkValid:
                    dDatosValidarTkBD = self.oVeficarTk.validarTokenBD(sUserName,sToken_encoded,nSistemaOrigen)
                    #ARSI 23/03/2025 SE AGREGA VALIDACIONES DE TK EN BD y el token dado por el cliente.
                    if dDatosValidarTkBD['valido'] == 1 and dDatos['valido'] == 1:
                        bValidoTk = True
                    else:
                        #ARSI 23/03/2025 SI LOS TOKENS NO SON VALIDOS ELIMINA EL TOKEN DE LA bd.
                        self.oAuth.inactivarTokens(sUserName,nSistemaOrigen);
                elif dDatos['valido'] == 1:
                    bValidoTk = True

                #ARSI 23/03/2025 AHORA SE VALIDA EL BOOLEANO DE TOKEN.
                #if dDatos['valido'] == 1:
                if bValidoTk:
                    
                    print("CVerificarTokenPermiso - El token es valido.")
                    
                    dUsuario = self.oAuth.consultarUsuarioActivo(sUserName)

                    if len(dUsuario):                                        
                        idUsuario = dUsuario[0]['id']
                        print("CVerificarTokenPermiso - Usuario validado, el id del usuario es: "+str(idUsuario))

                        #ARSI 06/06/2025 OBTENER ID PERSONAL DEL USUARIO CUANDO SE VERIFIQUE SUS PERMISOS.
                        dDatosPersonales = self.oAuth.obtenerDatosPersonales(idUsuario,0) 

                        if len(dDatosPersonales)>0:                                        
                            idPersonal = dDatosPersonales[0][1]

                        # lPermisoUsuario = self.oAuth.obtenerPermisos(nSistemaOrigen,idUsuario)
                        # lGrupoUsuario = self.oAuth.obtenerGrupos(nSistemaOrigen,idUsuario)

                        if(sTipo == "P"):                           
                            print("CVerificarTokenPermiso -  se valida el permiso: "+sPermGp)
                            lPermisoUsuario = self.oAuth.obtenerPermisos(nSistemaOrigen,idUsuario)
                            lGrupoUsuario = self.oAuth.obtenerGrupos(nSistemaOrigen,idUsuario)
                            

                            #if len(lPermisoUsuario)>0 & len(lGrupoUsuario)>0:
                            lPermisoUsuario.update(lGrupoUsuario)

                            print("CVerificarTokenPermiso -  se obtiene listado de permisos: ")
                            print(lPermisoUsuario)

                            if sPermGp in lPermisoUsuario:
                                print("CVerificarTokenPermiso - El usuario "+sUserName+" tiene el permiso: "+sPermGp);
                                
                                nStatus = 200
                                datos = {'status': 'Success', "message":'El token es válido y no ha expirado.', "idPersonal":idPersonal}
                            else:
                                nStatus = 200
                                datos = {'status': 'NOAUTORIZADO', "message":'El token es válido, pero el usuario no cuenta con el permiso solicitado.'}
                        elif(sTipo == "G"):
                            print("CVerificarTokenPermiso -  se valida el grupo: "+sPermGp)
                            
                            self.oAuth.obtenerGrupos(nSistemaOrigen,idUsuario)

                            lGrupoUsuario = self.oAuth.dGruposAsigUsuario

                            print("CVerificarTokenPermiso -  se obtiene listado de grupos: ")
                            print(lGrupoUsuario)

                            if sPermGp in lGrupoUsuario:
                                print("CVerificarTokenPermiso - El usuario "+sUserName+" esta asignado al grupo "+sPermGp);
                                nStatus = 200
                                datos = {'status': 'Success', "message":'El token es válido y no ha expirado.', "idPersonal":idPersonal}
                            else:
                                nStatus = 200
                                datos = {'status': 'NOAUTORIZADO', "message":'El token es válido, pero el usuario no esta asignado al grupo solicitado.'}
                        else:
                            nStatus = 400
                            datos = {'status': 'Error', "message":'El tipo de permiso o grupo no es valido.'}
                                                                  
                    else:
                        nStatus = 401
                        datos = {'status': 'Error', "message":'El usuario no existe.'}
                    # is_token_valid = True
                    # is_token_expired = False
                else:
                    nStatus = 401
                    datos = {'status': 'Error', "message":'El token es invalido'}

            else:
                #nStatus = 403
                datos = {"status": 'Error', "message": sTexto}
                
                
            
        except ValueError as error:
            nStatus = 404
            sTexto += "%s" % error
            datos = {'status': 'Error', "message": sTexto}
            # return False
        except KeyError as error:
            nStatus = 403
            sTexto += "%s" % error
            datos = {'status': 'Error', "message": sTexto}


        print(datos)
        print(nStatus)
        # return JsonResponse(datos)
    
        return JsonResponse(datos,status=nStatus)
    

class CInactivaTk(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),                
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema de donde viene el token; colocar NA en caso de que no aplique.')
            },
            required=['token', 'user','idSistema']
        ),
        #responses={200: 'Token Validado', 403: 'Json invalido o problemas internos en el server.', 404:'Datos invalidos'},
        responses={200: 'Token Validado', 400:'JSON INVALIDO' , 404:'Datos invalidos',401: 'Sin autorización,El servidor ha recibido la solicitud, pero no se ha podido autenticar al usuario.', 403:'Prohibido, El servidor entiende la solicitud, pero el usuario no tiene permiso para acceder al recurso, aunque sí está autenticado'},
    ) 
    
    def post(self,request):
        """
         Realiza la inactivación del token en la BD

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """           
        try:
            #pass
            #Se requiere username y idSistema para inactivar el token en la BD.
            print("CInactivaTk - Inactiva el token de la base de datos.")

            bValido = True
            sToken_encoded = ""
            sUserName = ""
            nSistemaOrigen = 0
            sPermGp = ""
            tk = ""
            is_token_valid = False
            is_token_expired = True
            sTexto = ""
            nLenDef = 0
            nItemJson = 0
            nStatus = 0
            nTotAfectadas = 0

            #27/03/2025 ARSI SE valida parametros de entrada.
            dCamposJson = ['user','idSistema']

            jd = json.loads(request.body)

            nLenDef = len(dCamposJson)
            

            if (jd['user'].isspace() or len(jd['user']) <= 1):
                sTexto += "El item de usuario es muy corto o viene vacio. "
                nStatus = 400
                bValido = False

            if isinstance(jd['idSistema'],int):                       
                if (jd['idSistema']<=0):
                    sTexto += "El item de idSistema debe contener algún id de sistema valido."
                    nStatus = 404
                    bValido = False
                   
            if isinstance(jd['idSistema'],str):
                    
                    sTexto += "El item de idSistema debe contener algún valor numerico que indique el Id del sistema valido. "
                    nStatus = 404
                    bValido = False
                    
                    if (jd['user'].isspace() or len(jd['user']) <= 1):
                        sTexto += "El item de usuario es muy corto o viene vacio. "     

            for item in dCamposJson:
                if item in jd:
                    continue
                else:                  
                    sTexto += " El campo faltante es: "+item+". "
                    bValido = False
                    break                                                 
                        
            nItemJson = len(jd)
                        
            if nItemJson != nLenDef:
                sTexto += "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False

            if bValido:
                sUserName = jd['user']
                idSistema = jd['idSistema']
                oAuth = CAutenticacion()

                
                print("CAutenticacion - registrarAccesos - Datos validos, se procede a inactivar token de la Base de datos.")

                nTotAfectadas = oAuth.inactivarTokens(sUserName,idSistema)

                if nTotAfectadas>0:
                    print("CAutenticacion - registrarAccesos - Se inactivaron "+str(nTotAfectadas)+" tokens")
                    nStatus = 200
                    datos = {'status': 'Success', "message":'El token ha sido inhabilitado'}
                else:
                    print("CAutenticacion - registrarAccesos - No se inactivaron tokens")
                    nStatus = 200
                    datos = {'status': 'Success', "message":'No se inactivaron tokens'}


            else:
               datos = {'status': 'Error', "message": sTexto}  
                
        except ValueError as error:
            nStatus = 404
            sTexto += "%s" % error
            datos = {'status': 'Error', "message": sTexto}
            # return False
        except KeyError as error:
            nStatus = 403
            sTexto += "%s" % error
            datos = {'status': 'Error', "message": sTexto}

        print(datos)
        print(nStatus)
        
        return JsonResponse(datos,status=nStatus)

        