from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from django.apps import apps

from django.utils.timezone import now
from .models import CodigoPostal


from django.utils.timezone import now
import json
# Importa tus modelos y serializers
from .models import (
    Usuario, Deposito, Vehiculo, Ingreso, Propietario, EstatusLegal, FotoEvidencia,
    DetallesAuto, ObjetoPersonal, RegistroDano, Inspeccion, SolicitudEdicion, Bitacora
)
from .serializers import (
    UsuarioSerializer, DepositoSerializer, VehiculoSerializer, 
    IngresoSerializer, PropietarioSerializer, DetallesAutoSerializer, 
    ObjetoPersonalSerializer, RegistroDanoSerializer, InspeccionSerializer, 
    SolicitudEdicionSerializer, BitacoraSerializer, FotoEvidenciaSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

# --- VISTAS DE AUTENTICACIÓN Y CONFIGURACIÓN ---
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view




import json
import ast

@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_cp(request, cp):
    try:
        codigo = CodigoPostal.objects.get(cp=cp)
        colonias = codigo.colonias
        
        # Asegurar que sea lista
        if isinstance(colonias, str):
            try:
                colonias = json.loads(colonias)
            except:
                colonias = ast.literal_eval(colonias)
        
        return Response({
            'estado': codigo.estado,
            'municipio': codigo.municipio,
            'colonias': colonias
        })
    except CodigoPostal.DoesNotExist:
        return Response({'error': 'CP no encontrado'}, status=404)

User = get_user_model()

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()

        # Siempre responde 200 aunque el email no exista (seguridad)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Si el correo existe, recibirás un enlace.'}, status=200)

        # Genera token y uid
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construye el link al frontend
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        print("UID:", uid)
        print("TOKEN:", token)
        

        # Envía el correo
        send_mail(
            subject = 'Recuperación de contraseña — MSYT',
            message = f'Hola {user.nombre_user},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n\n{reset_url}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este correo.',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [email],
        )

        return Response({'message': 'Si el correo existe, recibirás un enlace.'}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid      = request.data.get('uid')
        token    = request.data.get('token')
        password = request.data.get('new_password')

        if not all([uid, token, password]):
            return Response({'error': 'Faltan datos.'}, status=400)

        try:
            pk   = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            return Response({'error': 'Enlace inválido.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'El enlace expiró o ya fue usado.'}, status=400)

        user.set_password(password)
        user.save()

        return Response({'message': '¡Contraseña actualizada correctamente!'}, status=200)
    
    
    

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bitacora.objects.all().order_by('-fecha_evento')
    serializer_class = BitacoraSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class DepositoViewSet(viewsets.ModelViewSet):
    queryset = Deposito.objects.all().order_by('-id')
    serializer_class = DepositoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    #queryset = Usuario.objects.all()
    queryset = Usuario.objects.all().order_by('-id')
    serializer_class = UsuarioSerializer
    

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer
    search_fields = ['nombre', 'identificacion', 'telefono']
    
    
class FotoEvidenciaViewSet(viewsets.ModelViewSet):
    queryset = FotoEvidencia.objects.all().order_by('-id')
    serializer_class = FotoEvidenciaSerializer
    filterset_fields = ['estatus', 'ingreso', 'es_solicitud']  # ← agregar 'aceptada'

# --- VISTAS OPERATIVAS (El corazón del sistema) ---

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['placas', 'num_serie', 'marca']
    filterset_fields = ['estatus_actual', 'tipo_servicio']

class IngresoViewSet(viewsets.ModelViewSet):
    """
    Esta vista maneja todo el registro de entrada usando el IngresoSerializer.
    Maneja la creación de Vehículo, Detalles, Objetos y Daños automáticamente.
    """
    serializer_class = IngresoSerializer
    #queryset = Ingreso.objects.all().select_related('vehiculo', 'deposito')
    queryset = Ingreso.objects.all().select_related('vehiculo', 'deposito').order_by('-id')
    parser_classes = [MultiPartParser, FormParser] # IMPORTANTE para recibir archivos
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Ingreso.objects.none()

        if user.rol == 'SUPER':
            return self.queryset
        
        # Filtramos por el depósito asignado al usuario (Admin/Operador)
        return self.queryset.filter(deposito=user.id_deposito)

# --- VISTAS DE DETALLES Y EVIDENCIA ---

class RegistroDanoViewSet(viewsets.ModelViewSet):
    queryset = RegistroDano.objects.all()
    serializer_class = RegistroDanoSerializer
    filterset_fields = ['ingreso'] 

class ObjetoPersonalViewSet(viewsets.ModelViewSet):
    queryset = ObjetoPersonal.objects.all()
    serializer_class = ObjetoPersonalSerializer
    filterset_fields = ['ingreso']

class DetallesAutoViewSet(viewsets.ModelViewSet):
    queryset = DetallesAuto.objects.all()
    serializer_class = DetallesAutoSerializer
    filterset_fields = ['ingreso']

# --- VISTAS DE CONTROL Y EDICIÓN ---

class InspeccionViewSet(viewsets.ModelViewSet):
    queryset = Inspeccion.objects.all().order_by('-id')
    serializer_class = InspeccionSerializer
    filterset_fields = ['resultado', 'ingreso', 'administrador']
    
    def perform_create(self, serializer):
        # Esto ignora lo que venga de Vue y usa al usuario que hizo la petición
        serializer.save(administrador=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # Si es superusuario → ve todo
        if user.is_superuser:
            return Inspeccion.objects.all().order_by('-id')

        # Operador → solo inspecciones de su depósito
        return Inspeccion.objects.filter(
            ingreso__deposito=user.id_deposito
        ).order_by('-id')
    
    

from rest_framework.decorators import action, api_view, permission_classes


        
        
        
# --- 1. EL CIRUJANO (PARA EL ADMIN) ---
class SolicitudEdicionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudEdicion.objects.all().order_by('-id')
    serializer_class = SolicitudEdicionSerializer
    filterset_fields = ['estatus']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revisar(self, request, pk=None):
        solicitud = self.get_object()
        data = request.data
        
        # 1. Limpieza de estatus
        estatus_raw = data.get('estatus', '')   
        if isinstance(estatus_raw, list) and len(estatus_raw) > 0:
            estatus_raw = estatus_raw[0]
            
        nuevo_estatus = str(estatus_raw).strip().upper()
        motivo = data.get('motivo_rechazo', '')

        if solicitud.estatus != 'PENDIENTE':
            return Response({'error': 'Esta solicitud ya fue procesada'}, status=400)

        if nuevo_estatus == 'ACEPTADA':
            try:
                tabla_destino = solicitud.tabla_destino 

                # --- ESCENARIO 1: EDITAR OBJETO O DAÑO EXISTENTE ---
                if tabla_destino in ['ObjetoPersonal', 'RegistroDano']:
                    Modelo = apps.get_model('registros', tabla_destino)
                    objeto = Modelo.objects.get(id=solicitud.registro_id)
                    
                    es_foto = "Foto" in solicitud.campo_afectado or "Evidencia" in solicitud.campo_afectado
                    
                    if es_foto:
                        if "Objeto" in tabla_destino:
                            objeto.foto_objeto = solicitud.evidencia_solicitud
                        else:
                            objeto.foto_evidencia = solicitud.evidencia_solicitud
                    else:
                        if "Objeto" in tabla_destino:
                            try:
                                datos = json.loads(solicitud.valor_nuevo)
                                if isinstance(datos, str): datos = json.loads(datos)
                                datos_clean = {str(k).lower(): v for k, v in datos.items()}
                                
                                objeto.descripcion = datos_clean.get('descripcion', objeto.descripcion)
                                objeto.cantidad = datos_clean.get('cantidad', objeto.cantidad)
                                objeto.estado_objeto = str(datos_clean.get('estado', objeto.estado_objeto)).upper()
                            except:
                                val_crudo = str(solicitud.valor_nuevo).upper().strip()
                                if val_crudo in ['BUENO', 'REGULAR', 'MALO', 'DAÑADO']:
                                    objeto.estado_objeto = val_crudo
                                elif val_crudo.isdigit():
                                    objeto.cantidad = int(val_crudo)
                                else:
                                    objeto.descripcion = solicitud.valor_nuevo
                        else: # Daños
                            try:
                                datos = json.loads(solicitud.valor_nuevo)
                                if isinstance(datos, str): datos = json.loads(datos)
                                datos_clean = {str(k).lower(): v for k, v in datos.items()}
                                objeto.parte_vehiculo = datos_clean.get('parte_vehiculo', objeto.parte_vehiculo)
                                objeto.descripcion = datos_clean.get('descripcion', objeto.descripcion)
                            except:
                                objeto.descripcion = solicitud.valor_nuevo
                    objeto.save()

                # --- ESCENARIO 2: AÑADIR NUEVOS ---
                elif "añadir" in solicitud.campo_afectado.lower():
                    datos = json.loads(solicitud.valor_nuevo)
                    if "objeto" in solicitud.campo_afectado.lower():
                        apps.get_model('registros', 'ObjetoPersonal').objects.create(
                            ingreso_id=solicitud.registro_id,
                            descripcion=datos.get('descripcion'),
                            cantidad=datos.get('cantidad', 1),
                            estado_objeto=datos.get('estado', 'BUENO'),
                            foto_objeto=solicitud.evidencia_solicitud
                        )
                    elif "daño" in solicitud.campo_afectado.lower():
                        apps.get_model('registros', 'RegistroDano').objects.create(
                            ingreso_id=solicitud.registro_id,
                            parte_vehiculo=datos.get('parte_vehiculo'),
                            descripcion=datos.get('descripcion'),
                            foto_evidencia=solicitud.evidencia_solicitud
                        )

                # --- ESCENARIO 3: EDITAR VEHÍCULO O MECÁNICA ---
                else:
                    # Buscamos el Ingreso primero (ancla segura)
                    IngresoM = apps.get_model('registros', 'Ingreso')
                    # 🚨 Corregido de request_id a registro_id
                    ingreso_obj = IngresoM.objects.get(id=solicitud.registro_id) 

                    if solicitud.tabla_destino == 'DetallesAuto':
                        DetalleM = apps.get_model('registros', 'DetallesAuto')
                        objeto = DetalleM.objects.get(ingreso_id=ingreso_obj.id)
                    elif solicitud.tabla_destino == 'Vehiculo':
                        objeto = ingreso_obj.vehiculo
                    else:
                        objeto = ingreso_obj

                    # Aplicamos el cambio
                    if 'foto' in solicitud.campo_afectado or 'evidencia' in solicitud.campo_afectado:
                        setattr(objeto, solicitud.campo_afectado, solicitud.evidencia_solicitud)
                    else:
                        setattr(objeto, solicitud.campo_afectado, solicitud.valor_nuevo)
                    
                    objeto.save() 
                
                # --- CIERRE DE SOLICITUD ---
                solicitud.estatus = 'ACEPTADA'
                solicitud.usuario_acepto = request.user
                solicitud.fecha_aceptacion = now()
                solicitud.save()

                return Response({'status': 'Cambio aplicado con éxito'})

            except Exception as e:
                import traceback
                traceback.print_exc()
                return Response({'error': str(e)}, status=500)

        elif nuevo_estatus == 'RECHAZADA':
            if not motivo:
                return Response({'error': 'Motivo requerido'}, status=400)
            solicitud.estatus = 'RECHAZADA'
            solicitud.motivo_rechazo = motivo
            solicitud.usuario_acepto = request.user
            solicitud.fecha_aceptacion = now()
            solicitud.save()
            return Response({'status': 'Solicitud rechazada'})

        return Response({'error': 'Estatus no válido', 'recibido': nuevo_estatus}, status=400)
        
        
        
        
        
        
        
        
        
        

# --- 2. LA RECEPCIONISTA (PARA EL OPERADOR) ---
@api_view(['POST'])
def Crear_solicitud_cambio(request):
    try:
        modo = request.data.get('modo')
        ingreso_id = request.data.get('ingreso_id')
        justificacion = request.data.get('justificacion')
        archivo = request.FILES.get('archivo')

        ingreso = get_object_or_404(Ingreso, id=ingreso_id)

        if modo == 'FOTO_EXTRA':
            nombre_foto = request.data.get('nombre_foto', 'Evidencia Extra')
            FotoEvidencia.objects.create(
                ingreso=ingreso,
                nombre=nombre_foto,
                foto=archivo,
                estatus='PENDIENTE', 
                justificacion=justificacion,# ← pendiente de aprobación
                es_solicitud=True
            )
            


        elif modo == 'NUEVO_DANO':
            RegistroDano.objects.create(ingreso=ingreso, parte_vehiculo=request.data.get('parte_vehiculo', ''), descripcion=request.data.get('descripcion', ''), foto_evidencia=archivo)

        elif modo == 'NUEVO_OBJETO':
            ObjetoPersonal.objects.create(ingreso=ingreso, descripcion=request.data.get('descripcion', ''), cantidad=request.data.get('cantidad', 1), estado_objeto=request.data.get('estado', 'BUENO'), foto_objeto=archivo)

        elif modo == 'NUEVO_DOCUMENTO':
            tipo_doc = request.data.get('tipo_documento')
            if tipo_doc == 'Factura Original':
                ingreso.factura_original = archivo
                ingreso.presencia_factura = True
                ingreso.save()
            else:
                estatus = EstatusLegal.objects.filter(ingreso=ingreso).first()
                if estatus:
                    estatus.documento_oficio = archivo
                    estatus.save()
                else:
                    EstatusLegal.objects.create(ingreso=ingreso, documento_oficio=archivo)

        elif modo == 'EDICION_NORMAL':
            campo_db = request.data.get('campo') # Ej: 'num_serie'
            valor_nuevo = request.data.get('valor_nuevo')
            tabla_destino = request.data.get('tabla') or 'Ingreso'
        
            # --- LÓGICA PARA EL VALOR VIEJO ---
            valor_viejo = "No encontrado"
            try:
                ModeloDestino = apps.get_model('registros', tabla_destino)
                
                if tabla_destino == 'DetallesAuto':
                    obj_viejo = ModeloDestino.objects.get(ingreso_id=ingreso.id)
                else:
                    id_busqueda = request.data.get('id_especifico') or ingreso.id
                    obj_viejo = ModeloDestino.objects.get(id=id_busqueda)
                
                # 🚨 CORREGIDO: Usamos campo_db (que es lo que viene de Vue)
                valor_viejo = str(getattr(obj_viejo, campo_db, 'N/A'))
            except Exception as e:
                print(f"Error al buscar valor viejo: {e}")
                valor_viejo = "Dato actual"

            # Creamos la solicitud
            SolicitudEdicion.objects.create(
                usuario_solicito=request.user,
                tabla_destino=tabla_destino,
                justificacion=justificacion,
                registro_id=ingreso.id,
                campo_afectado=campo_db, # 🚨 CORREGIDO: campo_db
                valor_viejo=valor_viejo, 
                valor_nuevo=valor_nuevo,
                evidencia_solicitud=archivo,
                estatus='PENDIENTE'
            )

        return Response({"mensaje": "¡Movimiento registrado con éxito!"}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error detallado:", str(e))  # ← agregar
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  # ← cambiar para ver el error real
    
    
    
    
    
@api_view(['POST'])
def revisar_foto(request, foto_id):
    foto = get_object_or_404(FotoEvidencia, id=foto_id)
    decision = request.data.get('decision')  # 'ACEPTAR' o 'RECHAZAR'
    
    if decision == 'ACEPTAR':
        foto.estatus = 'ACEPTADA'
        foto.motivo_rechazo = None
        foto.save()
        return Response({'mensaje': 'Foto aprobada'})
    
    elif decision == 'RECHAZAR':
        motivo = request.data.get('motivo_rechazo', '')
        if not motivo:
            return Response({'error': 'El motivo es requerido'}, status=400)
        foto.estatus = 'RECHAZADA'
        foto.motivo_rechazo = motivo
        foto.save()
        return Response({'mensaje': 'Foto rechazada'})
    
    return Response({'error': 'Decisión no válida'}, status=400)