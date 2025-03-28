from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserChangeForm
from .models import UserAreas, Coordinacion, Gerencia, Direccion
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib import messages
from apps.sistemas.signals import set_changed_by

# Formulario personalizado para edición de usuarios que filtra permisos
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra permisos para mostrar solo los de la app 'sistemas-iai'
        self.fields['user_permissions'].queryset = self.fields['user_permissions'].queryset.filter(
            content_type__app_label='sistemas-iai'
        )

# Formulario para las áreas de usuario con filtrado de áreas activas y con encargados
class UserAreasInlineForm(forms.ModelForm):
    class Meta:
        model = UserAreas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra áreas que estén activas (estado=1) y que tengan encargados asignados
        self.fields['coordinacion'].queryset = Coordinacion.objects.filter(estado=1, id_coordinador_id__isnull=False)
        self.fields['gerencia'].queryset = Gerencia.objects.filter(estado=1, id_gerente_id__isnull=False)
        self.fields['direccion'].queryset = Direccion.objects.filter(estado=1, id_director_id__isnull=False)

# Inline para asignación de áreas a usuarios en el admin de Django
class UserAreasInline(admin.StackedInline):
    model = UserAreas
    form = UserAreasInlineForm
    can_delete = False
    verbose_name_plural = 'Asignación de Áreas'
    max_num = 1  # Solo permite una asignación por usuario
    
    def has_add_permission(self, request, obj=None):
        """Previene que usuarios encargados de áreas tengan asignaciones adicionales"""
        if obj and self.is_user_in_charge(obj):
            return False
        return True
    
    def has_change_permission(self, request, obj=None):
        """Bloquea la edición para usuarios que son encargados de áreas"""
        if obj and self.is_user_in_charge(obj):
            return False
        return True
    
    def is_user_in_charge(self, user):
        """Determina si un usuario es encargado de alguna área (director, gerente o coordinador)"""
        return (Direccion.objects.filter(id_director=user, estado=1).exists() or
                Gerencia.objects.filter(id_gerente=user, estado=1).exists() or
                Coordinacion.objects.filter(id_coordinador=user, estado=1).exists())

