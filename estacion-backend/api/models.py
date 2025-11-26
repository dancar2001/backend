from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    """
    Modelo de Usuario vinculado a Django User
    Agrega roles y datos adicionales
    """
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('administrativo', 'Administrativo'),
    )
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='usuario_perfil'
    )
    
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='estudiante',
        help_text='Rol del usuario en el sistema'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios'
        ordering = ['-created_at']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_rol_display()})"
    
    def get_rol_display(self):
        """Retorna el rol con capitalización"""
        return dict(self.ROLES).get(self.rol, self.rol)