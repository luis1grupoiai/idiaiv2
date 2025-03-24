from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserChangeForm
from .models import UserCoordinacion, Coordinacion, Gerencia, Direccion
from django.contrib.contenttypes.models import ContentType
from django import forms

class CustomUserChangeForm(UserChangeForm):
    # Define la metadata del formulario
    class Meta:
        model = User  # Especifica el modelo asociado al formulario (User en este caso)
        fields = '__all__'  # Incluye todos los campos del modelo en el formulario

    # Método que se ejecuta al inicializar una instancia del formulario
    def __init__(self, *args, **kwargs):
        # Llama al inicializador de la clase base (UserChangeForm) con los argumentos recibidos
        super().__init__(*args, **kwargs)
        
        # Filtra los permisos del usuario por app_label
        self.fields['user_permissions'].queryset = self.fields['user_permissions'].queryset.filter(content_type__app_label='sistemas-iai')

class UserProfileInline(admin.StackedInline):
    model = UserCoordinacion
    can_delete = False
    verbose_name_plural = 'Coordinacion de usuario'

# Define el administrador personalizado para el modelo User
class CustomUserAdmin(UserAdmin):
    # Usar el formulario personalizado
    form = CustomUserChangeForm

    # Agrega un enlace al perfil de usuario en línea (UserProfileInline)
    inlines = (UserProfileInline, )
    # Especifica los campos adicionales que se mostrarán en la lista de usuarios en el administrador
    list_display = ('username','first_name', 'last_name', 'get_coordinacion', 'get_gerencia', 'get_direccion', 'is_staff')

    # Define una función para obtener la coordinación del usuario
    # Define una función para obtener la coordinación del usuario
    def get_coordinacion(self, obj):
        # Busca el objeto UserCoordinacion asociado al usuario actual (obj)
        coordinacion = UserCoordinacion.objects.filter(user=obj).first()
        # Verifica si existe una coordinación y, en ese caso, devuelve el nombre de la coordinación
        # Si no hay coordinación, devuelve 'Sin coordinación'
        return coordinacion.coordinacion.nombre if coordinacion and coordinacion.coordinacion else 'Sin coordinación'
    # Personaliza cómo se mostrará el nombre de la función en la interfaz de administración de Django
    get_coordinacion.short_description = 'Coordinación'


    # Define una función para obtener la gerencia del usuario
    def get_gerencia(self, obj):
        # Busca el objeto UserCoordinacion asociado al usuario actual (obj)
        coordinacion = UserCoordinacion.objects.filter(user=obj).first()
        
        # Verifica si existe una coordinación y obtiene la gerencia asociada
        gerencia = coordinacion.coordinacion.id_gerencia if coordinacion and coordinacion.coordinacion else None
        
        # Devuelve el nombre de la gerencia si existe, de lo contrario, devuelve 'Sin gerencia'
        return gerencia.nombre if gerencia else 'Sin gerencia'

    # Personaliza cómo se mostrará el nombre de la función en la interfaz de administración de Django
    get_gerencia.short_description = 'Gerencia'


    # Define una función para obtener la dirección del usuario
    def get_direccion(self, obj):
        # Busca el objeto UserCoordinacion asociado al usuario actual (obj)
        coordinacion = UserCoordinacion.objects.filter(user=obj).first()

        # Verifica si existe la variable coordinacion y si tiene una propiedad coordinacion
        if coordinacion and coordinacion.coordinacion:
            # Obtiene la gerencia asociada a la coordinación
            gerencia = coordinacion.coordinacion.id_gerencia
            # Verifica si hay gerencia y si tiene una dirección asociada
            if gerencia and gerencia.id_direccion:
                # Devuelve el nombre de la dirección asociada a la gerencia
                return gerencia.id_direccion.nombre
            # Si no hay dirección asociada a la gerencia, verifica si hay dirección asociada directamente a la coordinación
            elif coordinacion.coordinacion.id_direccion:
                # Devuelve el nombre de la dirección asociada directamente a la coordinación
                return coordinacion.coordinacion.id_direccion.nombre

        # Si no hay coordinación o no hay dirección asociada, devuelve 'Sin dirección'
        return 'Sin dirección'

    # Personaliza cómo se mostrará el nombre de la función en la interfaz de administración de Django
    get_direccion.short_description = 'Dirección'


# Desregistra el modelo User del administrador predeterminado
admin.site.unregister(User)

# Registra el modelo User en la interfaz de administración de Django, utilizando la configuración personalizada definida en la clase CustomUserAdmin
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


