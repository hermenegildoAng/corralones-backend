"""
seed.py — Datos de prueba para el sistema de depósitos vehiculares
Uso: python manage.py shell < seed.py
  o: Copiar como management command en registros/management/commands/seed.py
"""

import os
import django
import datetime
from django.utils.timezone import now

# ── Si lo ejecutas con `python seed.py` directo (sin manage.py shell) ──
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
# django.setup()

from registros.models import (
    Deposito, Propietario, Vehiculo, Ingreso,
    EstatusLegal, DetallesAuto, ObjetoPersonal,
    RegistroDano, Inspeccion, Bitacora
)
from django.contrib.auth import get_user_model

Usuario = get_user_model()

print("🌱 Iniciando seed...")

# ─────────────────────────────────────────────────────────────────
# 1. DEPÓSITOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando depósitos...")

deposito_1, _ = Deposito.objects.get_or_create(
    nombre="Corralón Central Tlaxcala",
    defaults={
        "calle": "Av. Insurgentes 450",
        "colonia": "Centro",
        "cp": "90000",
        "municipio": "Tlaxcala de Xicohténcatl",
        "estado": "Tlaxcala",
        "telefono": "2461234567",
        "correo": "central@corralonTlax.gob.mx",
        "estatus_deposito": "ACTIVO",
    }
)

deposito_2, _ = Deposito.objects.get_or_create(
    nombre="Depósito Norte Apizaco",
    defaults={
        "calle": "Calle Reforma 120",
        "colonia": "Zona Industrial",
        "cp": "90300",
        "municipio": "Apizaco",
        "estado": "Tlaxcala",
        "telefono": "2417654321",
        "correo": "norte@corralonTlax.gob.mx",
        "estatus_deposito": "ACTIVO",
    }
)

deposito_3, _ = Deposito.objects.get_or_create(
    nombre="Depósito Sur Huamantla",
    defaults={
        "calle": "Blvd. Xicoténcatl 88",
        "colonia": "La Loma",
        "cp": "90500",
        "municipio": "Huamantla",
        "estado": "Tlaxcala",
        "telefono": "2479876543",
        "correo": "sur@corralonTlax.gob.mx",
        "estatus_deposito": "ACTIVO",
    }
)

print(f"     ✅ {Deposito.objects.count()} depósitos creados.")

# ─────────────────────────────────────────────────────────────────
# 2. USUARIOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando usuarios...")

# SUPER — sin sede
super_user, created = Usuario.objects.get_or_create(
    username="admin_secretaria",
    defaults={
        "nombre_user": "Carlos",
        "aPaterno_user": "Mendoza",
        "aMaterno_user": "Ríos",
        "email": "cmendoza@secretaria.gob.mx",
        "telefono_user": "2461000001",
        "rol": "SUPER",
        "id_deposito": None,
        "estatus_user": "ACTIVO",
        "is_staff": True,
    }
)
if created:
    super_user.set_password("Admin2026")
    super_user.save()

# ADMIN — sede central
admin_central, created = Usuario.objects.get_or_create(
    username="jgarcia",
    defaults={
        "nombre_user": "Jorge",
        "aPaterno_user": "García",
        "aMaterno_user": "López",
        "email": "jgarcia@corralonTlax.gob.mx",
        "telefono_user": "2461000002",
        "rol": "ADMIN",
        "id_deposito": deposito_1,
        "estatus_user": "ACTIVO",
    }
)
if created:
    admin_central.set_password("Garcia2026")
    admin_central.save()

# ADMIN — sede norte
admin_norte, created = Usuario.objects.get_or_create(
    username="mhernandez",
    defaults={
        "nombre_user": "María",
        "aPaterno_user": "Hernández",
        "aMaterno_user": "Torres",
        "email": "mhernandez@corralonTlax.gob.mx",
        "telefono_user": "2417000001",
        "rol": "ADMIN",
        "id_deposito": deposito_2,
        "estatus_user": "ACTIVO",
    }
)
if created:
    admin_norte.set_password("Hernandez2026")
    admin_norte.save()

