from django.contrib import admin
from .models import Permisos
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


admin.site.site_header = 'IDIAI v2'
admin.site.site_title = 'IDIAI V2'
admin.site.index_title = 'Sitio Administrativo IDIAI V2'


class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'descripcion', 'status')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content_type'].queryset = ContentType.objects.filter(app_label='sistemas-iai')
        return form

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = queryset.filter(content_type__app_label='sistemas-iai')
        return queryset, use_distinct

    fieldsets = (
        (None, {'fields': ('name', 'content_type', 'codename')}),
        ('Descripcion', {'fields': ('descripcion', 'status')}),
    )

    def get_queryset(self, request):
        # Filtra los permisos por app_label, en este caso, "sistemas-iai"
        return super().get_queryset(request).filter(content_type__app_label='sistemas-iai')

# Registra tu modelo personalizado y aparecerá en "Autenticación y autorización"
admin.site.register(Permisos, CustomPermissionAdmin)

# # class PermissionAdmin(admin.ModelAdmin):
# #     list_display = ( 'name', 'codename', 'descripcion', 'status')
    
# #     def get_queryset(self, request):
# #         # Filtra los permisos por app_label, en este caso, "sistemas-iai"
# #         return super().get_queryset(request).filter(content_type__app_label='sistemas-iai')

# # # Registra el modelo Permission en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase PermissionAdmin
# # admin.site.register(Permission, PermissionAdmin)
