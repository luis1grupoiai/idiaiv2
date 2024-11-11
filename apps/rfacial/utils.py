from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from pathlib import Path
import os
from datetime import datetime

# EMC 11/11/24 : La clase `EnvioCorreos` se encarga de rendirizar y enviar el correo.
class EnvioCorreos:
    def __init__(self, asunto, destinatarios, contexto_html):
        self.asunto = asunto
        self.destinatarios = destinatarios if isinstance(destinatarios, list) else [destinatarios]
        self.contexto_html = contexto_html or {}  # Contexto dinámico para la plantilla HTML
        self.from_email = 'sistemas.iai@grupo-iai.com.mx'

    def cargar_y_renderizar_plantilla(self):
        # Define la ruta a la plantilla
        template_path = 'apps/rfacial/templates/enviarCorreo.html'

        print(f"El asunto del correo es: {self.asunto}")
        print(f"El contenido del correo es: {self.contexto_html}")
        print(f"El destinatario del correo es: {self.destinatarios}")
        
        # Cargar el contenido de la plantilla HTML
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        # Crear el contexto de la plantilla con los datos dinámicos
        context = Context({
            "sistema": self.contexto_html.get("sistema", ""),
            "asunto": self.asunto,
            "contenido": self.contexto_html.get("contenido", ""),
            "URL" : self.contexto_html.get("URL", ""),
            "year": datetime.now().year,
            **self.contexto_html  # Agregar variables adicionales al contexto si es necesario
        })

        # Renderizar la plantilla con los datos
        template = Template(template_content)
        return template.render(context)

    def enviar(self):
        try:
            # Renderizar el HTML del correo
            plantilla_html = self.cargar_y_renderizar_plantilla()
            
            # Crear el correo solo con HTML
            correo = EmailMultiAlternatives(
                subject=self.asunto,
                from_email=self.from_email,
                to=self.destinatarios,
            )
            correo.attach_alternative(plantilla_html, "text/html")  # Adjuntar solo HTML
            
            # Enviar el correo
            correo.send()
            return {"status": "success", "message": "Correo enviado exitosamente"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
