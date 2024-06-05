import tkinter as tk
from tkinter import messagebox, simpledialog
from ldap3 import Server, Connection, ALL, NTLM, Tls
import ssl

def connect_ldap(port, server_address):
    if port == 389:
        protocol = "ldap://"
        use_ssl = False
        tls_configuration = None
    elif port == 636:
        protocol = "ldaps://"
        use_ssl = True
        # Configuración de TLS para validar certificados en LDAPS
        tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
    else:
        messagebox.showerror("Error", "Puerto no válido")
        return

    try:
        server = Server(f'{protocol}{server_address}:{port}', get_info=ALL, use_ssl=use_ssl, tls=tls_configuration)
        # Utiliza tus credenciales adecuadamente
        conn = Connection(server, user='GRUPO-IAI\\IDIAI', password='S0p0rt3i@i2024', authentication=NTLM)
        conn.bind()
        if conn.bound:
            messagebox.showinfo("Éxito", f"Conectado exitosamente a {server_address} a través del puerto {port}.")
        else:
            messagebox.showerror("Error", "No se pudo conectar al servidor. Verifica las credenciales o la configuración del servidor.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al intentar conectar: {str(e)}")
    finally:
        if conn.bound:
            conn.unbind()

# Función para obtener la dirección del servidor y realizar la conexión
def initiate_connection(port):
    server_address = server_address_input.get()  # Obtener la dirección del servidor del input
    if server_address:
        connect_ldap(port, server_address)
    else:
        messagebox.showerror("Error", "Por favor, introduce la dirección del servidor.")

# Crear la ventana de la aplicación
app = tk.Tk()
app.title("Conector LDAP/LDAPS")
app.geometry("350x200")

# Campo de entrada para la dirección del servidor
server_address_label = tk.Label(app, text="Dirección del servidor:")
server_address_label.pack(pady=(10,0))
server_address_input = tk.Entry(app)
server_address_input.pack(pady=(0,20))

# Crear botones
ldap_button = tk.Button(app, text="Conectar a LDAP (389)", command=lambda: initiate_connection(389))
ldap_button.pack(pady=5)

ldaps_button = tk.Button(app, text="Conectar a LDAPS (636)", command=lambda: initiate_connection(636))
ldaps_button.pack(pady=5)

# Iniciar la aplicación
app.mainloop()