# OPERADOR — sede central
operador_1, created = Usuario.objects.get_or_create(
    username="rlopez",
    defaults={
        "nombre_user": "Roberto",
        "aPaterno_user": "López",
        "aMaterno_user": "Pérez",
        "email": None,
        "telefono_user": "2461000003",
        "rol": "OPERADOR",
        "id_deposito": deposito_1,
        "estatus_user": "ACTIVO",
    }
)
if created:
    operador_1.set_password("Lopez2026")
    operador_1.save()

# OPERADOR — sede sur (SUSPENDIDO)
operador_2, created = Usuario.objects.get_or_create(
    username="aprojas",
    defaults={
        "nombre_user": "Ana",
        "aPaterno_user": "Rojas",
        "aMaterno_user": "Sánchez",
        "email": None,
        "telefono_user": "2479000001",
        "rol": "OPERADOR",
        "id_deposito": deposito_3,
        "estatus_user": "SUSPENDIDO",
    }
)
if created:
    operador_2.set_password("Rojas2026")
    operador_2.save()

print(f"     ✅ {Usuario.objects.count()} usuarios creados.")

# ─────────────────────────────────────────────────────────────────
# 3. PROPIETARIOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando propietarios...")

prop_1, _ = Propietario.objects.get_or_create(
    identificacion="TLAX901234HGRLPZ09",
    defaults={
        "nombre": "Luis",
        "apaterno": "Ramírez",
        "amaterno": "Flores",
        "correo": "luis.ramirez@gmail.com",
        "telefono": "2461112233",
        "direccion": "Calle Morelos 12, Tlaxcala Centro",
    }
)

prop_2, _ = Propietario.objects.get_or_create(
    identificacion="TLAX850601MGRTRN05",
    defaults={
        "nombre": "Teresa",
        "apaterno": "González",
        "amaterno": "Ramos",
        "correo": None,
        "telefono": "2417223344",
        "direccion": "Av. Hidalgo 88, Apizaco",
    }
)

prop_3, _ = Propietario.objects.get_or_create(
    identificacion="TLAX780312HGRCRS02",
    defaults={
        "nombre": "Fernando",
        "apaterno": "Cruz",
        "amaterno": "Ortega",
        "correo": "fcruz@hotmail.com",
        "telefono": "2479334455",
        "direccion": "Privada Juárez 5, Huamantla",
    }
)

print(f"     ✅ {Propietario.objects.count()} propietarios creados.")

# ─────────────────────────────────────────────────────────────────
# 4. VEHÍCULOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando vehículos...")

auto_1, _ = Vehiculo.objects.get_or_create(
    num_serie="3VWFE21C04M000001",
    defaults={
        "marca": "Volkswagen",
        "submarca": "Jetta",
        "modelo": "A4",
        "anio": 2004,
        "color_original": "Blanco",
        "color_actual": "Blanco",
        "placas": "TLX-123-A",
        "numero_motor": "AZM001234",
        "tipo_vehiculo": "SEDAN",
        "propietario": prop_1,
        "estatus_actual": "DENTRO",
        "repuve": "SIN REPORTE",
    }
)

auto_2, _ = Vehiculo.objects.get_or_create(
    num_serie="1HGBH41JXMN109186",
    defaults={
        "marca": "Honda",
        "submarca": "Civic",
        "modelo": "EX",
        "anio": 2018,
        "color_original": "Gris",
        "color_actual": "Gris",
        "placas": "TLX-456-B",
        "numero_motor": "R18A5678",
        "tipo_vehiculo": "SEDAN",
        "propietario": prop_2,
        "estatus_actual": "DENTRO",
        "repuve": "SIN REPORTE",
    }
)

auto_3, _ = Vehiculo.objects.get_or_create(
    num_serie="JTDBL40E299100301",
    defaults={
        "marca": "Toyota",
        "submarca": "Corolla",
        "modelo": "LE",
        "anio": 2009,
        "color_original": "Rojo",
        "color_actual": "Rojo",
        "placas": "TLX-789-C",
        "numero_motor": "2ZR0000301",
        "tipo_vehiculo": "SEDAN",
        "propietario": prop_3,
        "estatus_actual": "DENTRO",
        "repuve": "REPORTE ACTIVO",
    }
)

auto_4, _ = Vehiculo.objects.get_or_create(
    num_serie="5TEUX42N79Z123456",
    defaults={
        "marca": "Toyota",
        "submarca": "Tacoma",
        "modelo": "SR5",
        "anio": 2009,
        "color_original": "Negro",
        "color_actual": "Negro",
        "placas": "TLX-321-D",
        "numero_motor": "2TR123456",
        "tipo_vehiculo": "PICKUP",
        "propietario": None,
        "estatus_actual": "DENTRO",
        "repuve": "SIN REPORTE",
    }
)

print(f"     ✅ {Vehiculo.objects.count()} vehículos creados.")

# ─────────────────────────────────────────────────────────────────
# 5. INGRESOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando ingresos...")

# Ingreso 1 — Jetta en depósito central
ingreso_1 = None
if not Ingreso.objects.filter(vehiculo=auto_1).exists():
    ingreso_1 = Ingreso(
        vehiculo=auto_1,
        deposito=deposito_1,
        tipo_servicio="PARTICULAR",
        tipo_registro="NUEVO",
        autoridad_ingreso="Policía Municipal de Tlaxcala",
        presencia_factura=True,
        lugar_siniestro="Av. Insurgentes km 3, Tlaxcala",
        motivo_ingreso="Vehículo asegurado por conducir en estado de ebriedad",
        fecha_ingreso=now() - datetime.timedelta(days=10),
    )
    ingreso_1.save()

# Ingreso 2 — Civic en depósito norte
ingreso_2 = None
if not Ingreso.objects.filter(vehiculo=auto_2).exists():
    ingreso_2 = Ingreso(
        vehiculo=auto_2,
        deposito=deposito_2,
        tipo_servicio="PARTICULAR",
        tipo_registro="NUEVO",
        autoridad_ingreso="Tránsito Estatal Apizaco",
        presencia_factura=False,
        lugar_siniestro="Calle Reforma y Juárez, Apizaco",
        motivo_ingreso="Accidente vial con daños a terceros, vehículo retenido",
        fecha_ingreso=now() - datetime.timedelta(days=5),
    )
    ingreso_2.save()

# Ingreso 3 — Corolla en depósito sur
ingreso_3 = None
if not Ingreso.objects.filter(vehiculo=auto_3).exists():
    ingreso_3 = Ingreso(
        vehiculo=auto_3,
        deposito=deposito_3,
        tipo_servicio="PUBLIC0",
        tipo_registro="INVENTARIO",
        autoridad_ingreso="Agencia del Ministerio Público Huamantla",
        presencia_factura=False,
        lugar_siniestro="Blvd. Xicoténcatl s/n, Huamantla",
        motivo_ingreso="Vehículo con reporte de robo activo en REPUVE",
        fecha_ingreso=now() - datetime.timedelta(days=20),
    )
    ingreso_3.save()

# Ingreso 4 — Tacoma en depósito central
ingreso_4 = None
if not Ingreso.objects.filter(vehiculo=auto_4).exists():
    ingreso_4 = Ingreso(
        vehiculo=auto_4,
        deposito=deposito_1,
        tipo_servicio="PARTICULAR",
        tipo_registro="NUEVO",
        autoridad_ingreso="Policía Federal Carretera",
        presencia_factura=False,
        lugar_siniestro="Carretera Tlaxcala-Apizaco km 12",
        motivo_ingreso="Vehículo abandonado sin documentación, sin propietario identificado",
        fecha_ingreso=now() - datetime.timedelta(days=2),
    )
    ingreso_4.save()

print(f"     ✅ {Ingreso.objects.count()} ingresos creados.")

# ─────────────────────────────────────────────────────────────────
# 6. ESTATUS LEGAL
# ─────────────────────────────────────────────────────────────────
print("  → Creando estatus legales...")

for ingreso, oficio, condicion in [
    (ingreso_1, "OF-2026-001", "Asegurado Administrativo"),
    (ingreso_2, "OF-2026-002", "Retenido por Accidente"),
    (ingreso_3, "OF-2026-003", "Detenido por Investigación"),
    (ingreso_4, "OF-2026-004", "Abandonado - En Proceso Legal"),
]:
    if ingreso and not EstatusLegal.objects.filter(ingreso=ingreso).exists():
        EstatusLegal.objects.create(
            ingreso=ingreso,
            condicion_juridica=condicion,
            num_oficio=oficio,
            fecha_oficio=datetime.date.today() - datetime.timedelta(days=1),
            observaciones="Registro generado por seed de prueba.",
        )

