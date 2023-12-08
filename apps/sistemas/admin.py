from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Sistemas, SistemaPermisoGrupo

class SistemaPermisoInlineForm(forms.ModelForm):
    class Meta:
        model = SistemaPermisoGrupo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra los permisos por app_label
        app_label = 'sistemas-iai'  # Reemplaza 'tu_app_label' con el valor correcto
        content_type = ContentType.objects.get(app_label=app_label)
        self.fields['permiso'].queryset = self.fields['permiso'].queryset.filter(content_type=content_type)

class SistemaPermisoInline(admin.TabularInline):
    model = SistemaPermisoGrupo
    form = SistemaPermisoInlineForm
    verbose_name = 'Añadir Permiso y/o Grupo'
    verbose_name_plural = 'Añadir Permiso y/o Grupo'

class SistemaAdmin(admin.ModelAdmin):
    inlines = [SistemaPermisoInline]

admin.site.register(Sistemas, SistemaAdmin)


class CustomGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)  # Asegura que la lista de permisos se muestre correctamente

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filtra los permisos por app_label, en este caso, "sistemas-iai"
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type__app_label='sistemas-iai')
        return form

# Desregistras el modelo Group predeterminado
admin.site.unregister(Group)

# Registras el modelo Group con tu clase personalizada
admin.site.register(Group, CustomGroupAdmin)
