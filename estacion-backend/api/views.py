import csv
import requests
import os
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Usuario
from .serializers import UsuarioSerializer


# ============================================================================
# AUTENTICACIÓN - LOGIN CON EMAIL O USERNAME
# ============================================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Permite login con email o username"""
    
    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')
        
        # Intentar buscar por email
        try:
            user = User.objects.get(email=username_or_email)
            attrs['username'] = user.username
        except User.DoesNotExist:
            pass
        
        return super().validate(attrs)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint de login que acepta email o username"""
    serializer_class = CustomTokenObtainPairSerializer


# ============================================================================
# FUNCIÓN AUXILIAR
# ============================================================================

def get_user_rol(user):
    """Obtiene el rol del usuario"""
    if user.is_superuser:
        return 'administrativo'
    try:
        usuario = Usuario.objects.get(user=user)
        return usuario.rol
    except Usuario.DoesNotExist:
        return 'estudiante'


# ============================================================================
# USUARIOS
# ============================================================================

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """API para ver usuarios"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        rol = get_user_rol(self.request.user)
        
        if rol == 'estudiante':
            return Usuario.objects.filter(user=self.request.user)
        elif rol == 'profesor':
            return Usuario.objects.filter(rol='estudiante')
        return Usuario.objects.all()
    
    def destroy(self, request, pk=None):
        """Elimina un usuario (solo para administrativos)"""
        rol = get_user_rol(request.user)
        if rol != 'administrativo':
            return Response(
                {'error': 'Solo administradores pueden eliminar usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            usuario = self.get_object()
            user = usuario.user
            
            if user.is_superuser:
                return Response(
                    {'error': 'No se puede eliminar un superusuario'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            nombre = user.first_name or user.username
            usuario.delete()
            user.delete()
            
            return Response({
                'success': True,
                'mensaje': f'✅ {nombre} eliminado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# ⭐ CLIMA - ENDPOINTS
# ============================================================================

# ❌ COMENTADO - Endpoint ngrok expirado
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def obtener_clima(request):
#     """
#     Obtiene datos del clima desde el endpoint externo
#     
#     GET /api/clima/
#     
#     Retorna los datos sin problemas de CORS
#     """
#     try:
#         print('🔄 Consumiendo endpoint clima...')
#         
#         response = requests.get(
#             'https://86b6d4e6c656.ngrok-free.app/api_clima.php',
#             timeout=10,
#             headers={'Accept': 'application/json'}
#         )
#         
#         response.raise_for_status()
#         datos = response.json()
#         
#         print(f'✅ Datos recibidos: {len(datos)} registros')
#         return Response(datos, status=status.HTTP_200_OK)
#         
#     except Exception as e:
#         print(f'❌ Error: {str(e)}')
#         return Response(
#             {'error': f'Error al obtener datos: {str(e)}'},
#             status=status.HTTP_502_BAD_GATEWAY
#         )


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def guardar_clima_csv(request):
#     """
#     Guarda los datos de clima en un archivo CSV en el servidor
    
#     POST /api/clima/guardar/
#     {
#         "datos": [
#             {
#                 "id": "2933",
#                 "temperatura": "28.9",
#                 "humedad": "63",
#                 "lluvia": "0",
#                 "uv": "28.08",
#                 "fecha": "2025-11-20 21:15:07"
#             },
#             ...
#         ]
#     }
    
#     Retorna:
#     {
#         "success": true,
#         "message": "50 registros guardados",
#         "file": "/ruta/al/datos_clima.csv"
#     }
#     """
#     try:
#         data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
#         datos = data.get('datos', [])

#         if not datos:
#             return Response(
#                 {'success': False, 'error': 'No hay datos para guardar'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Ruta del archivo CSV
#         csv_path = os.path.join(settings.BASE_DIR, 'datos_clima.csv')
        
#         print(f'📝 Guardando en: {csv_path}')

#         # Verificar si el archivo existe
#         file_exists = os.path.exists(csv_path)

#         with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
#             fieldnames = ['id', 'temperatura', 'humedad', 'lluvia', 'uv', 'fecha']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#             # Si es nuevo archivo, escribe encabezados
#             if not file_exists:
#                 writer.writeheader()
#                 print('✅ Creando nuevo archivo CSV con encabezados')

#             # Escribe cada fila
#             for row in datos:
#                 writer.writerow({
#                     'id': row.get('id', ''),
#                     'temperatura': row.get('temperatura', ''),
#                     'humedad': row.get('humedad', ''),
#                     'lluvia': row.get('lluvia', ''),
#                     'uv': row.get('uv', ''),
#                     'fecha': row.get('fecha', '')
#                 })

#         print(f'✅ {len(datos)} registros guardados en {csv_path}')
#         return Response({
#             'success': True,
#             'message': f'{len(datos)} registros guardados',
#             'file': csv_path
#         }, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         print(f'❌ Error guardando CSV: {str(e)}')
#         return Response(
#             {'success': False, 'error': str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def descargar_clima_csv(request):
#     """
#     Descarga el archivo CSV de clima
    
#     GET /api/clima/descargar/
    
#     Retorna el archivo CSV para descargar
#     """
#     try:
#         csv_path = os.path.join(settings.BASE_DIR, 'datos_clima.csv')

#         if not os.path.exists(csv_path):
#             return Response(
#                 {'error': 'El archivo no existe aún'},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Retorna el archivo para descargar
#         response = FileResponse(
#             open(csv_path, 'rb'),
#             as_attachment=True,
#             filename='datos_clima.csv'
#         )
#         response['Content-Type'] = 'text/csv'
        
#         print('✅ Descargando CSV')
#         return response

#     except Exception as e:
#         print(f'❌ Error descargando CSV: {str(e)}')
#         return Response(
#             {'error': str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def leer_clima_csv(request):
#     """
#     Lee el contenido del archivo CSV de clima
    
#     GET /api/clima/leer/
    
#     Retorna los datos en JSON
#     """
#     try:
#         csv_path = os.path.join(settings.BASE_DIR, 'datos_clima.csv')

#         if not os.path.exists(csv_path):
#             return Response(
#                 {'error': 'El archivo no existe aún', 'datos': []},
#                 status=status.HTTP_200_OK
#             )

#         datos = []
#         with open(csv_path, 'r', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 datos.append(row)

#         print(f'✅ Leyendo CSV: {len(datos)} registros')
#         return Response({
#             'success': True,
#             'total': len(datos),
#             'datos': datos
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f'❌ Error leyendo CSV: {str(e)}')
#         return Response(
#             {'error': str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


# ============================================================================
# OTROS ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_usuario_endpoint(request):
    """Crea un nuevo usuario (solo para admin)"""
    rol = get_user_rol(request.user)
    if rol != 'administrativo':
        return Response(
            {'error': 'Solo administradores pueden crear usuarios'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        nombre = request.data.get('nombre', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        rol_usuario = request.data.get('rol', 'estudiante').strip()
        
        username = email.split('@')[0].lower()
        
        if not nombre or not email or not password:
            return Response(
                {'error': 'Faltan campos: nombre, email, password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'La contraseña debe tener mínimo 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'El email ya existe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre
        )
        
        usuario = Usuario.objects.create(
            user=user,
            rol=rol_usuario
        )
        
        return Response({
            'id': usuario.id,
            'username': user.username,
            'email': user.email,
            'nombre': user.first_name,
            'rol': usuario.rol,
            'rol_display': usuario.get_rol_display(),
            'mensaje': '✅ Usuario creado'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_datos_csv(request):
    """
    Guarda datos en el CSV de cultivos
    """
    rol = get_user_rol(request.user)
    if rol not in ['profesor', 'administrativo']:
        return Response(
            {'error': 'No tienes permiso'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        datos = request.data
        guardar_en_csv(datos)
        
        return Response({
            'success': True,
            'mensaje': '✅ Datos guardados en CSV'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


def guardar_en_csv(datos):
    """Guarda los datos en el CSV de cultivos"""
    try:
        csv_path = Path(settings.BASE_DIR) / 'cultivos_viabilidad_FINAL.csv'
        
        fila = {
            'date': datos.get('fecha'),
            'temperatura': datos.get('temperatura'),
            'radiacion_solar': datos.get('radiacion_solar'),
            'humedad_suelo': datos.get('humedad_suelo'),
            'humedad': datos.get('humedad'),
            'precipitacion': datos.get('precipitacion'),
            'tomate': datos.get('tomate', 'No'),
            'banana': datos.get('banana', 'No'),
            'cacao': datos.get('cacao', 'No'),
            'arroz': datos.get('arroz', 'No'),
            'maiz': datos.get('maiz', 'No'),
        }
        
        fieldnames = ['date', 'temperatura', 'radiacion_solar', 'humedad_suelo', 
                      'humedad', 'precipitacion', 'tomate', 'banana', 'cacao', 'arroz', 'maiz']
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(fila)
            
    except Exception as e:
        print(f"Error guardando CSV: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Obtiene información del usuario autenticado"""
    user = request.user
    
    if user.is_superuser:
        rol = 'administrativo'
        rol_display = 'Administrativo'
    else:
        try:
            usuario = Usuario.objects.get(user=user)
            rol = usuario.rol
            rol_display = usuario.get_rol_display()
        except Usuario.DoesNotExist:
            rol = 'estudiante'
            rol_display = 'Estudiante'
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name or user.username,
        'last_name': user.last_name or '',
        'rol': rol,
        'rol_display': rol_display,
    })