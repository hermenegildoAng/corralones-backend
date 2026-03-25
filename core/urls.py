from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
  # ← ajusta 'registros' al nombre real de tu app Django
# Asegúrate de importar tus views correctamente
# QUITA crear_ingreso_completo de aquí:
from registros.views import (
    MyTokenObtainPairView,
    DepositoViewSet, UsuarioViewSet, VehiculoViewSet, 
    IngresoViewSet, PropietarioViewSet, DetallesAutoViewSet,
    ObjetoPersonalViewSet, RegistroDanoViewSet, InspeccionViewSet,
    SolicitudEdicionViewSet, BitacoraViewSet       
)
from registros.views import buscar_cp , servir_pdf 


# Importamos directamente todo desde views
from registros import views 

# 1. Definimos el router UNA SOLA VEZ (Solo para ViewSets)
router = DefaultRouter()
router.register(r'depositos', views.DepositoViewSet, basename='depositos')
router.register(r'usuarios', views.UsuarioViewSet, basename='usuarios')
router.register(r'vehiculos', views.VehiculoViewSet, basename='vehiculos')
router.register(r'ingresos', views.IngresoViewSet, basename='ingresos')
router.register(r'propietarios', views.PropietarioViewSet, basename='propietarios')
router.register(r'detalles-auto', views.DetallesAutoViewSet, basename='detalles-auto')
router.register(r'objetos-personales', views.ObjetoPersonalViewSet, basename='objetos')
router.register(r'danos', views.RegistroDanoViewSet, basename='danos')
router.register(r'inspecciones', views.InspeccionViewSet, basename='inspecciones')
router.register(r'solicitudes-edicion', views.SolicitudEdicionViewSet, basename='solicitudes') # El del Admin
router.register(r'bitacora', views.BitacoraViewSet, basename='bitacora')
router.register(r'fotos', views.FotoEvidenciaViewSet)

# 🚨 Fíjate que AQUÍ YA NO ESTÁ el crear-solicitud-cambio. Lo pasamos abajo 👇


# 2. Definimos los urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- RUTA DEL OPERADOR PARA CREAR EDICIONES (Va fuera del router) ---
    path('api/ingresos/crear-solicitud-cambio/', views.Crear_solicitud_cambio, name='crear_solicitud_cambio'),
    
    # Aquí se incluyen todas las rutas registradas arriba (usuarios, depositos, etc.)
    path('api/', include(router.urls)),
    
    # Autenticación
    path('api/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Documentación
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Reset de contraseña
    path('api/password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('api/fotos/<int:foto_id>/revisar/', views.revisar_foto),

    path('api/cp/<str:cp>/', buscar_cp, name='buscar_cp'),
    # urls.py
    path('media/pdf/<path:ruta>', servir_pdf, name='servir_pdf'),
    

]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)