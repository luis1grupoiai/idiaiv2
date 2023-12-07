from django.contrib import admin
from .models import Sistemas, SistemaPermiso

class SistemaPermisoInline(admin.TabularInline):
    model = SistemaPermiso

class SistemaAdmin(admin.ModelAdmin):
    inlines = [SistemaPermisoInline]

admin.site.register(Sistemas, SistemaAdmin)
