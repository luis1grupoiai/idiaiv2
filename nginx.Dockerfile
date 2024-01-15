# Usa la imagen oficial de Nginx como base
FROM nginx:1.25.3-bookworm

# Elimina el archivo de configuración predeterminado de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia tu archivo de configuración personalizado de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto en el que Nginx estará escuchando
EXPOSE 80

# Define el comando predeterminado al iniciar el contenedor
CMD ["nginx", "-g", "daemon off;"]