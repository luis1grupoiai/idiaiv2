from django.contrib import admin
from .models import Sistemas, SistemaPermisoGrupo

class SistemaPermisoInline(admin.TabularInline):
    model = SistemaPermisoGrupo 

class SistemaAdmin(admin.ModelAdmin):
    inlines = [SistemaPermisoInline]

admin.site.register(Sistemas, SistemaAdmin)
