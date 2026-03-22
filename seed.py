import os
import django
import datetime
from django.utils.timezone import now

# ─────────────────────────────────────
# CONFIG DJANGO (ARREGLA TU ERROR 2)
# ─────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from registros.models import (
    Deposito, Propietario, Vehiculo, Ingreso,
    DetallesAuto
)
from django.contrib.auth import get_user_model

Usuario = get_user_model()

print("🌱 Iniciando seed maestro...\n")

# ─────────────────────────────────────
# 1. DEPÓSITOS
# ─────────────────────────────────────
print("→ Creando depósitos...")

deposito_norte, _ = Deposito.objects.get_or_create(
    nombre="Corralón Norte Apizaco",
    defaults={
        "calle": "Carretera Apizaco Km 2",
        "colonia": "Zona Industrial",
        "cp": "90300",
        "municipio": "Apizaco",
        "estado": "Tlaxcala",
        "telefono": "2411111111",
        "correo": "norte@corralon.gob.mx",
        "estatus_deposito": "ACTIVO",
    }
)

deposito_central, _ = Deposito.objects.get_or_create(
    nombre="Depósito Central Tlaxcala",
    defaults={
        "calle": "Av. Juárez 123",
        "colonia": "Centro",
        "cp": "90000",
        "municipio": "Tlaxcala",
        "estado": "Tlaxcala",
        "telefono": "2461111111",
        "correo": "central@corralon.gob.mx",
        "estatus_deposito": "ACTIVO",
    }
)

print(f"   ✅ {Deposito.objects.count()} depósitos listos\n")

# ─────────────────────────────────────
# 2. USUARIOS OBLIGATORIOS
# ─────────────────────────────────────
print("→ Creando usuarios obligatorios...")

# SUPER ROOT
super_root, created = Usuario.objects.get_or_create(
    username="super_root",
    defaults={
        "email": "root@corralon.gob.mx",
        "rol": "SUPER",
        "nombre_user": "Super",
        "aPaterno_user": "Root",
        "estatus_user": "ACTIVO",
        "is_staff": True,
        "is_superuser": True,
    }
)
if created:
    super_root.set_password("root123")
    super_root.save()

# ADMIN NORTE
admin_norte, created = Usuario.objects.get_or_create(
    username="admin_norte",
    defaults={
        "email": "admin.norte@corralon.gob.mx",
        "rol": "ADMIN",
        "nombre_user": "Admin",
        "aPaterno_user": "Norte",
        "id_deposito": deposito_norte,
        "estatus_user": "ACTIVO",
        "is_staff": True,
    }
)
if created:
    admin_norte.set_password("admin123")
    admin_norte.save()

# OPERADOR NORTE
ope_norte1, created = Usuario.objects.get_or_create(
    username="ope_norte1",
    defaults={
        "email": "ope.norte@corralon.gob.mx",
        "rol": "OPERADOR",
        "nombre_user": "Operador",
        "aPaterno_user": "Norte",
        "id_deposito": deposito_norte,
        "estatus_user": "ACTIVO",
    }
)
if created:
    ope_norte1.set_password("ope123")
    ope_norte1.save()

print(f"   ✅ {Usuario.objects.count()} usuarios listos\n")

# ─────────────────────────────────────
# 3. PROPIETARIO
# ─────────────────────────────────────
print("→ Creando propietario...")

propietario, _ = Propietario.objects.get_or_create(
    identificacion="GEN001",
    defaults={
        "nombre": "Juan",
        "apaterno": "Pérez",
        "amaterno": "López",
        "correo": "juan@gmail.com",
        "telefono": "2460000000",
        "direccion": "Tlaxcala Centro",
    }
)

print(f"   ✅ {Propietario.objects.count()} propietarios\n")

# ─────────────────────────────────────
# 4. VEHÍCULO
# ─────────────────────────────────────
print("→ Creando vehículo...")

vehiculo, _ = Vehiculo.objects.get_or_create(
    num_serie="SNTEST001",
    defaults={
        "marca": "Nissan",
        "submarca": "Versa",
        "modelo": "Sense",
        "anio": 2022,
        "color_original": "Blanco",
        "color_actual": "Blanco",
        "placas": "TLX-000-A",
        "numero_motor": "MOTOR001",
        "tipo_vehiculo": "SEDAN",
        "propietario": propietario,
        "estatus_actual": "DENTRO",
        "repuve": "SIN REPORTE",
    }
)

print(f"   ✅ {Vehiculo.objects.count()} vehículos\n")

# ─────────────────────────────────────
# 5. INGRESO
# ─────────────────────────────────────
print("→ Creando ingreso...")

ingreso = None
if not Ingreso.objects.filter(vehiculo=vehiculo).exists():
    ingreso = Ingreso.objects.create(
        vehiculo=vehiculo,
        deposito=deposito_norte,
        tipo_servicio="PARTICULAR",
        tipo_registro="NUEVO",
        autoridad_ingreso="Policía Estatal",
        presencia_factura=True,
        lugar_siniestro="Av. Principal",
        motivo_ingreso="Infracción de tránsito",
        fecha_ingreso=now(),
    )

print(f"   ✅ {Ingreso.objects.count()} ingresos\n")

# ─────────────────────────────────────
# 6. DETALLES AUTO
# ─────────────────────────────────────
print("→ Creando detalles del auto...")

if ingreso and not DetallesAuto.objects.filter(ingreso=ingreso).exists():
    DetallesAuto.objects.create(
        ingreso=ingreso,
        estatus_carroceria="BUENO",
        estatus_cristales="BUENO",
        estatus_espejos="BUENO",
        cant_llantas_delanteras=2,
        cant_llantas_traseras=2,
        estado_asientos="BUENO",
        vehiculo_sin_danos=True,
        estado_motor="BUENO",
        cilindros=4,
        cantidad_asientos=5,
        tipo_combustible="GASOLINA",
        presencia_bateria=True,
        tipo_transmision="MANUAL",
        estatus_odometro="FUNCIONAL",
        kilometraje_odometro=50000,
        estatus_aceite_motor="MEDIO",
        estatus_anticongelante="LLENO",
        estatus_combustible="MEDIO",
        estatus_bolsas_aire="INTACTAS",
    )

print(f"   ✅ {DetallesAuto.objects.count()} detalles\n")

# ─────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────
print("="*50)
print("✅ SEED COMPLETADO")
print("="*50)
print(f"Depósitos:   {Deposito.objects.count()}")
print(f"Usuarios:    {Usuario.objects.count()}")
print(f"Propietarios:{Propietario.objects.count()}")
print(f"Vehículos:   {Vehiculo.objects.count()}")
print(f"Ingresos:    {Ingreso.objects.count()}")
print(f"Detalles:    {DetallesAuto.objects.count()}")
print("="*50)

print("\n🔑 Usuarios creados:")
print("SUPER     → super_root   / root123")
print("ADMIN     → admin_norte  / admin123")
print("OPERADOR  → ope_norte1   / ope123")      