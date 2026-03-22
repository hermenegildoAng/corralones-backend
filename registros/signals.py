# signals.py — versión completa y fusionada

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Usuario,
    Deposito,
    Ingreso,
    Liberacion,
    SolicitudEdicion,
    Inspeccion,
    RegistroDano,
    Vehiculo,
    Bitacora,
)


# ─── HELPER ───────────────────────────────────────────────────
def log(tipo_evento: str, descripcion: str, usuario=None):
    Bitacora.objects.create(
        tipo_evento=tipo_evento,
        descripcion=descripcion,
        usuario=usuario,
    )


# ─── 1. VEHÍCULO (creación / edición) ────────────────────────
@receiver(post_save, sender=Vehiculo)
def bitacora_vehiculo(sender, instance, created, **kwargs):
    accion = "Creación" if created else "Edición"
    log(
        tipo_evento=f"{accion} de Vehículo",
        descripcion=(
            f"Vehículo {instance.marca} {instance.modelo} {instance.anio} "
            f"(Placas: {instance.placas} | VIN: {instance.num_serie}) "
            f"fue {'registrado' if created else 'modificado'}. "
            f"Estatus: {instance.estatus_actual}."
        ),
    )


# ─── 2. INGRESO DE VEHÍCULO ───────────────────────────────────
@receiver(post_save, sender=Ingreso)
def bitacora_ingreso(sender, instance, created, **kwargs):
    if not created:
        return

    v = instance.vehiculo
    log(
        tipo_evento="Ingreso de Vehículo",
        descripcion=(
            f"Ingresó {v.marca} {v.modelo} {v.anio} "
            f"(Placas: {v.placas} | VIN: {v.num_serie}) "
            f"al depósito '{instance.deposito.nombre}'. "
            f"Folio: {instance.folio}. "
            f"Motivo: {instance.motivo_ingreso}."
        ),
    )


# ─── 3. LIBERACIÓN DE VEHÍCULO ────────────────────────────────
@receiver(post_save, sender=Liberacion)
def bitacora_liberacion(sender, instance, created, **kwargs):
    if not created:
        return

    ingreso  = instance.ingreso
    vehiculo = ingreso.vehiculo
    log(
        tipo_evento="Liberación de Vehículo",
        descripcion=(
            f"El vehículo {vehiculo.marca} {vehiculo.modelo} "
            f"(Placas: {vehiculo.placas}) fue liberado. "
            f"Folio: {ingreso.folio}. "
            f"Recibió: {instance.quien_recibe} "
            f"(ID: {instance.identificacion_recibe}). "
            f"Autoridad: {instance.autoridad_autoriza}. "
            f"Oficio: {instance.numero_oficio_liberacion}."
        ),
    )


# ─── 4. REGISTRO DE DAÑOS ─────────────────────────────────────
@receiver(post_save, sender=RegistroDano)
def bitacora_danos(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        vehiculo = instance.ingreso.vehiculo
        log(
            tipo_evento="Registro de Daño",
            descripcion=(
                f"Se registró daño en '{instance.parte_vehiculo}' "
                f"del vehículo {vehiculo.marca} {vehiculo.modelo} "
                f"(Placas: {vehiculo.placas}). "
                f"Descripción: {instance.descripcion}. "
                f"Folio: {instance.ingreso.folio}."
            ),
        )
    except Exception as e:
        print(f"[signals] Error en bitacora_danos: {e}")


# ─── 5. SOLICITUD DE EDICIÓN ──────────────────────────────────
@receiver(post_save, sender=SolicitudEdicion)
def bitacora_solicitud_edicion(sender, instance, created, **kwargs):
    if created:
        log(
            tipo_evento="Edición — Solicitud Creada",
            descripcion=(
                f"'{instance.usuario_solicito.username}' solicitó editar "
                f"el campo '{instance.campo_afectado}' "
                f"(Tabla: {instance.tabla_destino}, ID: {instance.registro_id}). "
                f"'{instance.valor_viejo}' → '{instance.valor_nuevo}'. "
                f"Justificación: {instance.justificacion}."
            ),
            usuario=instance.usuario_solicito,
        )
    elif instance.estatus == 'ACEPTADA':
        revisor = instance.usuario_acepto.username if instance.usuario_acepto else 'Sistema'
        log(
            tipo_evento="Edición — Aceptada",
            descripcion=(
                f"Solicitud #{instance.id} ACEPTADA por '{revisor}'. "
                f"Campo '{instance.campo_afectado}' actualizado a '{instance.valor_nuevo}'."
            ),
            usuario=instance.usuario_acepto,
        )
    elif instance.estatus == 'RECHAZADA':
        revisor = instance.usuario_acepto.username if instance.usuario_acepto else 'Sistema'
        log(
            tipo_evento="Edición — Rechazada",
            descripcion=(
                f"Solicitud #{instance.id} RECHAZADA por '{revisor}'. "
                f"Campo: '{instance.campo_afectado}'. "
                f"Motivo: {instance.motivo_rechazo or 'No especificado'}."
            ),
            usuario=instance.usuario_acepto,
        )


# ─── 6. INSPECCIÓN DE VEHÍCULO ────────────────────────────────
@receiver(post_save, sender=Inspeccion)
def bitacora_inspeccion(sender, instance, created, **kwargs):
    if not created:
        return

    ingreso  = instance.ingreso
    vehiculo = ingreso.vehiculo

    semaforo = []
    if not instance.identificacion_ok: semaforo.append('ID/Placas con inconsistencias')
    if not instance.inventario_ok:     semaforo.append('Inventario físico incompleto')
    if not instance.estado_fisico_ok:  semaforo.append('Daños físicos sin validar')
    if not instance.documentacion_ok:  semaforo.append('Documentación con problemas')
    semaforo_str = '; '.join(semaforo) if semaforo else 'Todo verificado correctamente'

    log(
        tipo_evento="Inspección de Vehículo",
        descripcion=(
            f"Inspección del vehículo {vehiculo.marca} {vehiculo.modelo} "
            f"(Placas: {vehiculo.placas}) — Folio: {ingreso.folio}. "
            f"Resultado: {instance.resultado}. "
            f"Inspector: {instance.administrador.username}. "
            f"Verificación: {semaforo_str}. "
            f"Observaciones: {instance.observaciones_admin or 'Ninguna'}."
        ),
        usuario=instance.administrador,
    )


# ─── 7. CREACIÓN DE USUARIO ───────────────────────────────────
@receiver(post_save, sender=Usuario)
def bitacora_usuario(sender, instance, created, **kwargs):
    if not created:
        return

    deposito = instance.id_deposito.nombre if instance.id_deposito else 'Acceso Global'
    log(
        tipo_evento="Creación de Usuario",
        descripcion=(
            f"Se creó el usuario '{instance.username}' "
            f"({instance.nombre_user} {instance.aPaterno_user}) "
            f"con rol {instance.rol} — Sede: {deposito}."
        ),
    )


# ─── 8. CREACIÓN DE DEPÓSITO ──────────────────────────────────
@receiver(post_save, sender=Deposito)
def bitacora_deposito(sender, instance, created, **kwargs):
    if not created:
        return

    log(
        tipo_evento="Creación de Depósito",
        descripcion=(
            f"Se registró el depósito '{instance.nombre}' "
            f"en {instance.municipio}, {instance.estado} "
            f"(C.P. {instance.cp}). Estatus: {instance.estatus_deposito}."
        ),
    )