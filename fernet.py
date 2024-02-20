#
#Las llaves generadas por la clase Fernet del módulo cryptography en Python están diseñadas para ofrecer una seguridad 
#muy alta, adecuada para la mayoría de los usos prácticos de cifrado. Aquí hay algunos detalles sobre la complejidad y 
#seguridad de estas llaves:
#
#Longitud de la llave: Las llaves generadas por Fernet tienen una longitud de 256 bits. Esta longitud es considerada muy 
# #segura para la criptografía simétrica, según los estándares actuales, incluyendo las recomendaciones del NIST 
# #(Instituto Nacional de Estándares y Tecnología de EE.UU.).

#Algoritmo de cifrado: Fernet utiliza AES (Advanced Encryption Standard) en modo CBC (Cipher Block Chaining) para el
#cifrado de datos. AES es ampliamente reconocido y utilizado por gobiernos, sistemas financieros y en la industria en 
#general como un estándar de cifrado robusto y seguro.

#Seguridad de la implementación: La biblioteca cryptography es de código abierto y ha sido revisada por la comunidad 
#de seguridad. Aunque ninguna implementación de software puede garantizarse como perfectamente segura, el uso de
#bibliotecas bien mantenidas y ampliamente revisadas como cryptography minimiza el riesgo de vulnerabilidades 
#relacionadas con el cifrado.

#Gestión de llaves: La seguridad de cualquier sistema de cifrado depende en gran medida de cómo se manejan las 
#llaves. Incluso la llave más segura puede comprometerse si no se maneja adecuadamente (por ejemplo, si se 
#almacena o transmite de forma insegura).

#Entropía: La función generate_key() genera llaves utilizando fuentes de entropía seguras proporcionadas por
#el sistema operativo. Esto asegura que las llaves sean aleatorias y difíciles de predecir.

#En resumen, las llaves generadas por Fernet son adecuadas para proteger datos sensibles contra ataques de 
#fuerza bruta y otras formas de criptoanálisis conocidas hasta la fecha. Sin embargo, la seguridad total del
#sistema también dependerá de otros factores, como la gestión segura de las llaves, la protección del sistema 
#que las utiliza y la vigilancia contra vulnerabilidades emergentes en el ámbito de la criptografía.



import tkinter as tk
from tkinter import ttk
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key().decode()

def copy_to_clipboard(key):
    root.clipboard_clear()
    root.clipboard_append(key)
    root.update() # Esto asegura que el contenido se mantenga en el portapapeles incluso después de cerrar la aplicación

# Crear la ventana principal
root = tk.Tk()
root.title("Generador de Llaves de Encriptación")

# Configurar el tamaño de la ventana
root.geometry("500x200")

# Función para actualizar la llave y copiar al portapapeles
def generate_and_show_key(label):
    new_key = generate_key()
    label.config(text=new_key)

# Generar primera llave, mostrarla y botón para copiar al portapapeles
ttk.Label(root, text="Llave 1:").pack(pady=(10,0))
key1_label = ttk.Label(root, text=generate_key())
key1_label.pack()
ttk.Button(root, text="Generar y Copiar Llave 1", command=lambda: [generate_and_show_key(key1_label), copy_to_clipboard(key1_label.cget("text"))]).pack(pady=5)

# Generar segunda llave, mostrarla y botón para copiar al portapapeles
ttk.Label(root, text="Llave 2:").pack(pady=(10,0))
key2_label = ttk.Label(root, text=generate_key())
key2_label.pack()
ttk.Button(root, text="Generar y Copiar Llave 2", command=lambda: [generate_and_show_key(key2_label), copy_to_clipboard(key2_label.cget("text"))]).pack(pady=5)

root.mainloop()