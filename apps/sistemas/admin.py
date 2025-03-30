from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from .models import Sistemas, SistemaPermisoGrupo, UserSPG
from .signals import set_changed_by
from config.logger_setup import LoggerSetup
import os

entorno = os.environ.get('DJANGO_ENV')
logger = LoggerSetup.setup_logger_for_environment('sistemas', entorno)

class SistemaPermisoInlineForm(forms.ModelForm):
    class Meta:
        model = SistemaPermisoGrupo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app_label = 'sistemas-iai'
        content_types = ContentType.objects.filter(app_label=app_label)
        self.fields['permiso'].queryset = self.fields['permiso'].queryset.filter(content_type__in=content_types)

class SistemaPermisoInline(admin.TabularInline):
    model = SistemaPermisoGrupo
    form = SistemaPermisoInlineForm
    verbose_name = 'Añadir Permiso y/o Grupo'
    verbose_name_plural = 'Añadir Permiso y/o Grupo'

class SistemaAdmin(admin.ModelAdmin):
    inlines = [SistemaPermisoInline]
    list_display = ('nombre', 'version', 'status', 'get_permisos', 'get_grupos', 'created_at', 'updated_at')
    search_fields = ('nombre', 'status')

    def save_model(self, request, obj, form, change):
        if change:
            logger.info(f'Usuario {request.user} actualizó el sistema: {obj.nombre}')
        else:
            logger.info(f'Usuario {request.user} creó un nuevo sistema: {obj.nombre}')
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        logger.warning(f'Usuario {request.user} eliminó el sistema: {obj.nombre}')
        super().delete_model(request, obj)

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

admin.site.register(Sistemas, SistemaAdmin)

class CustomGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type__app_label='sistemas-iai')
        return form

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

