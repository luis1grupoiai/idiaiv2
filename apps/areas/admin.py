from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission
from .models import UserCoordinacion, Coordinacion, Gerencia, Direccion

admin.site.site_header = 'IDIAI v2'
admin.site.site_title = 'IDIAI v2'
admin.site.index_title = 'Sitio Administrativo IDIAI v2'

class UserProfileInline(admin.StackedInline):
    model = UserCoordinacion
    can_delete = False
    verbose_name_plural = 'Coordinacion de usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('first_name', 'last_name', 'coordinacion', 'is_staff')  # Agrega campos adicionales que deseas mostrar en la lista

    def coordinacion(self, obj):
        return obj.usercoordinacion.coordinacion  # Ajusta según la relación real en tu modelo

    coordinacion.short_description = 'Coordinacion'  # Nombre que se mostrará en la lista

# Desregistras el UserAdmin de Django
admin.site.unregister(User)

# Registra tu CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
# admin.site.register(UserCoordinacion)

class CoordinacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'coordinador', 'gerencia' , 'direccion' ,'created_at', 'updated_at')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'abreviatura', 'id_coordinador__username')  # Agregar campos para búsqueda
    list_filter = ('created_at', 'updated_at')  # Agregar filtros laterales

    def coordinador(self, obj):
        if obj.id_coordinador:
            return obj.id_coordinador.username
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    coordinador.short_description = 'Jefe de Coordinación'  # Nombre que se mostrará en la lista

    def gerencia(self, obj):
        if obj.id_gerencia:
            return obj.id_gerencia.nombre
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    gerencia.short_description = 'Gerencia'  # Corregido el nombre que se mostrará en la lista

    def direccion(self, obj):
        if obj.id_direccion:
            return obj.id_direccion.nombre
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    direccion.short_description = 'Direccion'  # Corregido el nombre que se mostrará en la lista

    # Otros ajustes según tus necesidades
admin.site.register(Coordinacion, CoordinacionAdmin)

class GerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'gerente', 'direccion', 'created_at', 'updated_at')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'abreviatura', 'id_gerente__username')  # Agregar campos para búsqueda
    list_filter = ('created_at', 'updated_at')  # Agregar filtros laterales

    def gerente(self, obj):
        if obj.id_gerente:
            return obj.id_gerente.username
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    gerente.short_description = 'Gerente'  # Nombre que se mostrará en la lista

    def direccion(self, obj):
        if obj.id_direccion:
            return obj.id_direccion.nombre
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    direccion.short_description = 'Direccion'  # Corregido el nombre que se mostrará en la lista

admin.site.register(Gerencia, GerenciaAdmin)

class DireccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'rfc', 'director', 'created_at', 'updated_at')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'abreviatura', 'id_gerente__username')  # Agregar campos para búsqueda
    list_filter = ('created_at', 'updated_at')  # Agregar filtros laterales

    def director(self, obj):
        if obj.id_director:
            return obj.id_director.username
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    director.short_description = 'Director'  # Nombre que se mostrará en la lista

admin.site.register(Direccion, DireccionAdmin)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'codename', 'descripcion', 'status')

admin.site.register(Permission, PermissionAdmin)