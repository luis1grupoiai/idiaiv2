from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from pathlib import Path
import os
from datetime import datetime
from django.template.loader import render_to_string

# EMC 11/11/24 : La clase `EnvioCorreos` se encarga de rendirizar y enviar el correo.
class EnvioCorreos:
    def __init__(self, asunto, destinatarios, contexto_html):
        self.asunto = asunto
        self.destinatarios = destinatarios if isinstance(destinatarios, list) else [destinatarios]
        self.contexto_html = contexto_html or {}
        self.from_email = 'sistemas.iai@grupo-iai.com.mx'

    def cargar_y_renderizar_plantilla(self):
        # Agrega las variables adicionales al contexto
        context = {
            "sistema": self.contexto_html.get("sistema", ""),
            "asunto": self.asunto,
            "contenido": self.contexto_html.get("contenido", ""),
            "URL": self.contexto_html.get("URL", ""),
            "year": datetime.now().year,
            **self.contexto_html
        }
        
        # Renderizar directamente usando render_to_string
        return render_to_string('enviarCorreo.html', context)

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
            correo.attach_alternative(plantilla_html, "text/html")
            
            # Enviar el correo
            correo.send()
            return {"status": "success", "message": "Correo enviado exitosamente"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
