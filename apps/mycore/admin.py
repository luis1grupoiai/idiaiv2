# Relacion 1 a 1
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, Coordinacion
# # Register your models here.

# admin.site.register(User)
# admin.site.register(Coordinacion)

# Opcion 2

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# from .models import UserCoordinacion, Coordinacion

# class UserProfileInline(admin.StackedInline):
#     model = UserCoordinacion
#     can_delete = False
#     verbose_name_plural = 'Coordinacion de usuario'

# class CustomUserAdmin(UserAdmin):
#     inlines = (UserProfileInline, )

# # Desregistras el UserAdmin de Django
# admin.site.unregister(User)

# # Registra tu CustomUserAdmin
# admin.site.register(User, CustomUserAdmin)
# admin.site.register(UserCoordinacion)

# # También registras el modelo Coordinacion si quieres gestionarlo desde el admin
# admin.site.register(Coordinacion)

# opcion 3
