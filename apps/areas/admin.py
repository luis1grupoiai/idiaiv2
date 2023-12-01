from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserCoordinacion, Coordinacion

admin.site.site_header = 'IDIAI v2'
admin.site.site_title = 'IDIAI v2'
admin.site.index_title = 'Sitio Administrativo IDIAI v2'

class UserProfileInline(admin.StackedInline):
    model = UserCoordinacion
    can_delete = False
    verbose_name_plural = 'Coordinacion de usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'coordinacion_display')  # Agrega campos adicionales que deseas mostrar en la lista

    def coordinacion_display(self, obj):
        return obj.usercoordinacion.coordinacion  # Ajusta según la relación real en tu modelo

    coordinacion_display.short_description = 'Coordinacion'  # Nombre que se mostrará en la lista

# Desregistras el UserAdmin de Django
admin.site.unregister(User)

# Registra tu CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
# admin.site.register(UserCoordinacion)
class CoordinacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'coordinador', 'created_at', 'updated_at')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'abreviatura', 'id_coordinador__username')  # Agregar campos para búsqueda
    list_filter = ('created_at', 'updated_at')  # Agregar filtros laterales

    def coordinador(self, obj):
        return obj.id_coordinador.username  # Muestra el nombre de usuario del coordinador

    coordinador.short_description = 'Jefe de Coordinación'  # Nombre que se mostrará en la lista

    # Otros ajustes según tus necesidades
admin.site.register(Coordinacion, CoordinacionAdmin)