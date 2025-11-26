from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    
    # Autenticación JWT
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuarios
    path('crear-usuario/', views.crear_usuario_endpoint, name='crear-usuario'),
    
    # CSV
    path('guardar-datos-csv/', views.guardar_datos_csv, name='guardar-datos-csv'),
    # path('api/proxy-clima/', views.proxy_clima, name='proxy-clima'),
    
    # User profile
    path('me/', views.me, name='me'),
     #path('clima/', views.obtener_clima, name='obtener_clima'),
]

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register(r'usuarios', views.UsuarioViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
    
#     # ⭐ CLIMA
#     path('clima/', views.obtener_clima, name='obtener_clima'),
#     path('clima/guardar/', views.guardar_clima_csv, name='guardar_clima_csv'),
#     path('clima/descargar/', views.descargar_clima_csv, name='descargar_clima_csv'),
#     path('clima/leer/', views.leer_clima_csv, name='leer_clima_csv'),
    
#     # OTROS
#     path('crear-usuario/', views.crear_usuario_endpoint, name='crear_usuario'),
#     path('guardar-datos-csv/', views.guardar_datos_csv, name='guardar_datos_csv'),
#     path('me/', views.me, name='me'),
# ]