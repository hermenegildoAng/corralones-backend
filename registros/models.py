from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import datetime
import os
import uuid
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

# --- FUNCIONES DE RUTA PARA ARCHIVOS ---
class CodigoPostal(models.Model):
    cp = models.CharField(max_length=5, db_index=True)  # 🔥 índice
    estado = models.CharField(max_length=210)
    municipio = models.CharField(max_length=210)
    colonias = models.CharField(max_length=150)
    def __str__(self):
        return f"{self.cp} - {self.municipio}, {self.estado}"


def ruta_fotos_evidencia(instance, filename):
    vehiculo_id = instance.ingreso.vehiculo.placas or instance.ingreso.vehiculo.num_serie or f"ID_{instance.ingreso.vehiculo.id}"
    fecha = instance.ingreso.fecha_ingreso.strftime('%Y-%m-%d')
    return f'vehiculos/{vehiculo_id}/ingreso_{fecha}/fotos_evidencia/{filename}'

def ruta_fotos_danos(instance, filename):
    vehiculo_id = instance.ingreso.vehiculo.placas or instance.ingreso.vehiculo.num_serie or f"ID_{instance.ingreso.vehiculo.id}"
    fecha = instance.ingreso.fecha_ingreso.strftime('%Y-%m-%d')
    return f'vehiculos/{vehiculo_id}/ingreso_{fecha}/fotos_danos/{filename}'

def ruta_fotos_objetos(instance, filename):
    vehiculo_id = instance.ingreso.vehiculo.placas or instance.ingreso.vehiculo.num_serie or f"ID_{instance.ingreso.vehiculo.id}"
    fecha = instance.ingreso.fecha_ingreso.strftime('%Y-%m-%d')
    return f'vehiculos/{vehiculo_id}/ingreso_{fecha}/fotos_objetos/{filename}'

def ruta_documentos(instance, filename):
    # Como los documentos pueden venir del Ingreso o del EstatusLegal, lo validamos:
    ingreso = getattr(instance, 'ingreso', None) or instance
    vehiculo_id = ingreso.vehiculo.placas or ingreso.vehiculo.num_serie or f"ID_{ingreso.vehiculo.id}"
    fecha = ingreso.fecha_ingreso.strftime('%Y-%m-%d')
    return f'vehiculos/{vehiculo_id}/ingreso_{fecha}/documentos/{filename}'

def ruta_solicitudes_temporales(instance, filename):
    # Las fotos que sube el operador y están esperando aprobación se van a una carpeta temporal
    return f'solicitudes_pendientes/{now().strftime("%Y-%m")}/{filename}'

# --- MODELOS ---

class Deposito(models.Model):
    ESTATUS_CHOICES = (
        ('ACTIVO', 'Activo'), 
        ('SUSPENDIDO', 'Suspendido'), 
        ('PAUSADO', 'Pausado')
    )

    # Identificación
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Corralón")
    
    # Dirección Desglosada (Para que coincida con tu frontend)
    calle = models.CharField(max_length=255)
    colonia = models.CharField(max_length=150)
    cp = models.CharField(max_length=5, verbose_name="Código Postal")
    municipio = models.CharField(max_length=150)
    estado = models.CharField(max_length=100)
    
    # Campo calculado o resumen (opcional, podrías eliminarlo si usas los de arriba)
    ubicacion_completa = models.TextField(blank=True, null=True)

    # Contacto
    telefono = models.CharField(max_length=10)
    correo = models.EmailField()
    
    # Operación
    estatus_deposito = models.CharField(
        max_length=30, 
        choices=ESTATUS_CHOICES, 
        default='ACTIVO'
    )
    
    # Auditoría básica
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"
        ordering = ['-creado_el']

    def __str__(self):
        return f"{self.nombre} - {self.municipio}"

    def save(self, *args, **kwargs):
        # Opcional: Auto-generar la ubicación completa antes de guardar
        self.ubicacion_completa = f"{self.calle}, Col. {self.colonia}, {self.cp}, {self.municipio}, {self.estado}"
        super().save(*args, **kwargs)


