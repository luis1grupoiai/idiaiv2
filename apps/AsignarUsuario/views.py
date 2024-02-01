from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import VallEmpleado 
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags



@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    
    
        
    empleados = []
    empleados = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    
   # print(empleados)
    context = {
        'empleados' : empleados,
        'active_page': 'solicitud',
        'nombre_usuario': nameUser(request),
        'categoria':'Aqui va la Categoria del empleado'
    }
    return render(request, 'personal.html',context)

@login_required
def solicitudNuevos(request):
    # Aquí la lógica para mostrar la página de inicio
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )

   # print(empleados)
    context = {
        'empleados' : empleados,
        'active_page': 'Nsolicitud',
        'nombre_usuario': nameUser(request),
        'categoria':'Aqui va la Categoria del empleado'
    }
    return render(request, 'nuevoPersonal.html',context)


def nameUser(request):
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name 
    
    return  nombreUsuario







def enviar_correo(request):
    
    print("se entro a la vista de envio de correo XD")

    if request.method == 'POST':
        dato1 = request.POST.get('nombre')
        dato2 = request.POST.get('puesto')
        
        mensaje = f'''
        Asunto: Alta de Usuario

        Hola,

        Aquí está el mensaje del correo con los datos:

        Nombre: {dato1}
        Puesto: {dato2}

        Atentamente,
        IDIAI
        CONFIDENCIALIDAD. Este e-mail y cualquiera de sus archivos anexos son confidenciales y pueden constituir información privilegiada. Si usted no es el destinatario adecuado, por favor, notifíquelo inmediatamente al emisor y elimínelo de su computadora, no revele estos contenidos a ninguna otra persona, no los utilice para otra finalidad, ni almacene o copie esta información en medio alguno. 
        CONFIDENTIALITY. This e-mail and any attachments thereof are confidential and may be privileged. If you are not a named recipient, please notify the sender immediately and delete it from your computer, do not disclose its contents to another person, use it for any purpose or store or copy the information in any medium

        '''
        
        #codigo parar visualizar el correo que se va enviar 
        datos = {
        'nombre': dato1,
        'puesto': dato2,
         }
        
            
        # Crear un mensaje HTML utilizando una plantilla (puedes personalizar la plantilla)
        html_message = get_template('CorreoSolicitudAlta.html').render({'nombre': dato1, 'puesto': dato2})

        # Crear el mensaje de texto plano
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                'Asunto del Mensaje prueba',
                plain_message ,
                'sistemas.iai@grupo-iai.com.mx',
                ['manuel.zarate@grupo-iai.com.mx'],
                fail_silently=False,
            )
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {e}")
             
    #return redirect(reverse('solicitud'))
        
    return render(request, 'CorreoSolicitudAlta.html', datos)
        
        
        # Aquí puedes utilizar dato1 y dato2 como necesites


    