import json

from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import serializers
from django.conf import settings
import threading
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Deposito, Usuario, Propietario, Vehiculo, 
    Ingreso, EstatusLegal, DetallesAuto, 
    ObjetoPersonal, SolicitudEdicion, Bitacora,
    RegistroDano, Inspeccion , FotoEvidencia
)
from .models import CodigoPostal
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from decouple import config as decouple_config

class IngresoListSerializer(serializers.ModelSerializer):
    # Traemos solo lo esencial del vehículo para la tabla
    vehiculo_detalle = serializers.SerializerMethodField()
    nombre_deposito = serializers.CharField(source='deposito.nombre', read_only=True)

    class Meta:
        model = Ingreso
        fields = [
            'id', 'folio', 'fecha_ingreso', 'nombre_deposito', 
            'vehiculo_detalle', 'tipo_registro', 'deposito'
        ]

    def get_vehiculo_detalle(self, obj):
        if obj.vehiculo:
            return {
                'marca': obj.vehiculo.marca,
                'modelo': obj.vehiculo.modelo,
                'anio': obj.vehiculo.anio,
                'placas': obj.vehiculo.placas,
                'estatus_actual': obj.vehiculo.estatus_actual
            }
        return None

# serializers.py
class CodigoPostalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoPostal
        fields = '__all__'
# --- AUTH ---

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['rol'] = user.rol
        # Opcional: puedes meter el estatus también en el token decodificado
        token['estatus_user'] = user.estatus_user 
        return token

    def validate(self, attrs):
        # 1. Ejecuta la validación base (revisa que user y password existan y coincidan)
        data = super().validate(attrs)

        # 2. Verificar si el usuario está suspendido
        # self.user es instanciado automáticamente por super().validate(attrs)
        if self.user.estatus_user == 'SUSPENDIDO':
            raise serializers.ValidationError({
                "detail": "Tu cuenta ha sido suspendida. Por favor, contacta al administrador del sistema."
            })

        # 3. Inyectar datos extra en la respuesta JSON del login para el frontend
        data['rol'] = self.user.rol
        data['id_deposito'] = self.user.id_deposito.id if self.user.id_deposito else None
        data['username'] = self.user.username
        data['nombre_user'] = self.user.nombre_user
        data['aPaterno_user'] = self.user.aPaterno_user
        data['email'] = self.user.email
        data['estatus_user'] = self.user.estatus_user # Útil para que el router de Vue lo guarde
        
        return data


# --- DEPOSITO ---

from rest_framework import serializers
from .models import Deposito, Ingreso # Asegúrate de importar Ingreso si no está

#---Deposito-----------

class DepositoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposito
        fields = [
            'id', 
            'nombre', 
            'calle', 
            'colonia', 
            'cp', 
            'municipio', 
            'estado', 
            'telefono', 
            'correo', 
            'estatus_deposito'
        ]
        
class CodigoPostalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoPostal
        fields = '__all__'

# --- USUARIO (VERSIÓN CORRECTA) ---