class Usuario(AbstractUser):
    ROLES = (('SUPER', 'Super Usuario Secretaría'), ('ADMIN', 'Administrador SMyT'), ('OPERADOR', 'Usuario Concesionario'))
    rol = models.CharField(max_length=10, choices=ROLES, default='SUPER')
    id_deposito = models.ForeignKey(Deposito, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_user = models.CharField(max_length=100, verbose_name="Nombre(s)")
    aPaterno_user = models.CharField(max_length=50, verbose_name="Apellido Paterno")
    aMaterno_user = models.CharField(max_length=50, verbose_name="Apellido Materno")
    email = models.EmailField(unique=True , null=True, blank=True)
    telefono_user = models.CharField(max_length=20, blank=True)
    estatus_user = models.CharField(max_length=10, choices=(('ACTIVO', 'Activo'), ('SUSPENDIDO', 'Suspendido')), default='ACTIVO')

class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    apaterno = models.CharField(max_length=100)
    amaterno = models.CharField(max_length=100)
    correo = models.EmailField(null=True, blank=True)
    identificacion = models.CharField(max_length=50) 
    telefono = models.CharField(max_length=20)
    direccion = models.TextField("Dirección completa", blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apaterno}"

class Vehiculo(models.Model):
   
    ESTATUS_VEHICULO = (('DENTRO', 'En Depósito'), ('LIBERADO', 'Fuera / Entregado'), ('TRANSFERIDO', 'Transferido'))
    
    marca = models.CharField(max_length=100)
    submarca = models.CharField(max_length=100, blank=True, null=True) 
    modelo = models.CharField(max_length=100)
    anio = models.IntegerField()
    color_original = models.CharField(max_length=50)
    color_actual = models.CharField(max_length=50)
    num_serie = models.CharField(max_length=50, unique=True) 
    placas = models.CharField(max_length=20)
    numero_motor = models.CharField(max_length=50)
    repuve = models.CharField(max_length=50, blank=True, null=True)
    
    tipo_vehiculo = models.CharField(max_length=50) 
    propietario = models.ForeignKey(
        'Propietario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='vehiculos'
    )
    estatus_actual = models.CharField(max_length=20, choices=ESTATUS_VEHICULO, default='LIBERADO')

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placas}"

class Ingreso(models.Model):
    TIPO_REGISTRO_CHOICES = (('NUEVO', 'Ingreso Ordinario'), ('INVENTARIO', 'Carga de Inventario'))
    TIPO_SERVICIO_CHOICES = (('PARTICULAR', 'Particular'), ('PUBLICO', 'Público'), ('ESPECIALIZADO', 'Especializado'))
    
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    deposito = models.ForeignKey('Deposito', on_delete=models.PROTECT, related_name='ingresos_aqui')
    tipo_registro = models.CharField(max_length=20, choices=TIPO_REGISTRO_CHOICES, default='NUEVO')
    folio = models.CharField(max_length=50, unique=True, blank=True)
    autoridad_ingreso = models.CharField(max_length=200)
    presencia_factura = models.BooleanField(default=False)  
    factura_original = models.FileField(upload_to=ruta_documentos, null=True, blank=True)
    lugar_siniestro = models.TextField()
    motivo_ingreso = models.TextField()
    fecha_ingreso = models.DateTimeField() 

    # En Ingreso.save()
    # En registros/models.py dentro de class Ingreso:

    def save(self, *args, **kwargs):
    # Solo generamos folio si no tiene uno
        if not self.folio:
            anio = datetime.date.today().year
            ultimo_ingreso = Ingreso.objects.filter(folio__contains=f"-{anio}-").order_by('id').last()
            
            if ultimo_ingreso:
                ultimo_numero = int(ultimo_ingreso.folio.split('-')[-1])
                nuevo_numero = str(ultimo_numero + 1).zfill(4)
            else:
                nuevo_numero = '0001'
                
            prefijo = 'SMyT' if self.tipo_registro == 'NUEVO' else 'INV'
            self.folio = f"{prefijo}-{anio}-{nuevo_numero}"
        
            super().save(*args, **kwargs)
        
            if self.vehiculo:
                self.vehiculo.estatus_actual = 'DENTRO'
                # Usamos update_fields para que sea más eficiente y no dispare otros procesos innecesarios
                self.vehiculo.save(update_fields=['estatus_actual'])
           
        
    @property
    def expediente_multimedia_completo(self):
        """
        Verifica si este ingreso específico ya tiene fotos de daños 
        o si el operador marcó que el auto venía impecable.
        """
        tiene_fotos = self.danos.exists() 
        vuelve_limpio = getattr(self.historial_detalles, 'vehiculo_sin_danos', False)
        
        return tiene_fotos or vuelve_limpio

