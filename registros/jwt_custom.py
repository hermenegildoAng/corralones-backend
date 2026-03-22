# registros/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTConVerificacionEstatus(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        
        if user.estatus_user == 'SUSPENDIDO':
            raise AuthenticationFailed('Tu cuenta ha sido suspendida.')
        
        return user