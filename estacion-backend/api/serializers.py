from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para mostrar usuarios (READ ONLY)"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'rol', 'rol_display', 'created_at']
        read_only_fields = ['id', 'created_at', 'username', 'email', 'first_name', 'last_name']


class UsuarioCreateSerializer(serializers.Serializer):
    """Serializer para crear usuarios"""
    nombre = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=8, required=True)
    rol = serializers.ChoiceField(
        choices=['estudiante', 'profesor', 'administrativo'],
        required=False,
        default='estudiante'
    )
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        return attrs
    
    def create(self, validated_data):
        nombre = validated_data.get('nombre')
        email = validated_data.get('email')
        password = validated_data.get('password')
        rol = validated_data.get('rol', 'estudiante')
        
        # Generar username desde el email
        username = email.split('@')[0].lower()
        
        # Crear User de Django
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre
        )
        
        # Crear Usuario con rol
        usuario = Usuario.objects.create(
            user=user,
            rol=rol
        )
        
        return usuario