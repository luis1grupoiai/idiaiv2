from django.contrib import admin
from .models import Permisos

admin.site.site_header = 'IDIAI v2'
admin.site.site_title = 'IDIAI V2'
admin.site.index_title = 'Sitio Administrativo IDIAI V2'


class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'codename', 'descripcion', 'status')
    fieldsets = (
        (None, {'fields': ('name', 'content_type', 'codename')}),
        ('Descripcion', {'fields': ('descripcion','status')}),
    )

# Registra tu modelo personalizado y aparecerá en "Autenticación y autorización"
admin.site.register(Permisos, CustomPermissionAdmin)
