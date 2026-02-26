from rest_framework import viewsets
from .models import Usuario, Deposito, Vehiculo, Ingreso, Propietario, DetallesAuto, ObjetoPersonal
from .serializers import (
    UsuarioSerializer, DepositoSerializer, VehiculoSerializer, 
    IngresoSerializer, PropietarioSerializer
)

class DepositoViewSet(viewsets.ModelViewSet):
    queryset = Deposito.objects.all()
    serializer_class = DepositoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

class IngresoViewSet(viewsets.ModelViewSet):
    queryset = Ingreso.objects.all()
    serializer_class = IngresoSerializer

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer