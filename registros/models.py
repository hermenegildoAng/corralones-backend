from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import datetime
import os

# --- FUNCIONES DE RUTA PARA ARCHIVOS ---

def path_evidencia_vehiculo(instance, filename):
    vin = instance.vehiculo.num_serie
    fecha = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join('vehiculos', vin, fecha, 'evidencia', filename)

def path_objetos_vehiculo(instance, filename):
    vin = instance.vehiculo.num_serie
    fecha = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join('vehiculos', vin, fecha, 'objetos', filename)

# --- MODELOS ---

class Deposito(models.Model):
    ESTATUS_CHOICES = (('ACTIVO', 'Activo'), ('SUSPENDIDO', 'Suspendido'), ('PAUSADO', 'Pausado'))
    nombre = models.CharField(max_length=200)
    ubicacion = models.TextField()
    concesionario_responsable = models.CharField(max_length=200)
    estatus_deposito = models.CharField(max_length=30, choices=ESTATUS_CHOICES, default='ACTIVO')
    
    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    ROLES = (('SUPER', 'Super Usuario Secretaría'), ('ADMIN', 'Administrador SMyT'), ('OPERADOR', 'Usuario Concesionario'))
    rol = models.CharField(max_length=10, choices=ROLES, default='SUPER')
    id_deposito = models.ForeignKey(Deposito, on_delete=models.SET_NULL, null=True, blank=True)
    aPaterno_user = models.CharField(max_length=50, verbose_name="Apellido Paterno")
    aMaterno_user = models.CharField(max_length=50, verbose_name="Apellido Materno")
    telefono_user = models.CharField(max_length=20, blank=True)
    estatus_user = models.CharField(max_length=10, choices=(('ACTIVO', 'Activo'), ('SUSPENDIDO', 'Suspendido')), default='ACTIVO')

class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    apaterno = models.CharField(max_length=100)
    amaterno = models.CharField(max_length=100)
    correo = models.EmailField(null=True, blank=True)
    identificacion = models.CharField(max_length=50) 
    telefono = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.nombre} {self.apaterno}"

class Vehiculo(models.Model):
    TIPO_SERVICIO_CHOICES = (('PARTICULAR', 'Particular'), ('PUBLICO', 'Público'), ('ESPECIALIZADO', 'Especializado'))
    ESTATUS_VEHICULO = (('DENTRO', 'En Depósito'), ('LIBERADO', 'Fuera / Entregado'), ('TRANSFERIDO', 'Transferido'))
    
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    anio = models.IntegerField()
    color_original = models.CharField(max_length=50)
    color_actual = models.CharField(max_length=50)
    num_serie = models.CharField(max_length=50, unique=True) 
    placas = models.CharField(max_length=20)
    numero_motor = models.CharField(max_length=50)
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES)
    tipo_vehiculo = models.CharField(max_length=50) 
    propietario = models.ForeignKey(Propietario, on_delete=models.SET_NULL, null=True)
    estatus_actual = models.CharField(max_length=20, choices=ESTATUS_VEHICULO, default='DENTRO')

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placas}"

class Ingreso(models.Model):
    TIPO_REGISTRO_CHOICES = (('NUEVO', 'Ingreso Ordinario'), ('INVENTARIO', 'Carga de Inventario'))
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    tipo_registro = models.CharField(max_length=20, choices=TIPO_REGISTRO_CHOICES, default='NUEVO')
    folio = models.CharField(max_length=50, unique=True, blank=True) # IMPORTANTE: blank=True para el save()
    autoridad_ingreso = models.CharField(max_length=200)
    presencia_factura = models.BooleanField(default=False)
    factura_original = models.FileField(upload_to='facturas/%Y/%m/%d/', null=True, blank=True)
    lugar_siniestro = models.TextField()
    motivo_ingreso = models.TextField()
    fecha_ingreso = models.DateTimeField() # Editable para inventario viejo

    def save(self, *args, **kwargs):
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
        
        # Al ingresar, el vehículo pasa a estar DENTRO automáticamente
        self.vehiculo.estatus_actual = 'DENTRO'
        self.vehiculo.save()
        super().save(*args, **kwargs)

class EstatusLegal(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='historial_legal')
    condicion_juridica = models.CharField(max_length=200)
    num_oficio = models.CharField(max_length=100)
    documento_oficio = models.FileField(upload_to='oficios/%Y/%m/%d/')
    fecha_oficio = models.DateField()
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-fecha_registro']

class DetallesAuto(models.Model):
    ESTADO_CHOICES = (('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo'), ('DAÑADO', 'Dañado'))
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='historial_detalles')
    
    # Exterior e Interior
    estatus_carroceria = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    estatus_cristales = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    estatus_espejos = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    cant_llantas_delanteras = models.PositiveIntegerField(default=2)
    cant_llantas_traseras = models.PositiveIntegerField(default=2)
    estado_asientos = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    
    # Mecánica y Odómetro
    estado_motor = models.CharField(max_length=20, choices=ESTADO_CHOICES)
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
    
    # Fotos Dinámicas
    evidencia_foto_frontal = models.ImageField(upload_to=path_evidencia_vehiculo, null=True, blank=True)
    evidencia_foto_lateral_izquierda = models.ImageField(upload_to=path_evidencia_vehiculo, null=True, blank=True)
    evidencia_foto_lateral_derecha = models.ImageField(upload_to=path_evidencia_vehiculo, null=True, blank=True)
    evidencia_foto_interior = models.ImageField(upload_to=path_evidencia_vehiculo, null=True, blank=True)
    evidencia_foto_capo = models.ImageField(upload_to=path_evidencia_vehiculo, null=True, blank=True)
    
    observaciones_detalladas = models.TextField(blank=True, null=True)

class ObjetoPersonal(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='objetos_encontrados')
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    estado_objeto = models.CharField(max_length=20, choices=(('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('MALO', 'Malo')), default='BUENO')
    foto_objeto = models.ImageField(upload_to=path_objetos_vehiculo, null=True, blank=True)
    
    
    
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
    justificacion = models.TextField()
    registro_id = models.IntegerField() # ID del vehículo o ingreso afectado
    campo_afectado = models.CharField(max_length=100)
    valor_viejo = models.TextField()
    valor_nuevo = models.TextField()
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True) 
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)
    
    
# --- BITÁCORA Y SEGURIDAD

class Bitacora(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tipo_evento = models.CharField(max_length=100) 
    fecha_evento = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

class HashVehiculo(models.Model):
    vehiculo = models.OneToOneField(Vehiculo, on_delete=models.CASCADE)
    numero_hash = models.CharField(max_length=255)