print(f"     ✅ {EstatusLegal.objects.count()} estatus legales creados.")

# ─────────────────────────────────────────────────────────────────
# 7. DETALLES AUTO (Mecánica / Inspección física)
# ─────────────────────────────────────────────────────────────────
print("  → Creando detalles de autos...")

datos_detalles = [
    (ingreso_1, "BUENO",   "BUENO",   "BUENO",   4, "GASOLINA", 4, True),
    (ingreso_2, "REGULAR", "BUENO",   "REGULAR", 4, "GASOLINA", 5, True),
    (ingreso_3, "MALO",    "MALO",    "MALO",    4, "GASOLINA", 4, False),
    (ingreso_4, "BUENO",   "REGULAR", "BUENO",   6, "DIESEL",   5, True),
]

for ingreso, carroceria, motor, asientos_est, cilindros, combustible, cant_asientos, bateria in datos_detalles:
    if ingreso and not DetallesAuto.objects.filter(ingreso=ingreso).exists():
        DetallesAuto.objects.create(
            ingreso=ingreso,
            estatus_carroceria=carroceria,
            estatus_cristales="BUENO",
            estatus_espejos="BUENO",
            cant_llantas_delanteras=2,
            cant_llantas_traseras=2,
            estado_asientos=asientos_est,
            vehiculo_sin_danos=(carroceria == "BUENO" and motor == "BUENO"),
            estado_motor=motor,
            cilindros=cilindros,
            cantidad_asientos=cant_asientos,
            tipo_combustible=combustible,
            presencia_bateria=bateria,
            tipo_transmision="MANUAL",
            estatus_odometro="FUNCIONAL",
            kilometraje_odometro=85000,
            estatus_aceite_motor="MEDIO",
            estatus_anticongelante="LLENO",
            estatus_combustible="BAJO",
            estatus_bolsas_aire="INTACTAS",
        )

print(f"     ✅ {DetallesAuto.objects.count()} detalles creados.")

# ─────────────────────────────────────────────────────────────────
# 8. OBJETOS PERSONALES
# ─────────────────────────────────────────────────────────────────
print("  → Creando objetos personales...")

objetos_seed = [
    (ingreso_1, "Mochila negra con documentos personales", 1),
    (ingreso_1, "Gafas de sol marca Ray-Ban", 1),
    (ingreso_2, "Botiquín de primeros auxilios", 1),
    (ingreso_2, "Cables de corriente (jumper)", 1),
    (ingreso_3, "Teléfono celular sin batería", 1),
    (ingreso_4, "Herramienta básica (llave de rueda, gato)", 1),
]

for ingreso, descripcion, cantidad in objetos_seed:
    if ingreso:
        ObjetoPersonal.objects.get_or_create(
            ingreso=ingreso,
            descripcion=descripcion,
            defaults={"cantidad": cantidad, "estado_objeto": "BUENO"}
        )

print(f"     ✅ {ObjetoPersonal.objects.count()} objetos personales creados.")

# ─────────────────────────────────────────────────────────────────
# 9. REGISTROS DE DAÑOS
# ─────────────────────────────────────────────────────────────────
print("  → Creando registros de daños...")

danos_seed = [
    (ingreso_2, "Defensa delantera",     "Golpe severo con deformación, pérdida de pintura"),
    (ingreso_2, "Faro delantero derecho","Cristal roto, carcasa dañada"),
    (ingreso_3, "Cofre (capó)",          "Abolladura profunda en zona central"),
    (ingreso_3, "Parabrisas",            "Fractura diagonal de esquina a esquina"),
    (ingreso_3, "Puerta trasera derecha","Rayones profundos y oxido visible"),
    (ingreso_4, "Espejo retrovisor izq.", "Desprendido, cables expuestos"),
]