class UsuarioSerializer(serializers.ModelSerializer):
    id_deposito_detalles = DepositoSerializer(source='id_deposito', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'password', 'nombre_user', 'aPaterno_user', 
            'aMaterno_user', 'email', 'rol', 'id_deposito', 
            'id_deposito_detalles', 'estatus_user', 'telefono_user'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    def create(self, validated_data):
        password = validated_data.get('password')
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        email = validated_data.get('email')
        username = validated_data.get('username')

        if email:
            def enviar():
                try:
                    import requests as req
                    api_key = decouple_config('BREVO_API_KEY')
                    req.post(
                        'https://api.brevo.com/v3/smtp/email',
                        headers={'api-key': api_key, 'Content-Type': 'application/json'},
                        json={
                            'sender': {'email': 'mcarmonapalestina@gmail.com', 'name': 'SMYT Corralones'},
                            'to': [{'email': email}],
                            'subject': 'Credenciales de acceso — MSYT',
                            'textContent': f'Bienvenido al sistema.\n\nUsuario: {username}\nContraseña: {password}'
                        }
                    )
                except Exception as e:
                    print(f"Error enviando correo: {e}")

            threading.Thread(target=enviar, daemon=True).start()
        

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# --- BASICOS ---

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = '__all__'


class FotoEvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoEvidencia
        fields = '__all__'

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = [
            'id', 'num_serie', 'placas', 'marca', 'submarca','numero_motor',
            'modelo', 'anio', 'color_original', 'color_actual',
            'tipo_vehiculo', 'propietario', 'estatus_actual', 'repuve'
        ]


class RegistroDanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroDano
        fields = '__all__'


class ObjetoPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetoPersonal
        fields = '__all__'


class DetallesAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallesAuto
        fields = '__all__'


class EstatusLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatusLegal
        fields = '__all__'




class InspeccionSerializer(serializers.ModelSerializer):
    # Campos para mostrar información (Lectura)
    ingreso_data = serializers.SerializerMethodField()
    folio = serializers.CharField(source='ingreso.folio', read_only=True)
    # Cambiamos este nombre para que no choque con el campo de escritura
    admin_username = serializers.CharField(source='administrador.username', read_only=True)
    
    class Meta:
        model = Inspeccion
        fields = [
            'id',
            'ingreso',       
            'administrador',  
            'folio',
            'admin_username',
            'resultado',
            'observaciones_admin',
            'identificacion_ok',
            'inventario_ok',
            'estado_fisico_ok',
            'documentacion_ok',
            'fecha_revision',
            'ingreso_data'
        ]
        
    def get_ingreso_data(self, obj):
        try:
            v = obj.ingreso.vehiculo
            return {
                "vehiculo": f"{v.marca} {v.submarca} {v.modelo} {v.anio}",
                "placas": v.placas
            }
        except:
            return None


class SolicitudEdicionSerializer(serializers.ModelSerializer):
    # Traemos el nombre de usuario en lugar de solo el ID
    usuario_nombre = serializers.ReadOnlyField(source='usuario_solicito.username')
    admin_nombre = serializers.ReadOnlyField(source='usuario_acepto.username')
    
    # Opcional: Si quieres mostrar a qué vehículo pertenece en la lista
    # (Suponiendo que registro_id es el ID del Ingreso en la mayoría de los casos)
    folio_ingreso = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudEdicion
        fields = [
            'id', 'usuario_solicito', 'usuario_nombre', 'usuario_acepto', 
            'admin_nombre', 'justificacion', 'registro_id', 'campo_afectado', 
            'valor_viejo', 'valor_nuevo', 'estatus', 'evidencia_solicitud', 
            'motivo_rechazo', 'tabla_destino', 'fecha_solicitud', 'fecha_aceptacion',
            'folio_ingreso'
        ]

    def get_folio_ingreso(self, obj):
        try:
            from django.apps import apps
            Ingreso = apps.get_model('registros', 'Ingreso')
            Vehiculo = apps.get_model('registros', 'Vehiculo')

            # 1. CASO: El ID es de un INGRESO (Mecánica, Objetos, Daños)
            # Intentamos buscar el ingreso directamente
            if Ingreso.objects.filter(id=obj.registro_id).exists():
                ingreso = Ingreso.objects.get(id=obj.registro_id)
                return ingreso.folio

            # 2. CASO: El ID es de un VEHÍCULO (Marca, Serie, Placas)
            # Buscamos el ÚLTIMO ingreso que tuvo ese vehículo para mostrar su folio
            elif Vehiculo.objects.filter(id=obj.registro_id).exists():
                # Buscamos el ingreso más reciente relacionado a ese vehículo
                ultimo_ingreso = Ingreso.objects.filter(vehiculo_id=obj.registro_id).order_by('-id').first()
                return f"{ultimo_ingreso.folio} (Dato Vehículo)" if ultimo_ingreso else "Sin Ingreso"

            return "N/A"
        except Exception as e:
            print(f"Error en Serializer: {e}")
            return "Error ID"


class BitacoraSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    rol = serializers.CharField(source='usuario.rol', read_only=True)

    class Meta:
        model = Bitacora
        fields = ['id', 'tipo_evento', 'descripcion', 'usuario', 'rol', 'fecha_evento']


# --- INGRESO (FUSIONADO PRO) ---

class IngresoSerializer(serializers.ModelSerializer):
    vehiculo_detalle = VehiculoSerializer(source='vehiculo', read_only=True)
    nombre_deposito = serializers.CharField(source='deposito.nombre', read_only=True)

    detalles_auto = DetallesAutoSerializer(source='historial_detalles', read_only=True)
    objetos_personales = ObjetoPersonalSerializer(source='objetos_encontrados', many=True, read_only=True)
    registros_danos = RegistroDanoSerializer(source='danos', many=True, read_only=True)

    estatus_legales = EstatusLegalSerializer(many=True, read_only=True)
    #fotos_evidencia = FotoEvidenciaSerializer(many=True, read_only=True)
    fotos_evidencia = serializers.SerializerMethodField()

    def get_fotos_evidencia(self, obj):
        fotos = obj.fotos_evidencia.filter(estatus='ACEPTADA')
        return FotoEvidenciaSerializer(fotos, many=True).data
        
        
    vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(), 
        required=False, 
        allow_null=True
    )

    deposito = serializers.PrimaryKeyRelatedField(read_only=True)
    fecha_ingreso = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Ingreso
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        vehiculo_id = request.data.get('vehiculo')
        marca = request.data.get('marca')

        if vehiculo_id and vehiculo_id not in ['null', '', 'undefined']:
            vehiculo_obj = Vehiculo.objects.get(id=vehiculo_id)
        else:
            vehiculo_obj = Vehiculo.objects.create(
                marca=marca,
                submarca=request.data.get('submarca', ''),
                modelo=request.data.get('modelo'),
                anio=request.data.get('anio', 2026),
                placas=request.data.get('placas', '').upper(),
                num_serie=request.data.get('num_serie', '').upper(),
                numero_motor=request.data.get('numero_motor', 'S/N').upper(),
                color_actual=request.data.get('color_actual'),
                color_original=request.data.get('color_original'),
                tipo_vehiculo=request.data.get('tipo_vehiculo', 'SEDAN'),
                repuve=request.data.get('repuve', '')
            )

        validated_data['vehiculo'] = vehiculo_obj
        validated_data['fecha_ingreso'] = timezone.now()

        if hasattr(user, 'id_deposito') and user.id_deposito:
            validated_data['deposito'] = user.id_deposito

        mecanica_data = json.loads(request.data.get('detalles_auto', '{}'))
        objetos_data = json.loads(request.data.get('objetos_data', '[]'))
        danos_data = json.loads(request.data.get('danos_data', '[]'))

        ingreso = Ingreso.objects.create(**validated_data)

        # MECÁNICA
        # --- SECCIÓN DE MECÁNICA EN EL SERIALIZER cd ---
        # MECÁNICA (Ya sin las fotos)
        DetallesAuto.objects.create(
            ingreso=ingreso,
            presencia_bateria=mecanica_data.get('presencia_bateria', True),
            estatus_carroceria=mecanica_data.get('estatus_carroceria', 'BUENO'),
            cilindros=mecanica_data.get('cilindros'),
            cantidad_asientos=mecanica_data.get('cantidad_asientos'),
            estado_asientos=mecanica_data.get('estado_asientos', 'BUENO'), # 🚨 ¡FALTABA ESTA COMA!
            tipo_combustible=mecanica_data.get('tipo_combustible'),
            
            kilometraje_odometro=mecanica_data.get('kilometraje_odometro', 0),
            estatus_odometro=mecanica_data.get('estatus_odometro', 'FUNCIONAL'),
            
            estatus_cristales=mecanica_data.get('estatus_cristales', 'BUENO'),
            estatus_espejos=mecanica_data.get('estatus_espejos', 'BUENO'),
            estado_motor=mecanica_data.get('estado_motor', 'BUENO'),
            tipo_transmision=mecanica_data.get('tipo_transmision', 'MANUAL'),
            
            estatus_aceite_motor=mecanica_data.get('estatus_aceite_motor', 'MEDIO'),
            estatus_combustible=mecanica_data.get('estatus_combustible', 'MEDIO'),
            estatus_anticongelante=mecanica_data.get('estatus_anticongelante', 'MEDIO')
        )
        
        nombres_fotos = {
            'evidencia_foto_frontal': 'Frontal',
            'evidencia_foto_lateral_izquierda': 'Lateral Izquierda',
            'evidencia_foto_lateral_derecha': 'Lateral Derecha',
            'evidencia_foto_interior': 'Interior',
            'evidencia_foto_capo': 'Motor / Capó',
            'evidencia_foto_trasera': 'Trasera'
        }
        
        for clave, nombre_bonito in nombres_fotos.items():
            foto_file = request.FILES.get(clave)
            if foto_file:
                FotoEvidencia.objects.create(
                    ingreso=ingreso,
                    nombre=nombre_bonito,
                    foto=foto_file
                )
        
        EstatusLegal.objects.create(
            ingreso=ingreso,
            condicion_juridica=request.data.get('condicion_juridica'),
            num_oficio=request.data.get('num_oficio'),
            documento_oficio=request.FILES.get('documento_oficio'),
            fecha_oficio=request.data.get('fecha_oficio'),
            observaciones=request.data.get('observaciones'),
        )

        # OBJETOS
        for i, obj in enumerate(objetos_data):
            foto = request.FILES.get(f'foto_objeto_{i}')
            ObjetoPersonal.objects.create(
                ingreso=ingreso,
                foto_objeto=foto,
                descripcion=obj.get('descripcion', ''),
                cantidad=obj.get('cantidad', 1)
            )

        # DAÑOS
        for i, dano in enumerate(danos_data):
            foto = request.FILES.get(f'foto_dano_{i}')
            RegistroDano.objects.create(
                ingreso=ingreso,
                foto_evidencia=foto,
                parte_vehiculo=dano.get('parte_vehiculo', ''),
                descripcion=dano.get('descripcion', '')
            )

        return ingreso