class EstatusLegal(models.Model):
    ingreso = models.ForeignKey(
        'Ingreso', 
        on_delete=models.CASCADE, 
        related_name='estatus_legales' # Plural para que tenga sentido
    )
    
    condicion_juridica = models.CharField(max_length=200)
    num_oficio = models.CharField(max_length=100)
    documento_oficio = models.FileField(upload_to=ruta_documentos)
    fecha_oficio = models.DateField()
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) 

    class Meta:
        verbose_name_plural = "Estatus Legales"
        ordering = ['-fecha_registro']

class DetallesAuto(models.Model):
    ESTADO_CHOICES = (('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo'), ('DAÑADO', 'Dañado'))
    ingreso = models.OneToOneField('Ingreso', on_delete=models.CASCADE, related_name='historial_detalles')
    
    
    # Exterior 
    # e Interior
    estatus_carroceria = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    estatus_cristales = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    estatus_espejos = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    cant_llantas_delanteras = models.PositiveIntegerField(default=2)
    cant_llantas_traseras = models.PositiveIntegerField(default=2)
    estado_asientos = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    
    vehiculo_sin_danos = models.BooleanField("¿El vehículo no presenta daños?", default=False)
    
    # Mecánica y Odómetro
    estado_motor = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    cilindros = models.PositiveIntegerField(null=True, blank=True)
    cantidad_asientos = models.PositiveIntegerField(null=True, blank=True)
    tipo_combustible = models.CharField(max_length=50, null=True, blank=True)
    presencia_bateria = models.BooleanField(default=True)
    tipo_transmision = models.CharField(max_length=20, choices=(('MANUAL', 'Manual'), ('AUTOMATICA', 'Automática'), ('SEMIAUTOMATICA', 'Semiautomática')))
    estatus_odometro = models.CharField(max_length=20, choices=(('FUNCIONAL', 'Funcional'), ('ROTO', 'Roto'), ('SIN_PANTALLA', 'Sin pantalla'), ('ILEGIBLE', 'Ilegible')), default='FUNCIONAL')
    kilometraje_odometro = models.PositiveIntegerField(null=True, blank=True)
    
    # Líquidos
    NIVEL_CHOICES = (('LLENO', 'Lleno'), ('MEDIO', 'Medio'), ('BAJO', 'Bajo'), ('VACIO', 'Vacío'))
    estatus_aceite_motor = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    estatus_anticongelante = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    estatus_combustible = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    estatus_bolsas_aire = models.CharField(max_length=20, default='INTACTAS')
    
   
    
    observaciones_detalladas = models.TextField(blank=True, null=True)

class ObjetoPersonal(models.Model):
    ingreso = models.ForeignKey(
        'Ingreso', 
        on_delete=models.CASCADE, 
        related_name='objetos_encontrados'
    )
    
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    estado_objeto = models.CharField(max_length=20, choices=(('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')), default='BUENO')
    foto_objeto = models.ImageField(upload_to=ruta_fotos_objetos, null=True, blank=True)
    
    
    
