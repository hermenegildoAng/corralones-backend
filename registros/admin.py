from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Deposito, Usuario, Propietario, Vehiculo, 
    Ingreso, EstatusLegal, DetallesAuto, 
    ObjetoPersonal, SolicitudEdicion, Bitacora, 
    RegistroDano, Inspeccion, FotoEvidencia
)

# --- 1. CONFIGURACIÓN DE USUARIO ---
class CustomUserAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información de la Secretaría', {
            'fields': ('rol', 'id_deposito', 'estatus_user', 'aPaterno_user', 'aMaterno_user', 'telefono_user')
        }),
    )
    list_display = ['username', 'rol', 'id_deposito', 'estatus_user', 'is_staff']
    list_filter = ['rol', 'estatus_user', 'id_deposito']

# --- 2. DEFINICIÓN DE INLINES 
class DetallesAutoInline(admin.StackedInline):
    model = DetallesAuto
    can_delete = False
    verbose_name_plural = 'Detalles del Vehículo (En este Ingreso)'

class EstatusLegalInline(admin.TabularInline):
    model = EstatusLegal
    extra = 1

class RegistroDanoInline(admin.TabularInline):
    model = RegistroDano
    extra = 1

class ObjetoPersonalInline(admin.TabularInline):
    model = ObjetoPersonal
    extra = 1

class InspeccionInline(admin.StackedInline):
    model = Inspeccion
    can_delete = False

# --- 3. CONFIGURACIÓN DE MODELOS PRINCIPALES ---

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('folio', 'get_placas', 'tipo_registro', 'fecha_ingreso')
    readonly_fields = ('folio',) 
    search_fields = ('folio', 'vehiculo__placas', 'vehiculo__num_serie')
    list_filter = ('tipo_registro', 'fecha_ingreso', 'deposito' )
    
    
    inlines = [
        DetallesAutoInline, 
        EstatusLegalInline, 
        RegistroDanoInline, 
        ObjetoPersonalInline,
        InspeccionInline
    ]

   
    def get_placas(self, obj):
        return obj.vehiculo.placas
    get_placas.short_description = 'Placas'

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placas', 'marca', 'modelo', 'num_serie', 'estatus_actual')
    search_fields = ('placas', 'num_serie', 'propietario__nombre')
    list_filter = ['estatus_actual']
    

@admin.register(SolicitudEdicion)
class SolicitudEdicionAdmin(admin.ModelAdmin):
    list_display = ('usuario_solicito', 'campo_afectado', 'estatus', 'fecha_solicitud')
    readonly_fields = ('fecha_solicitud', 'fecha_aceptacion')
    list_filter = ['estatus']

# --- 4. REGISTROS RESTANTES ---
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Deposito)
admin.site.register(Propietario)
admin.site.register(Bitacora)

@admin.register(FotoEvidencia)
class FotoEvidenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingreso', 'nombre', 'estatus']
    list_filter = ['estatus']
    list_editable = ['estatus']