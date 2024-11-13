from django.db import connection
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User, Permission
from django.dispatch import receiver
from threading import local

# Usamos un almacenamiento local para capturar el usuario que realiza el cambio
_user = local()

def set_changed_by(user):
    """Establece el usuario que realiza el cambio"""
    _user.value = user

@receiver(m2m_changed, sender=User.user_permissions.through)
def log_permission_changes(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove']:
        action_type = 'agregar' if action == 'post_add' else 'eliminar'
        changed_by = getattr(_user, 'value', None)  # Obtener el usuario actual si está definido

        with connection.cursor() as cursor:
            for pk in pk_set:
                permission = Permission.objects.get(pk=pk)

                # Ejecutar la consulta SQL para insertar el cambio
                cursor.execute('''
                    INSERT INTO PermissionChangeHistory (user_id, permission_id, action, changed_fields, changed_by)
                    VALUES (%s, %s, %s, %s, %s)
                ''', [
                    instance.id,  # ID del usuario al que se le cambió el permiso
                    permission.id,  # ID del permiso
                    action_type,  # Tipo de acción ('add' o 'remove')
                    f"Permiso modificado: {permission.codename}",  # Detalle opcional
                    changed_by.id if changed_by else None  # ID del usuario que realizó el cambio
                ])
