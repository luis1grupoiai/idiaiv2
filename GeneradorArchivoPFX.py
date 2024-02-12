import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

def load_certificate_and_key(cert_path, key_path):
    with open(cert_path, 'rb') as cert_file:
        cert_data = cert_file.read()
    certificate = x509.load_pem_x509_certificate(cert_data, default_backend())

    with open(key_path, 'rb') as key_file:
        key_data = key_file.read()
    private_key = serialization.load_pem_private_key(key_data, password=None, backend=default_backend())

    return certificate, private_key

def export_to_pfx(certificate, private_key, pfx_path, pfx_password):
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=b"My Certificate",
        key=private_key,
        cert=certificate,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(pfx_password.encode())
    )

    with open(pfx_path, 'wb') as pfx_file:
        pfx_file.write(pfx_data)
    messagebox.showinfo("Éxito", f"Archivo PFX generado en: {pfx_path}")

def generate_pfx():
    cert_path = filedialog.askopenfilename(title="Selecciona el archivo de certificado (.crt)")
    if not cert_path:
        return
    
    key_path = filedialog.askopenfilename(title="Selecciona el archivo de clave privada (.key)")
    if not key_path:
        return
    
    pfx_password = simpledialog.askstring("Contraseña PFX", "Ingresa la contraseña para el archivo PFX:", show='*')
    if not pfx_password:
        return
    
    pfx_path = filedialog.asksaveasfilename(defaultextension=".pfx", filetypes=[("Archivos PFX", "*.pfx")], title="Guardar como")
    if not pfx_path:
        return
    
    certificate, private_key = load_certificate_and_key(cert_path, key_path)
    export_to_pfx(certificate, private_key, pfx_path, pfx_password)

# Configuración de la ventana de la aplicación
app = tk.Tk()
app.title("Generador de Archivos PFX")
app.geometry("400x200")

generate_button = tk.Button(app, text="Generar Archivo PFX", command=generate_pfx)
generate_button.pack(pady=50)

app.mainloop()
#openssl pkcs12 -export -out certificate.pfx -inkey private.key -in certificate.crt 