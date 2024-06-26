#from ldap3 import Server, Connection, ALL, NTLM

# Para LDAP (puerto 389)
#server = Server('ldap://192.192.194.10', port=389, get_info=ALL)
#conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM)
#conn.bind()
#print(conn.bound)

# Para LDAPS (puerto 636 con SSL)
#server = Server('ldaps://192.192.194.10:636', get_info=ALL, use_ssl=True)
#conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM)
#conn.bind()
#print(conn.bound)

import tkinter as tk
from tkinter import messagebox, simpledialog
from ldap3 import Server, Connection, ALL, NTLM

def connect_ldap(port, server_address):
    if port == 389:
        protocol = "ldap://"
    elif port == 636:
        protocol = "ldaps://"
    else:
        messagebox.showerror("Error", "Puerto no válido")
        return
    
    server = Server(f'{protocol}{server_address}:{port}', get_info=ALL, use_ssl=(port == 636))
    print(server)
   # conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM) #
    conn = Connection(server, user='GRUPO-IAI\\IDIAI', password='S0p0rt3i@i2024', authentication=NTLM) #ldaps://DC:636
    try:
        conn.bind()
        if conn.bound:
            messagebox.showinfo("Éxito", f"Conectado exitosamente a {server_address} a través del puerto {port}.")
        else:
            messagebox.showerror("Error", "No se pudo conectar al servidor.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al intentar conectar: {str(e)}")
    finally:
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
server_address_label = tk.Label(app, text="Dirección del servidor:192.192.194.10")
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

"""
import tkinter as tk
from tkinter import messagebox
from ldap3 import Server, Connection, ALL, NTLM

def connect_ldap(port):
    if port == 389:
        protocol = "ldap://"
    elif port == 636:
        protocol = "ldaps://"
    else:
        messagebox.showerror("Error", "Puerto no válido")
        return
    
    server_address = '192.192.194.10'
    server = Server(f'{protocol}{server_address}:{port}', get_info=ALL, use_ssl=(port == 636))
    conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM)
    
    try:
        conn.bind()
        if conn.bound:
            messagebox.showinfo("Éxito", f"Conectado exitosamente a través del puerto {port}.")
        else:
            messagebox.showerror("Error", "No se pudo conectar al servidor.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al intentar conectar: {str(e)}")
    finally:
        conn.unbind()

# Crear la ventana de la aplicación
app = tk.Tk()
app.title("Conector LDAP/LDAPS")
app.geometry("300x150")

# Crear botones
ldap_button = tk.Button(app, text="Conectar a LDAP (389)", command=lambda: connect_ldap(389))
ldap_button.pack(pady=10)

ldaps_button = tk.Button(app, text="Conectar a LDAPS (636)", command=lambda: connect_ldap(636))
ldaps_button.pack(pady=10)

# Iniciar la aplicación
app.mainloop()

"""







































"""
librerias que hacen funcionar el proyecto ;) esto es un regalo de mi para el futuro XD
absl-py                       2.0.0
annotated-types               0.6.0
asgiref                       3.7.2
attrs                         23.1.0
bcrypt                        4.1.1
certifi                       2023.11.17
cffi                          1.16.0
charset-normalizer            3.3.2
click                         8.1.7
cmake                         3.27.7
colorama                      0.4.6
contourpy                     1.2.0
cryptography                  41.0.7
cycler                        0.12.1
Django                        4.2.7
django-components             0.29
django-jazzmin                2.6.0
django-mssql-backend          2.8.1
django-querycount             0.8.3
django-sslserver              0.22
django-unfold                 0.18.0
djangorestframework           3.14.0
djangorestframework-simplejwt 5.3.1
dlib                          19.24.2
dotty-dict                    1.3.1
drf-yasg                      1.21.7
face-recognition              1.3.0
face_recognition_models       0.3.0
flatbuffers                   23.5.26
fonttools                     4.46.0
gitdb                         4.0.11
GitPython                     3.1.40
gunicorn                      21.2.0
idna                          3.6
importlib-resources           6.1.1
inflection                    0.5.1
Jinja2                        3.1.2
kiwisolver                    1.4.5
ldap3                         2.9.1
markdown-it-py                3.0.0
MarkupSafe                    2.1.3
matplotlib                    3.8.2
mdurl                         0.1.2
mediapipe                     0.10.8
mssql-django                  1.3
numpy                         1.26.2
opencv-contrib-python         4.8.1.78
opencv-python                 4.8.1.78
packaging                     23.2
passlib                       1.7.4
Pillow                        10.1.0
pip                           23.3.2
protobuf                      3.20.3
psycopg2                      2.9.9
pyasn1                        0.5.1
pycparser                     2.21
pycryptodome                  3.20.0
pydantic                      2.5.3
pydantic_core                 2.14.6
Pygments                      2.17.2
PyJWT                         2.8.0
pyodbc                        5.0.1
pyparsing                     3.1.1
python-dateutil               2.8.2
python-dotenv                 1.0.0
python-gitlab                 4.3.0
python-semantic-release       8.7.0
pytz                          2023.3.post1
PyYAML                        6.0.1
requests                      2.31.0
requests-toolbelt             1.0.0
rich                          13.7.0
setuptools                    65.5.0
shellingham                   1.5.4
six                           1.16.0
smmap                         5.0.1
sounddevice                   0.4.6
sqlparse                      0.4.4
tomlkit                       0.12.3
typing_extensions             4.9.0
tzdata                        2023.3
uritemplate                   4.1.1
urllib3                       2.1.0
wfastcgi                      3.0.0
whitenoise                    6.6.0
"""
