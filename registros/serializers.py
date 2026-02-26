from rest_framework import serializers
from .models import (
    Deposito, Usuario, Propietario, Vehiculo, 
    Ingreso, EstatusLegal, DetallesAuto, 
    ObjetoPersonal, SolicitudEdicion, Bitacora
)

class DepositoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposito
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'rol', 'id_deposito', 'aPaterno_user', 'aMaterno_user', 'estatus_user']

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = '__all__'

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'

class IngresoSerializer(serializers.ModelSerializer):
    
    folio = serializers.CharField(read_only=True)
    class Meta:
        model = Ingreso
        fields = '__all__'

class EstatusLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatusLegal
        fields = '__all__'

class DetallesAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallesAuto
        fields = '__all__'

class ObjetoPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetoPersonal
        fields = '__all__'

class SolicitudEdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudEdicion
        fields = '__all__'

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = '__all__'