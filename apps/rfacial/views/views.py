# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password

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




import json
import os
import base64

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

    # @staticmethod
    def obtenerPermisos(self, p_nIdSistema, p_nIdUsuario):
        dPermisos = {}
        dPermisosUsuario = {}
        print("Accede a metodo obtenerPermisos.")
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
            print(timezone.now())
            # Calcular la fecha de expiración del token
            expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
            # expiration_time = timestamp + (expiration_hours * 60)  # 60 segundos en un minuto, solo para terminos de prueba ...
            # print(expiration_time)
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
        print(sTextFinal)

    
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

    def consultarExisteUsuario(self, nameUser):
        print("Accede a metodo  consultarExisteUsuario:")
        print(nameUser)
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
        print("Accede a metodo  consultarUsuarioActivo:")
        print(nameUser)
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
    


    def registrarAcceso(self, username, idSistema, observaciones, opc, bConsultaBloqueo = False):
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

                        print(intFechaCad)
                        print(timestamp)

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


            if bValido and not bConsultaBloqueo:                       
                if bExisteRegAccess:
                    print("Si existe registro de historial de acceso en los sistemas para el usuario : "+username)

                    if opc == 1:
                        print("caso exitoso, el usuario se loggeo sin problemas : "+username)
                        message = "Success"
                        sTexto = "Caso exitoso, el usuario se loggeo sin problemas : "+username
                        actualizaReg = intentos.objects.filter(id=idReg).update(activo=0,updated_at=timezone.now())

                        
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

                                

                                actualizaReg = intentos.objects.filter(id=idReg).update(activo=1,updated_at=timezone.now(),fechaCadReg=fecha_modificada,numintentos=NumIntentos)

                            
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
                        print("caso exitoso, el usuario se loggeo sin problemas : "+username)

                        regAcceso = intentos(
                            username= username,
                            numintentos = 0,
                            idSistema = idSistema,
                            activo = 0,
                            observaciones = observaciones
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
            datos = {}
            info = {}
            
            #Declaración y asignación de variables
            bValido = True
            
            bKey = False
            bKeyTkG = False
            bKeyRF = False
            
            dCamposJson = ['token', 'user', 'password','idSistema', 'timeExp']
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

            #Valida que el numero de claves del JSON enviado a la API
            #coincida con el numero de claves declaras en el diccioario dCamposJson
            nItemJson = len(jd)
            
            if nItemJson != nLenDef:
                sTexto = "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False



            #Validación de las claves json, si alguna clave no se encuentra en el objeto, entonces
            #el valor de bValido es Falso y regresa un mensaje de error indicando el identificador
            #  faltante.
            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    sTexto += "El campo faltante es: "+item+". "
                    bValido = False
                    break
            
            #si las claves estan correctas, continuara realizando el resto del proceso
            # de autenticación
            if bValido:
                print("1 ) Tamaño y nombre de claves de JSON obtenido, validos.")
                # IMPORTANTE!
                # Intranet tiene el id de sistema 3, Reconocimiento facial tiene el id de sistema 4.

                #2. Compara el token obtenido del json contra el secretKey de la aplicación.
                # 2.1. Para el sistema de RF (Reconocimiento Facial) el  token =4  - KEY_RF
                # keySis = base64.b64decode(jd['token'])
                # keySis = keySis.decode('utf-8')
                skTk = str(jd['token'])
                # keySis = self.decodificarB64(jd['token'])
                keySis = self.decodificarB64(skTk)
                print(keySis)

                # print(keySis)
                # print(os.environ.get('KEY_RF'))

                if keySis == str(os.environ.get('SECRET_KEY')):
                    bKey = True
                elif keySis == str(os.environ.get('KEY_RF')):
                    bKeyRF = True
                elif keySis == str(os.environ.get('KEY_GTKG')):
                    bKeyTkG = True
                elif keySis == str(os.environ.get('KEYVALIDADJG')):
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
                                        
                                        print("paso 2")

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
                                            info = self.registrarAcceso(jd['user'],sistema,sTexto+" Desde el sistema "+self.sNombreSistema,opc)
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
                                        print(dDatosPersonales[0][1])
                                        idPersonal = dDatosPersonales[0][1]
                                        sNombreCompleto = dDatosPersonales[0][9]
                                        idUsuario = dDatosPersonales[0][0]                               
                                        sUserName = dDatosPersonales[0][3]

                                        
                                        dUsuario = self.consultarUsuarioActivo(sUserName)

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
                                                    print("Se solicita generar TKG.")

                                                    #Se consulta que exista token global asignado al usuario
                                                    dUsTk = list(TokenGlobal.objects.filter(username=jd['user'], caduco=0).values())
                                                                
                                                    if len(dUsTk) == 0:
                                                        # insertar TKG en BD 05/03/2024
                                                        # sTimeExp = 0
                                                        if jd['timeExp'] == 0:
                                                            sTimeExp = 3
                                                        else:
                                                            sTimeExp = jd['timeExp']

                                                        gtkg = self.generarTKGlobal(jd['user'],sTimeExp,sistema)
                                                        insertTkG = TokenGlobal(username=jd['user'], token=gtkg,sistemaOrigen=sistema, caduco=0)
                                                        insertTkG.save()
                                                    else:
                                                        gtkg = dUsTk[0]['token']
                                                    
                                                                                            
                                                    
                                                    

                                                    
                                                    #Si el consumo de la Api tiene el key para generar Token Global
                                                    #paso 1) Se consulta en Base de datos si el usuario cuenta con TKG activo
                                                    #paso 2) En caso de que el usuario no cuente con TKG activo, entonces se inserta uno
                                                    #paso 3) En caso de que exista un TKG en base de datos, se verifica que este aun activo, si no lo esta, entonces borrar.
                                                    #paso 4) En caso de que exista un TKG en BD, y si aun esta activo, entonces permanecer con dicho TKG.
                                    
                                                    # is_token_valid = default_token_generator.check_token(jd['user'], tokenApi)
                                                
                                                opc = 1
                                                info = self.registrarAcceso(sUserName,sistema,"Inicio de sesión exitoso al sistema "+self.sNombreSistema,opc)
                                                nStatus = 200
                                                datos = {'message': 'Success','idPersonal':idPersonal,'usuario': sUserName, 'sistema':self.sNombreSistema,'nombreCompleto':sNombreCompleto,'token': tokenApi,'grupos':self.dGruposAsigUsuario,'permisos': dPermisos,'sistemas':sListSistemasPermitidos, 'tkg':gtkg}
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
            
        except ValueError as error:
            nStatus = 404
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}
            # return False
        

        if opc == 3:
           info = self.registrarAcceso(jd['user'],jd['idSistema'],sTexto,opc)
           print(info)
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
        

        print(datos)

        return JsonResponse(datos,status= nStatus)
    
    
    # def put(self,request):
    #     pass

    # def delete(self,request):
    #     pass


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
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.')
            },
            required=['token', 'user']
        ),
        responses={200: 'Token Validado', 500: 'Json invalido o problemas internos en el server.', 404:'Datos invalidos'},
    ) 
    def post(self,request):
        """
        Realiza la validación del token dado por la api de autenticación.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
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

            dCamposJson = ['token', 'user']
            
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


            if (jd['token'].isspace() or len(jd['token']) <= 1):
                sTexto += "El item token es muy corto o viene vacio. "
                nStatus = 404
                bValido = False

            if (jd['user'].isspace() or len(jd['user']) <= 1):
                sTexto += "El item de usuario es muy corto o viene vacio. "
                nStatus = 404
                bValido = False


            if bValido:
                print("Verificar token ...")
                sToken_encoded = jd['token']
                sUserName = jd['user']
                
                user = User.objects.get(username=sUserName) 
                
                # tk = urlsafe_base64_decode(sToken_encoded)                
                # tk = tk.decode('utf-8')
                # print("Entra a decrypt ...")
                tk = crfr.decrypt(sToken_encoded.encode()).decode()

                # print(tk)
                 # Separar el token y la marca de tiempo
                parts = tk.split(',')

                # print("Token ... :( por favor funciona: ")
                # print(parts[0])
                
                token_without_timestamp = '-'.join(parts[:-1])
                timestamp = int(parts[-1])
                # print("timestamp: ")
                # print(timestamp)

                # Calcular la fecha de expiración del token
                # expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
                expiration_time = timestamp  # 3600 segundos en una hora
                # expiration_time = timestamp + (1 * 60)  # 60 segundos prueba de 1 min.

                print(expiration_time)
                print(timezone.now().timestamp())

                if expiration_time > timezone.now().timestamp():
                    print("Aun no expira el token")
                    is_token_expired = False
                # else:
                #     print("El token ya expiro...")
                    # is_token_expired = True

                # is_token_valid = default_token_generator.check_token(user, tk)
                is_token_valid = default_token_generator.check_token(user, parts[0])
                

                if is_token_valid and not is_token_expired:
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
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}
            # return False
        except KeyError as error:
            nStatus = 500
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}

       
       

        return JsonResponse(datos,status=nStatus)  
    

    
    

class CVerificaTokenGlobal(APIView):

    tkgb = ""

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
        responses={200: 'Token Validado'},
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
            tkg = ""
            bValido = True
            dCamposJson = ['user']
            user = ""
            sUserName = ""
            nSistemaOrigen = 0
            ntam = 0
            nTamTot = 0
            ltam = []
            sSl = ""

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
                sUserName = jd['user']

                dUsTk = list(TokenGlobal.objects.filter(username=sUserName, caduco=0).values())

                if len(dUsTk)==1:
                                    
                    tkg = dUsTk[0]['token']
                    nSistemaOrigen = int(dUsTk[0]['sistemaOrigen'])
                    user = User.objects.get(username=sUserName) 

                    # print("Se obtiene el token.")

                    tkDpt = crfr.decrypt(tkg.encode()).decode()

                    # print(tkDpt)
                    
                    ltam = tkDpt.split(os.environ.get('USGL'))

                    ntam = int(ltam[1])

                    nTamTot = len(ltam[0]+os.environ.get('USGL'))

                    if ntam == nTamTot:
                        is_len = True

                        parts = tkDpt.split(',')

                        if len(parts)>0:
                            # print(parts[0])
                            
                            is_token_valid = default_token_generator.check_token(user,parts[0])
                            # if is_token_valid:
                            #     print("el token si es valido...")

                            timestamp = int(parts[1])
                            expiration_time = timestamp

                            # print(expiration_time)
                            # print( timezone.now().timestamp())

                            if expiration_time > timezone.now().timestamp():                    
                                is_token_expired = False #Si es false entonces el token aun no expira.
                            # else:
                            #     print("Expirto token...")

                            if nSistemaOrigen == int(parts[2]):
                                is_system_origin = True #Si es true entonces el sistema origien es el correcto.

                            sSl = parts[3]

                            if sSl[:3] == os.environ.get('SIGNAL'):
                                is_signal = True


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
                datos = {'message': 'JSON invalido.', 'Resultado': sTexto}


        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "Resultado": sTexto}

        
        print(datos)

        return JsonResponse(datos)
    
    
    

