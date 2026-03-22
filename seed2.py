import os
import django
from django.utils.timezone import now
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from registros.models import (
    Deposito, Usuario, Propietario, Vehiculo, 
    Ingreso, DetallesAuto, RegistroDano , Inspeccion , SolicitudEdicion
)

def seed_maestro():
    print("🚀 Iniciando Carga Maestra de Datos...")

    # 1. DEPÓSITOS
    depositos_data = [
        {'nombre': "Corralón Norte - Apizaco", 'ubicacion': 'Salida Apizaco Km 2'},
        {'nombre': "Corralón Sur - Zacatelco", 'ubicacion': 'Carr. Federal Puebla-Tlax'},
        {'nombre': "Depósito Central - Tlaxcala", 'ubicacion': 'Centro Capital'},
    ]

    deps = []
    for d in depositos_data:
        obj, _ = Deposito.objects.get_or_create(
            nombre=d['nombre'],
            defaults={'ubicacion': d['ubicacion']}
        )
        deps.append(obj)

    # 2. USUARIOS
    if not Usuario.objects.filter(username="super_root").exists():
        Usuario.objects.create_superuser(
            username="super_root", 
            email="admin@gobierno.gob.mx", 
            password="adminpass", 
            rol='SUPER', 
            nombre_user='Admin',
            aPaterno_user='General'
        )
    
    usuarios_data = [
        {'user': 'admin_norte', 'email': 'admin.norte@grastlax.com', 'rol': 'ADMIN', 'dep': deps[0]},
        {'user': 'ope_norte1', 'email': 'ope1.norte@grastlax.com', 'rol': 'OPERADOR', 'dep': deps[0]},
    ]

    for u in usuarios_data:
        if not Usuario.objects.filter(username=u['user']).exists():
            Usuario.objects.create_user(
                username=u['user'], email=u['email'], password="pass123", 
                rol=u['rol'], id_deposito=u['dep'], nombre_user=u['user']
            )

    # 3. PROPIETARIO
    prop, _ = Propietario.objects.get_or_create(
        identificacion="GEN001",
        defaults={'nombre': "General", 'apaterno': "Publico", 'correo': "general@corralon.com"}
    )

    # 4. VEHÍCULOS E INGRESOS (Editado para que no truene)
    vehiculos_data = [
        {'marca': 'Nissan', 'modelo': 'Versa', 'placa': 'VRS-99-AA', 'serie': 'SN_NISSAN_001', 'dep': deps[0], 'color': 'Blanco', 'anio': 2022},
    ]

    for v in vehiculos_data:
        car, _ = Vehiculo.objects.update_or_create(
            num_serie=v['serie'],
            defaults={
                'marca': v['marca'], 'modelo': v['modelo'], 'placas': v['placa'],
                'anio': v['anio'], 'color_original': v['color'], 'color_actual': v['color'],
                'tipo_vehiculo': "SEDAN", 'estatus_actual': "FUERA", 'propietario': prop,
                'numero_motor': 'MOTOR-SN-001'
            }
        )
    
        # Crear Ingreso solo si no existe
        if not Ingreso.objects.filter(vehiculo=car).exists():
            ing = Ingreso.objects.create(
                vehiculo=car, deposito=v['dep'], tipo_registro='NUEVO',
                tipo_servicio='PARTICULAR', autoridad_ingreso='Policía Estatal',
                motivo_ingreso='Infracción', fecha_ingreso=now(), lugar_siniestro="Av. Juárez"
            )

            # 5. DETALLES (Corregido con los CHOICES correctos)
            DetallesAuto.objects.create(
                ingreso=ing,
                estatus_carroceria='REGULAR',
                estatus_cristales='BUENO',
                estatus_espejos='BUENO',
                estado_asientos='BUENO',
                tipo_transmision='AUTOMATICA',
                estatus_combustible='MEDIO', # Antes decía '1/4' y eso truena
                estado_motor='BUENO'         # Antes decía 'FUNCIONA' y eso truena
            )

    print("✅ Carga Maestra finalizada con éxito.")

if __name__ == '__main__':
    seed_maestro()