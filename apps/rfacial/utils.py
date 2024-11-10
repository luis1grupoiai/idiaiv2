# utils.py
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from pathlib import Path
from dotenv import load_dotenv
import os
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / '.env'  # Ruta al archivo .env

# Verifica que la ruta es correcta
print("Ruta del archivo .env:", env_path)

load_dotenv(env_path)  
print("EMAIL_HOST:", os.getenv("EMAIL_HOST"))
print("EMAIL_HOST_USER:", os.getenv("EMAIL_HOST_USER"))
print("EMAIL_HOST_PASSWORD:", os.getenv("EMAIL_HOST_PASSWORD"))
print("DEFAULT_FROM_EMAIL:", os.getenv("DEFAULT_FROM_EMAIL"))

class EnvioCorreos:
    def __init__(self, asunto, destinatarios, mensaje_texto, mensaje_html=None):
        self.asunto = asunto
        self.destinatarios = destinatarios if isinstance(destinatarios, list) else [destinatarios]
        self.mensaje_texto = mensaje_texto
        self.mensaje_html = mensaje_html
        self.from_email = 'sistemas.iai@grupo-iai.com.mx';
    def enviar(self):
        try:
            # Crear el correo con texto y HTML opcional
            correo = EmailMultiAlternatives(
                subject=self.asunto,
                body=self.mensaje_texto,
                from_email=self.from_email,
                to=self.destinatarios,
            )
            if self.mensaje_html:
                correo.attach_alternative(self.mensaje_html, "text/html")
            
            # Enviar el correo
            correo.send()
            return {"status": "success", "message": "Correo enviado exitosamente"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
