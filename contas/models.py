from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.validators import MaxValueValidator
from django.db import models

ADMIN_GROUP = 'Administradores'

ROLE_USER = 'usuario'
ROLE_ADMIN = 'admin'
ROLE_SUPERADMIN = 'superadmin'
ROLE_CHOICES = [
    (ROLE_USER, 'Usuário'),
    (ROLE_ADMIN, 'Admin'),
    (ROLE_SUPERADMIN, 'Superadmin'),
]

# O que um admin pode fazer pelo /admin/: moderar comentários e cuidar das
# categorias. Editar ou remover posts continua restrito ao autor e aos
# superadmins.
ADMIN_PERMISSIONS = [
    'view_post',
    'view_comment', 'change_comment', 'delete_comment',
    'view_category', 'add_category', 'change_category', 'delete_category',
]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    age = models.PositiveSmallIntegerField(
        'idade', null=True, blank=True, validators=[MaxValueValidator(120)],
    )
    fun_facts = models.TextField('curiosidades', blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @classmethod
    def for_user(cls, user):
        profile, _ = cls.objects.get_or_create(user=user)
        return profile


def role_of(user):
    if user.is_superuser:
        return ROLE_SUPERADMIN
    if user.is_staff:
        return ROLE_ADMIN
    return ROLE_USER


def admin_group():
    group, _ = Group.objects.get_or_create(name=ADMIN_GROUP)
    group.permissions.set(Permission.objects.filter(
        content_type__app_label='blog', codename__in=ADMIN_PERMISSIONS,
    ))
    return group


def set_role(user, role):
    group = admin_group()
    user.is_staff = role in (ROLE_ADMIN, ROLE_SUPERADMIN)
    user.is_superuser = role == ROLE_SUPERADMIN
    user.save(update_fields=['is_staff', 'is_superuser'])
    if role == ROLE_ADMIN:
        user.groups.add(group)
    else:
        user.groups.remove(group)
