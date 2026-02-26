from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Deposito, Usuario, Propietario, Vehiculo, 
    Ingreso, EstatusLegal, DetallesAuto, 
    ObjetoPersonal, SolicitudEdicion, Bitacora
)

# 1. Configuración de Usuario (Mantenemos lo tuyo y agregamos estatus_user)
class CustomUserAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información de la Secretaría', {'fields': ('rol', 'id_deposito', 'estatus_user', 'aPaterno_user', 'aMaterno_user', 'telefono_user')}),
    )
    list_display = ['username', 'rol', 'id_deposito', 'estatus_user', 'is_staff']
    list_filter = ['rol', 'estatus_user', 'id_deposito']

# 2. Vistas Relacionadas (Inlines) 
# Esto permite ver/editar detalles y estatus legal dentro de la misma pantalla del Vehículo
class DetallesAutoInline(admin.StackedInline):
    model = DetallesAuto
    extra = 0

class EstatusLegalInline(admin.TabularInline):
    model = EstatusLegal
    extra = 0

# 3. Personalización de los modelos principales
@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placas', 'marca', 'modelo', 'num_serie', 'estatus_actual')
    search_fields = ('placas', 'num_serie', 'propietario__nombre')
    list_filter = ('estatus_actual', 'tipo_servicio')
    inlines = [DetallesAutoInline, EstatusLegalInline]

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('folio', 'vehiculo', 'tipo_registro', 'fecha_ingreso')
    readonly_fields = ('folio',) # El sistema lo genera solo
    search_fields = ('folio', 'vehiculo__placas', 'vehiculo__num_serie')
    list_filter = ('tipo_registro', 'fecha_ingreso')

@admin.register(SolicitudEdicion)
class SolicitudEdicionAdmin(admin.ModelAdmin):
    list_display = ('usuario_solicito', 'campo_afectado', 'estatus', 'fecha_solicitud')
    readonly_fields = ('fecha_solicitud', 'fecha_aceptacion')
    list_filter = ('estatus',)

# 4. Registros finales
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Deposito)
admin.site.register(Propietario)
admin.site.register(ObjetoPersonal)
admin.site.register(Bitacora)