class SolicitudEdicion(models.Model):
    ESTATUS_CHOICES = (
        ('PENDIENTE', 'Pendiente'), 
        ('ACEPTADA', 'Aceptada'), 
        ('RECHAZADA', 'Rechazada')
    )
    
    usuario_solicito = models.ForeignKey(
        settings.AUTH_USER_MODEL,   
        on_delete=models.CASCADE, 
        related_name='solicitudes_creadas'
    )
    usuario_acepto = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes_revisadas'
    )
    
    tabla_destino = models.CharField(max_length=50, null=True, blank=True)
    
    justificacion = models.TextField()
    registro_id = models.IntegerField() 
    campo_afectado = models.CharField(max_length=100)
    valor_viejo = models.TextField()
    valor_nuevo = models.TextField()
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='PENDIENTE')
    
    # NUEvos
    evidencia_solicitud = models.ImageField(upload_to=ruta_solicitudes_temporales, null=True, blank=True)
    motivo_rechazo = models.TextField(null=True, blank=True)
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True) 
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.campo_afectado} ({self.estatus})"
    
    
class RegistroDano(models.Model):
    ingreso = models.ForeignKey('Ingreso', on_delete=models.CASCADE, related_name='danos')
    
    parte_vehiculo = models.CharField("Parte afectada", max_length=100, help_text="Ej: Defensa delantera, Parabrisas")
    descripcion = models.TextField("Descripción del daño")
    foto_evidencia = models.ImageField(upload_to=ruta_fotos_danos, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Daño en {self.parte_vehiculo} - {self.ingreso.vehiculo.num_serie}"




class Inspeccion(models.Model):
    
    RESULTADOS = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado (Requiere Corrección)'),
        ('OBSERVADO', 'Aprobado con Observaciones'),
    ]

    ingreso = models.ForeignKey('Ingreso', on_delete=models.CASCADE, related_name='inspeccion')
    administrador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='inspecciones_realizadas'
    )
    fecha_revision = models.DateTimeField(auto_now_add=True)

    # El "Semáforo" de control
    identificacion_ok = models.BooleanField("Datos ID (Placas/VIN) correctos", default=True)
    inventario_ok = models.BooleanField("Inventario físico verificado", default=True)
    estado_fisico_ok = models.BooleanField("Daños físicos validados con fotos", default=True)
    documentacion_ok = models.BooleanField("Documentación legible", default=True)

    # Veredicto final
    resultado = models.CharField(max_length=20, choices=RESULTADOS, default='APROBADO')
    observaciones_admin = models.TextField("Comentarios del Administrador", blank=True)

    class Meta:
        verbose_name = "Inspección Administrativa"
        verbose_name_plural = "Inspecciones Administrativas"

    def __str__(self):
        return f"Inspección {self.ingreso.folio} - {self.resultado}"
    

class Liberacion(models.Model):
    ingreso = models.OneToOneField(Ingreso, on_delete=models.CASCADE, related_name='liberacion')
    fecha_salida = models.DateTimeField(auto_now_add=True)
    quien_recibe = models.CharField("Nombre de quien retira", max_length=200)
    identificacion_recibe = models.CharField("Identificación (INE/Licencia)", max_length=100)
    autoridad_autoriza = models.CharField("Autoridad que liberó", max_length=150)
    numero_oficio_liberacion = models.CharField("No. de Oficio", max_length=100)
    observaciones_salida = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Al liberar, el vehículo debe cambiar su estatus a 'FUERA' automáticamente
        super().save(*args, **kwargs)
        vehiculo = self.ingreso.vehiculo
        vehiculo.estatus_actual = 'FUERA'
        vehiculo.save()

    def __str__(self):
        return f"Liberación de Folio: {self.ingreso.folio}"
    
    
class FotoEvidencia(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, related_name='fotos_evidencia')
    nombre = models.CharField(max_length=150, help_text="Ej: Frontal, Lateral Izquierdo, Llanta extra...")
    foto = models.ImageField(upload_to=ruta_fotos_evidencia)
    fecha_subida = models.DateTimeField(auto_now_add=True)  
    justificacion = models.TextField(blank=True, null=True)
    es_solicitud = models.BooleanField(default=False)
    
    ESTATUS_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    )
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='ACEPTADA')
    motivo_rechazo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - Ingreso {self.ingreso.folio}"
    
# --- BITÁCORA Y SEGURIDAD

class Bitacora(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tipo_evento = models.CharField(max_length=100) 
    fecha_evento = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

class HashVehiculo(models.Model):
    vehiculo = models.OneToOneField(Vehiculo, on_delete=models.CASCADE)
    numero_hash = models.CharField(max_length=255)