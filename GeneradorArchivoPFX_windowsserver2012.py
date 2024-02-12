import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess

def generate_pfx_with_openssl():
    cert_path = filedialog.askopenfilename(title="Selecciona el archivo de certificado (.crt)")
    if not cert_path:
        return
    
    key_path = filedialog.askopenfilename(title="Selecciona el archivo de clave privada (.key)")
    if not key_path:
        return
    
    pfx_path = filedialog.asksaveasfilename(defaultextension=".pfx", filetypes=[("Archivos PFX", "*.pfx")], title="Guardar como")
    if not pfx_path:
        return
    
    pfx_password = simpledialog.askstring("Contraseña PFX", "Ingresa la contraseña para el archivo PFX:", show='*')
    if not pfx_password:
        return
    
    # Comando OpenSSL para generar el archivo PFX
    command = f'openssl pkcs12 -export -out "{pfx_path}" -inkey "{key_path}" -in "{cert_path}" -passout pass:{pfx_password}'
    
    try:
        subprocess.run(command, check=True, shell=True)
        messagebox.showinfo("Éxito", "Archivo PFX generado exitosamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al generar el archivo PFX: {e}")

# Configuración de la ventana de la aplicación
app = tk.Tk()
app.title("Generador de Archivos PFX para Windows Server 2012")
app.geometry("500x250")

generate_button = tk.Button(app, text="Generar Archivo PFX con OpenSSL", command=generate_pfx_with_openssl)
generate_button.pack(pady=50)

app.mainloop()
#openssl pkcs12 -export -out certificate.pfx -inkey private.key -in certificate.crt -keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES
#openssl pkcs12 -export -out "salida.pfx" -inkey "private.key" -in "certificate.crt" -passout pass:tu_contraseña_aqui