# Admin personalizado para el modelo User de Django
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    inlines = (UserAreasInline,)
    list_display = ('username', 'get_nombre_completo', 'get_coordinacion', 'get_gerencia', 'get_direccion')

    def get_inline_instances(self, request, obj=None):
        """Oculta el inline de áreas si el usuario es encargado"""
        if obj and self.is_user_in_charge(obj):
            return []
        return super().get_inline_instances(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Muestra mensaje informativo cuando se edita un usuario encargado"""
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)

        if obj and self.is_user_in_charge(obj):
            messages.info(request, f'Este usuario es {self.get_user_charge_info(obj)}, por lo que no necesita asignación adicional de áreas.')

        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """Registra quién hizo el cambio y elimina asignaciones si el usuario se convierte en encargado"""
        set_changed_by(request.user)
        super().save_model(request, obj, form, change)

        # Elimina asignación de áreas si el usuario ahora es encargado
        if self.is_user_in_charge(obj):
            UserAreas.objects.filter(user=obj).delete()

    def is_user_in_charge(self, user):
        """Verifica si el usuario tiene un cargo de responsabilidad"""
        return (Direccion.objects.filter(id_director=user, estado=1).exists() or
                Gerencia.objects.filter(id_gerente=user, estado=1).exists() or
                Coordinacion.objects.filter(id_coordinador=user, estado=1).exists())

    def get_user_charge_info(self, user):
        """Devuelve una cadena descriptiva del cargo del usuario"""
        if direccion := Direccion.objects.filter(id_director=user).first():
            return f"Director de {direccion.nombre}"
        if gerencia := Gerencia.objects.filter(id_gerente=user).first():
            return f"Gerente de {gerencia.nombre}"
        if coordinacion := Coordinacion.objects.filter(id_coordinador=user).first():
            return f"Coordinador de {coordinacion.nombre}"
        return "Sin cargo asignado"
    
    def save_related(self, request, form, formsets, change):
        """Maneja el guardado de relaciones, omitiendo UserAreas para encargados"""
        set_changed_by(request.user)
        obj = form.instance
        
        # Solo guarda UserAreas si el usuario no es encargado
        if not self.is_user_in_charge(obj):
            super().save_related(request, form, formsets, change)

    # Métodos para mostrar información en la lista de usuarios
    def get_nombre_completo(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    get_nombre_completo.short_description = 'Nombre'

    def get_coordinacion(self, obj):
        """Obtiene la coordinación del usuario, priorizando si es encargado"""
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj, estado=1).first():
            return coordinacion.nombre
        try:
            user_area = UserAreas.objects.get(user=obj)
            return user_area.coordinacion.nombre if user_area.coordinacion else 'Sin coordinación'
        except UserAreas.DoesNotExist:
            return 'Sin coordinación'
    get_coordinacion.short_description = 'Coordinación'

    def get_gerencia(self, obj):
        """Obtiene la gerencia del usuario, con lógica compleja de jerarquía"""
        if gerencia := Gerencia.objects.filter(id_gerente=obj, estado=1).first():
            return gerencia.nombre
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj, estado=1).first():
            return coordinacion.id_gerencia.nombre if coordinacion.id_gerencia else 'Sin gerencia'
        try:
            user_area = UserAreas.objects.get(user=obj)
            if user_area.coordinacion and user_area.coordinacion.id_gerencia:
                return user_area.coordinacion.id_gerencia.nombre
            if user_area.gerencia:
                return user_area.gerencia.nombre
        except UserAreas.DoesNotExist:
            pass
        return 'Sin gerencia'
    get_gerencia.short_description = 'Gerencia'

    def get_direccion(self, obj):
        """Obtiene la dirección del usuario, con lógica compleja de jerarquía"""
        if direccion := Direccion.objects.filter(id_director=obj, estado=1).first():
            return direccion.nombre
        if gerencia := Gerencia.objects.filter(id_gerente=obj, estado=1).first():
            return gerencia.id_direccion.nombre if gerencia.id_direccion else 'Sin dirección'
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj, estado=1).first():
            if coordinacion.id_gerencia and coordinacion.id_gerencia.id_direccion:
                return coordinacion.id_gerencia.id_direccion.nombre
            elif coordinacion.id_direccion:
                return coordinacion.id_direccion.nombre
        try:
            user_area = UserAreas.objects.get(user=obj)
            if user_area.coordinacion:
                if user_area.coordinacion.id_gerencia and user_area.coordinacion.id_gerencia.id_direccion:
                    return user_area.coordinacion.id_gerencia.id_direccion.nombre
                if user_area.coordinacion.id_direccion:
                    return user_area.coordinacion.id_direccion.nombre
            if user_area.gerencia and user_area.gerencia.id_direccion:
                return user_area.gerencia.id_direccion.nombre
            if user_area.direccion:
                return user_area.direccion.nombre
        except UserAreas.DoesNotExist:
            pass
        return 'Sin dirección'
    get_direccion.short_description = 'Dirección'

# Registro personalizado del modelo User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Admin para el modelo Coordinacion
class CoordinacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'coordinador', 'gerencia', 'direccion', 'created_at', 'updated_at')
    search_fields = ('nombre', 'abreviatura', 'id_coordinador__username')
    list_filter = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Muestra solo coordinaciones activas (estado=1)"""
        return super().get_queryset(request).filter(estado=1)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra direcciones y gerencias para mostrar solo las activas con encargados"""
        if db_field.name == "id_direccion":  
            kwargs["queryset"] = Direccion.objects.filter(estado=1, id_director_id__isnull=False)
        elif db_field.name == "id_gerencia":
            kwargs["queryset"] = Gerencia.objects.filter(estado=1, id_gerente_id__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Métodos para mostrar información relacionada en la lista
    def coordinador(self, obj):
        return obj.id_coordinador.username if obj.id_coordinador else "Sin asignar"
    coordinador.short_description = 'Coordinador'

    def gerencia(self, obj):
        return obj.id_gerencia.nombre if obj.id_gerencia else "Sin asignar"
    gerencia.short_description = 'Gerencia'

    def direccion(self, obj):
        return obj.id_direccion.nombre if obj.id_direccion else "Sin asignar"
    direccion.short_description = 'Dirección'

admin.site.register(Coordinacion, CoordinacionAdmin)

# Admin para el modelo Gerencia
class GerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'gerente', 'direccion', 'created_at', 'updated_at')
    search_fields = ('nombre', 'abreviatura', 'id_gerente__username')
    list_filter = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Muestra solo gerencias activas (estado=1)"""
        return super().get_queryset(request).filter(estado=1)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra direcciones para mostrar solo las activas con encargados"""
        if db_field.name == "id_direccion":  
            kwargs["queryset"] = Direccion.objects.filter(estado=1, id_director_id__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def gerente(self, obj):
        return obj.id_gerente.username if obj.id_gerente else "Sin asignar"
    gerente.short_description = 'Gerente'

    def direccion(self, obj):
        return obj.id_direccion.nombre if obj.id_direccion else "Sin asignar"
    direccion.short_description = 'Dirección'

admin.site.register(Gerencia, GerenciaAdmin)

# Admin para el modelo Direccion
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'nombreCorto', 'director', 'estado', 'created_at', 'updated_at')
    search_fields = ('nombre', 'abreviatura', 'id_gerente__username')
    list_filter = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Muestra solo direcciones activas (estado=1)"""
        return super().get_queryset(request).filter(estado=1)

    def director(self, obj):
        return obj.id_director.username if obj.id_director else "Sin asignar"
    director.short_description = 'Director'

admin.site.register(Direccion, DireccionAdmin)

# Admin personalizado para el modelo Permission
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type', 'descripcion', 'status')

    def get_queryset(self, request):
        """Filtra permisos para mostrar solo los de la app 'sistemas-iai'"""
        return super().get_queryset(request).filter(content_type__app_label='sistemas-iai')

admin.site.register(Permission, PermissionAdmin)

# Habiltar el ContentType en la vista Admin de Django
# class CustomContentTypeAdmin(admin.ModelAdmin):
#     # Campos que quieres mostrar en la lista de ContentType
#     list_display = ('app_label', 'model')

# # Registra el admin personalizado para ContentType
# admin.site.register(ContentType, CustomContentTypeAdmin)