for ingreso, parte, descripcion in danos_seed:
    if ingreso:
        RegistroDano.objects.get_or_create(
            ingreso=ingreso,
            parte_vehiculo=parte,
            defaults={"descripcion": descripcion}
        )

print(f"     ✅ {RegistroDano.objects.count()} daños registrados.")

# ─────────────────────────────────────────────────────────────────
# 10. INSPECCIONES ADMINISTRATIVAS
# ─────────────────────────────────────────────────────────────────
print("  → Creando inspecciones...")

inspecciones_seed = [
    (ingreso_1, admin_central, "APROBADO",   True,  True,  True,  True,  ""),
    (ingreso_2, admin_central, "OBSERVADO",  True,  True,  False, True,  "Faltan fotos del lado trasero del daño en defensa."),
    (ingreso_3, admin_norte,   "RECHAZADO",  False, True,  False, False, "VIN no coincide con documentación. Requiere verificación física urgente."),
]

for ingreso, admin, resultado, id_ok, inv_ok, fisico_ok, doc_ok, observaciones in inspecciones_seed:
    if ingreso and not Inspeccion.objects.filter(ingreso=ingreso).exists():
        Inspeccion.objects.create(
            ingreso=ingreso,
            administrador=admin,
            resultado=resultado,
            identificacion_ok=id_ok,
            inventario_ok=inv_ok,
            estado_fisico_ok=fisico_ok,
            documentacion_ok=doc_ok,
            observaciones_admin=observaciones,
        )

print(f"     ✅ {Inspeccion.objects.count()} inspecciones creadas.")

# ─────────────────────────────────────────────────────────────────
# 11. BITÁCORA
# ─────────────────────────────────────────────────────────────────
print("  → Creando entradas de bitácora...")

bitacora_seed = [
    (super_user,    "LOGIN",            "Inicio de sesión desde IP 192.168.1.10"),
    (admin_central, "CREACION_INGRESO", f"Creó ingreso con folio {ingreso_1.folio if ingreso_1 else 'SMyT-2026-0001'}"),
    (operador_1,    "CREACION_INGRESO", f"Creó ingreso con folio {ingreso_4.folio if ingreso_4 else 'SMyT-2026-0004'}"),
    (admin_central, "INSPECCION",       f"Aprobó inspección del folio {ingreso_1.folio if ingreso_1 else 'SMyT-2026-0001'}"),
    (admin_norte,   "INSPECCION",       f"Rechazó inspección del folio {ingreso_3.folio if ingreso_3 else 'INV-2026-0001'} por inconsistencia en VIN"),
    (super_user,    "SUSPENSION_USER",  f"Suspendió al usuario @{operador_2.username}"),
]

for usuario, tipo, descripcion in bitacora_seed:
    Bitacora.objects.create(
        usuario=usuario,
        tipo_evento=tipo,
        descripcion=descripcion,
    )

print(f"     ✅ {Bitacora.objects.count()} entradas en bitácora.")

# ─────────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────────
print("")
print("=" * 50)
print("✅ SEED COMPLETADO")
print("=" * 50)
print(f"  Depósitos:       {Deposito.objects.count()}")
print(f"  Usuarios:        {Usuario.objects.count()}")
print(f"  Propietarios:    {Propietario.objects.count()}")
print(f"  Vehículos:       {Vehiculo.objects.count()}")
print(f"  Ingresos:        {Ingreso.objects.count()}")
print(f"  Estatus Legales: {EstatusLegal.objects.count()}")
print(f"  Detalles Auto:   {DetallesAuto.objects.count()}")
print(f"  Objetos:         {ObjetoPersonal.objects.count()}")
print(f"  Daños:           {RegistroDano.objects.count()}")
print(f"  Inspecciones:    {Inspeccion.objects.count()}")
print(f"  Bitácora:        {Bitacora.objects.count()}")
print("=" * 50)
print("")
print("🔑 Credenciales de acceso:")
print("   SUPER    → admin_secretaria / Admin2026")
print("   ADMIN    → jgarcia          / Garcia2026")
print("   ADMIN    → mhernandez       / Hernandez2026")
print("   OPERADOR → rlopez           / Lopez2026")
print("   OPERADOR → aprojas          / Rojas2026  (SUSPENDIDO)")
print("=" * 50)