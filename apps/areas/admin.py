from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserChangeForm
from .models import UserAreas, Coordinacion, Gerencia, Direccion
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib import messages
from apps.sistemas.signals import set_changed_by

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_permissions'].queryset = self.fields['user_permissions'].queryset.filter(
            content_type__app_label='sistemas-iai'
        )

class UserAreasInlineForm(forms.ModelForm):
    class Meta:
        model = UserAreas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coordinacion'].queryset = Coordinacion.objects.filter(estado=1)
        self.fields['gerencia'].queryset = Gerencia.objects.filter(estado=1)
        self.fields['direccion'].queryset = Direccion.objects.filter(estado=1)

class UserAreasInline(admin.StackedInline):
    model = UserAreas
    form = UserAreasInlineForm
    can_delete = False
    verbose_name_plural = 'Asignación de Áreas'
    max_num = 1
    
    def has_add_permission(self, request, obj=None):
        """Oculta el botón de añadir si el usuario es encargado"""
        if obj and self.is_user_in_charge(obj):
            return False
        return True
    
    def has_change_permission(self, request, obj=None):
        """Oculta el inline si el usuario es encargado"""
        if obj and self.is_user_in_charge(obj):
            return False
        return True
    
    def is_user_in_charge(self, user):
        """Verifica si el usuario es encargado de alguna área"""
        return (Direccion.objects.filter(id_director=user).exists() or
                Gerencia.objects.filter(id_gerente=user).exists() or
                Coordinacion.objects.filter(id_coordinador=user).exists())

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    inlines = (UserAreasInline,)
    list_display = ('username', 'get_nombre_completo', 'get_coordinacion', 'get_gerencia', 'get_direccion')

    def get_inline_instances(self, request, obj=None):
        """Oculta el inline si el usuario es encargado"""
        if obj and self.is_user_in_charge(obj):
            return []
        return super().get_inline_instances(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Añade mensaje informativo para usuarios encargados"""
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)

        if obj and self.is_user_in_charge(obj):
            messages.info(request, f'Este usuario es {self.get_user_charge_info(obj)}, por lo que no necesita asignación adicional de áreas.')

        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """Elimina asignación de áreas si se convierte en encargado"""
        set_changed_by(request.user)
        super().save_model(request, obj, form, change)

        # Si el usuario es encargado, eliminar UserAreas
        if self.is_user_in_charge(obj):
            UserAreas.objects.filter(user=obj).delete()

    def is_user_in_charge(self, user):
        """Devuelve True si el usuario es encargado de alguna área"""
        return (Direccion.objects.filter(id_director=user).exists() or
                Gerencia.objects.filter(id_gerente=user).exists() or
                Coordinacion.objects.filter(id_coordinador=user).exists())

    def get_user_charge_info(self, user):
        """Devuelve en qué área es encargado el usuario"""
        if direccion := Direccion.objects.filter(id_director=user).first():
            return f"Director de {direccion.nombre}"
        if gerencia := Gerencia.objects.filter(id_gerente=user).first():
            return f"Gerente de {gerencia.nombre}"
        if coordinacion := Coordinacion.objects.filter(id_coordinador=user).first():
            return f"Coordinador de {coordinacion.nombre}"
        return "Sin cargo asignado"
    
    def save_related(self, request, form, formsets, change):
        """Maneja el guardado de relaciones"""
        set_changed_by(request.user)
        obj = form.instance
        
        # Si el usuario es encargado, no guardar UserAreas
        if not self.is_user_in_charge(obj):
            super().save_related(request, form, formsets, change)

    def get_nombre_completo(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    get_nombre_completo.short_description = 'Nombre'

    def get_coordinacion(self, obj):
        """Obtiene la coordinación del usuario, ya sea porque es encargado o porque pertenece a un área"""
        # Si el usuario es coordinador de alguna área
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj).first():
            return coordinacion.nombre
        # Si no es coordinador, obtener su área asignada en UserAreas
        try:
            user_area = UserAreas.objects.get(user=obj)
            return user_area.coordinacion.nombre if user_area.coordinacion else 'Sin coordinación'
        except UserAreas.DoesNotExist:
            return 'Sin coordinación'
    get_coordinacion.short_description = 'Coordinación'

    def get_gerencia(self, obj):
        """Obtiene la gerencia del usuario, ya sea porque es encargado o por su relación en UserAreas"""
        # Si el usuario es gerente de alguna gerencia
        if gerencia := Gerencia.objects.filter(id_gerente=obj).first():
            return gerencia.nombre
        # Si es coordinador, obtener la gerencia asociada a su coordinación
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj).first():
            return coordinacion.id_gerencia.nombre if coordinacion.id_gerencia else 'Sin gerencia'
        # Si no es coordinador, obtener la gerencia desde UserAreas
        try:
            user_area = UserAreas.objects.get(user=obj)
            if user_area.coordinacion and user_area.coordinacion.id_gerencia:
                return user_area.coordinacion.id_gerencia.nombre
            return user_area.gerencia.nombre if user_area.gerencia else 'Sin gerencia'
        except UserAreas.DoesNotExist:
            return 'Sin gerencia'
    get_gerencia.short_description = 'Gerencia'

    def get_direccion(self, obj):
        """Obtiene la dirección del usuario, ya sea porque es encargado o por su relación en UserAreas"""
        # Si el usuario es director de alguna dirección
        if direccion := Direccion.objects.filter(id_director=obj).first():
            return direccion.nombre
        # Si es gerente, obtener la dirección asociada a su gerencia
        if gerencia := Gerencia.objects.filter(id_gerente=obj).first():
            return gerencia.id_direccion.nombre if gerencia.id_direccion else 'Sin dirección'
        # Si es coordinador, obtener la dirección desde su gerencia
        if coordinacion := Coordinacion.objects.filter(id_coordinador=obj).first():
            if coordinacion.id_gerencia and coordinacion.id_gerencia.id_direccion:
                return coordinacion.id_gerencia.id_direccion.nombre
            elif coordinacion.id_direccion:
                return coordinacion.id_direccion.nombre
        # Si no es encargado, obtener la dirección desde UserAreas
        try:
            user_area = UserAreas.objects.get(user=obj)
            if user_area.coordinacion:
                if user_area.coordinacion.id_gerencia and user_area.coordinacion.id_gerencia.id_direccion:
                    return user_area.coordinacion.id_gerencia.id_direccion.nombre
                elif user_area.coordinacion.id_direccion:
                    return user_area.coordinacion.id_direccion.nombre
            return user_area.direccion.nombre if user_area.direccion else 'Sin dirección'
        except UserAreas.DoesNotExist:
            return 'Sin dirección'
    get_direccion.short_description = 'Dirección'

             
# Desregistramos y registramos la configuración personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

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

# Registra el modelo Coordinacion en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase CoordinacionAdmin
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

# Registra el modelo Gerencia en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase GerencoiaAdmin
admin.site.register(Gerencia, GerenciaAdmin)

class DireccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'nombreCorto', 'director', 'estado', 'created_at', 'updated_at')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'abreviatura', 'id_gerente__username')  # Agregar campos para búsqueda
    list_filter = ('created_at', 'updated_at')  # Agregar filtros laterales

    def director(self, obj):
        if obj.id_director:
            return obj.id_director.username
        else:
            return "Sin asignar"  # O cualquier otro mensaje que desees mostrar para los casos en que id_gerencia sea None

    director.short_description = 'Director'  # Nombre que se mostrará en la lista

# Registra el modelo Direccion en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase DireccionAdmin
admin.site.register(Direccion, DireccionAdmin) 


# Habiltar el ContentType en la vista Admin de Django
# class CustomContentTypeAdmin(admin.ModelAdmin):
#     # Campos que quieres mostrar en la lista de ContentType
#     list_display = ('app_label', 'model')

# # Registra el admin personalizado para ContentType
# admin.site.register(ContentType, CustomContentTypeAdmin)


# También puedes registrar el modelo Permission en la sección de autenticación y autorización
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type', 'descripcion', 'status')

    def get_queryset(self, request):
        # Filtra los permisos por app_label, en este caso, "sistemas-iai"
        return super().get_queryset(request).filter(content_type__app_label='sistemas-iai')

# Registra el modelo Permission en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase PermissionAdmin
admin.site.register(Permission, PermissionAdmin)


