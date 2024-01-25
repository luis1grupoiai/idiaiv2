from ldap3 import Server, Connection, ALL, NTLM

# Para LDAP (puerto 389)
server = Server('ldap://192.192.194.10', port=389, get_info=ALL)
conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM)
conn.bind()
print(conn.bound)

# Para LDAPS (puerto 636 con SSL)
server = Server('ldaps://192.192.194.10:636', get_info=ALL, use_ssl=True)
conn = Connection(server, user='iai\\desarrollo', password='D3sarrollo', authentication=NTLM)
conn.bind()
print(conn.bound)


