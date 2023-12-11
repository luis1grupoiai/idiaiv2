from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Sistemas, SistemaPermisoGrupo

# Define un formulario para el modelo SistemaPermisoGrupo en la interfaz de administración de Django
class SistemaPermisoInlineForm(forms.ModelForm):
    class Meta:
        model = SistemaPermisoGrupo
        fields = '__all__'

    # Inicializa el formulario y filtra las opciones de permisos basándose en la aplicación 'sistemas-iai'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app_label = 'sistemas-iai'
        content_type = ContentType.objects.get(app_label=app_label)
        self.fields['permiso'].queryset = self.fields['permiso'].queryset.filter(content_type=content_type)

# Define una clase de línea en la interfaz de administración para el modelo SistemaPermisoGrupo
class SistemaPermisoInline(admin.TabularInline):
    model = SistemaPermisoGrupo
    form = SistemaPermisoInlineForm
    verbose_name = 'Añadir Permiso y/o Grupo'
    verbose_name_plural = 'Añadir Permiso y/o Grupo'

# Define una clase de administrador para el modelo Sistemas
class SistemaAdmin(admin.ModelAdmin):
    # Agrega la clase de línea SistemaPermisoInline a la interfaz de administración
    inlines = [SistemaPermisoInline]
    
    # Configura los campos que se mostrarán en la lista de objetos del modelo
    list_display = ('nombre', 'version', 'status', 'get_permisos', 'get_grupos', 'created_at', 'updated_at')
    
    # Agrega campos de búsqueda para facilitar la búsqueda en la interfaz de administración
    search_fields = ('nombre', 'status') 

    # Define métodos personalizados para obtener y mostrar permisos y grupos
    def get_permisos(self, obj):
        permisos = SistemaPermisoGrupo.objects.filter(sistema=obj)
        permisos_names = [p.permiso.name for p in permisos if p.permiso and p.permiso.name]
        return ' - '.join(permisos_names) if permisos_names else 'Sin Permisos'

    get_permisos.short_description = 'Permisos'

    def get_grupos(self, obj):
        grupos = SistemaPermisoGrupo.objects.filter(sistema=obj)
        grupos_names = [g.grupo.name for g in grupos if g.grupo and g.grupo.name]
        return ' - '.join(grupos_names) if grupos_names else 'Sin Grupos'

    get_grupos.short_description = 'Grupos'

# Registra el modelo Sistemas con su configuración personalizada en la interfaz de administración
admin.site.register(Sistemas, SistemaAdmin)

# Define una clase de administrador personalizada para el modelo Group en la interfaz de administración
class CustomGroupAdmin(admin.ModelAdmin):
    
    # Permite la selección de permisos utilizando una interfaz de filtro horizontal
    filter_horizontal = ('permissions',)  

    # Personaliza el formulario del grupo para filtrar las opciones de permisos basándose en la aplicación 'sistemas-iai'
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type__app_label='sistemas-iai')
        return form

# Anula el registro predeterminado del modelo Group en la interfaz de administración
admin.site.unregister(Group)

# Registra el modelo Group con la configuración personalizada en la interfaz de administración
admin.site.register(Group, CustomGroupAdmin)
