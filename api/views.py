from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse

GENERIC_ERROR = 'No tienes permisos para realizar esta accion.'
# Create your views here.
# Autenticación

@api_view(['POST'])
def login(request):
    user = get_object_or_404(Usuarios, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({'details': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)
    update_last_login(None, user)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UsuariosSerializer(instance=user)
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def signup(request):
    serializer = UsuariosSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # Asegúrate de que la contraseña se haya seteado correctamente
            user.set_password(request.data['password'])
            user.save()
            # Crear el token para el usuario
            token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def logout(request):
    try:
        token = request.auth
        token.delete()
        return Response({'result':'Sesión cerrada'},status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'result':'Token no encontrado'},status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_locales(request):
    locales = Locales.objects.all()
    locales_list = []
    for local in locales:
        fotos = Fotos_Locales.objects.filter(local=local)
        fotos_list = [{'id': foto.id, 'imagen': foto.imagen.url} for foto in fotos]
        locales_list.append({
            'id': local.id,
            'nombre': local.nombre,
            'direccion': local.direccion,
            'categoria_culinaria': {
                'id': local.categoria_culinaria.id,
                'nombre': local.categoria_culinaria.nombre,
                'descripcion': local.categoria_culinaria.descripcion
            } if local.categoria_culinaria else None,
            'empresa': {
                'id': local.empresa.id,
                'nombre': local.empresa.nombre,
                'confirmado': local.empresa.confirmado,
                'usuario': local.empresa.usuario.id,
                'localNum': local.empresa.locales.count()
            } if local.empresa else None,
            'fotos': fotos_list
        })
    return JsonResponse(locales_list, safe=False)
# Usuarios
class ListUsers(generics.ListCreateAPIView):
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated]  # Asegúrate de que la vista requiere autenticación
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Usuarios.objects.all()
        else:
            queryset = [user]
        return queryset

class DetailedUsers(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if self.request.user.is_superuser:
            return Usuarios.objects.get(id=self.kwargs['pk'])
        else:
            if self.request.user.id == self.kwargs['pk']:
                return self.request.user
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            user = self.request.user
            if user.id == self.kwargs['pk']:
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser:
            if 'password' in request.data:
                user.set_password(request.data['password'])
                user.save()
                request.data.pop('password')  # Remove password from request data to avoid rehashing
            return super().update(request, *args, **kwargs)
        else:
            if user.id == self.request.user.id:
                if 'password' in request.data:
                    user.set_password(request.data['password'])
                    user.save()
                    request.data.pop('password')
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser:
            if 'password' in request.data:
                user.set_password(request.data['password'])
                user.save()
                request.data.pop('password')  # Remove password from request data to avoid rehashing
            return super().partial_update(request, *args, **kwargs)
        else:
            if user.id == self.request.user.id:
                if 'password' in request.data:
                    user.set_password(request.data['password'])
                    user.save()
                    request.data.pop('password')
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)


# Empresas
class ListEmpresas(generics.ListCreateAPIView):
    serializer_class = EmpresasSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Empresas.objects.all()
        elif self.request.user.rol == 4:
            queryset = Empresas.objects.filter(usuario=self.request.user)
        else:
            queryset = Empresas.objects.none()
        return queryset
    def perform_create(self, serializer):
        if self.request.user.rol == 4 or self.request.user.is_superuser:
            empresa_existe = Empresas.objects.filter(usuario=self.request.user).exists()
            if not empresa_existe:
                serializer.save(usuario=self.request.user, confirmado=False)
            else:
                raise PermissionDenied('Ya tienes una empresa registrada.')
        else:
            raise PermissionDenied('No tienes permisos para realizar esta acción.')

class DetailedEmpresas(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmpresasSerializer
    def get_object(self):
        empresa = get_object_or_404(Empresas, id=self.kwargs['pk'])
        if self.request.user.is_superuser:
            return empresa
        elif self.request.user.rol == 4:
            if self.request.user == empresa.usuario:
                return empresa
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        empresa = self.get_object()
        if not empresa:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if self.request.user.is_superuser:
            empresa.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif self.request.user.rol == 4:
            if self.request.user == empresa.usuario:
                empresa.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        empresa = self.get_object()
        if not empresa:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if self.request.is_superuser:
            return self.update(request, *args, **kwargs)
        elif self.request.user.rol == 4:
            if self.request.user == empresa.usuario:
                return self.update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        empresa = self.get_object()
        if not empresa:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if self.request.is_superuser:
            return self.partial_update(request, *args, **kwargs)
        elif self.request.user.rol == 4:
            if self.request.user == empresa.usuario:
                return self.partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Categorias Culinarias
class ListCategoriasCulinarias(generics.ListCreateAPIView):
    serializer_class = CategoriasCulinariasSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CategoriasCulinarias.objects.all()
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)

class DetailedCategoriasCulinarias(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoriasCulinariasSerializer

    def get_object(self):
        return get_object_or_404(CategoriasCulinarias, id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().partial_update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Locales
class ListLocales(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LocalesSerializer
    def perform_create(self, serializer):
        if self.request.user.is_superuser or self.request.user.rol == 4:
            empresa = get_object_or_404(Empresas, usuario=self.request.user)
            if not empresa.confirmado:
                raise PermissionDenied(GENERIC_ERROR + ' Espera a que un administrador confirme tu empresa.')
            else:
                serializer.save(empresa=empresa)
                empresa.localNum += 1
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)

class DetailedLocales(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LocalesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Locales, id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser or self.request.user.rol == 4:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        local = self.get_object()
        if self.request.user.rol == 4:
            if self.request.user == local.empresa.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 4:
            if self.request.user == local.empresa.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Horarios
class ListHorarios(generics.ListCreateAPIView):
    serializer_class = HorariosSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Horarios.objects.all()
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.user.rol == 3:
            local = Locales.objects.get(usuario=self.request.user)
            serializer.save(local=local)
        else:
            raise PermissionDenied(GENERIC_ERROR)
class DetailedHorarios(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HorariosSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        return get_object_or_404(Horarios, local=local, id=self.kwargs['pk'])
    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs['local'])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Fotos Locales
class ListFotosLocales(generics.ListCreateAPIView):
    serializer_class = FotosLocalesSerializer
    def get_queryset(self):
        return Fotos_Locales.objects.all()
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.user.rol == 3:
            local = Locales.objects.get(usuario=self.request.user)
            serializer.save(local=local)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)

class DetailedFotosLocales(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FotosLocalesSerializer
    def get_object(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        return get_object_or_404(Fotos_Locales, local=local, id=self.kwargs['pk'])
    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs['local'])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Productos
class ListProductos(generics.ListCreateAPIView):
    serializer_class = ProductosSerializer

    def get_queryset(self):
        return Productos.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.user.rol == 3:
            local = Locales.objects.get(usuario=self.request.user)
            serializer.save(local=local)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)

class DetailedProductos(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductosSerializer

    def get_object(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        return get_object_or_404(Productos, local=local, id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs['local'])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Tramos Horarios
class ListTramosHorarios(generics.ListCreateAPIView):
    serializer_class = TramosHorariosSerializer

    def get_queryset(self):
        return Tramos_Horarios.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.user.rol == 3:
            local = Locales.objects.get(usuario=self.request.user)
            serializer.save(local=local)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)

class DetailedTramosHorarios(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TramosHorariosSerializer

    def get_object(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        return get_object_or_404(Tramos_Horarios, local=local, id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs['local'])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Reservas
class ListReservas(generics.ListCreateAPIView):
    serializer_class = ReservasSerializer

    def get_queryset(self):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            return Reservas.objects.filter(local=local)
        elif self.request.user.is_superuser:
            return Reservas.objects.all()
        else:
            return Reservas.objects.filter(usuario=self.request.user)
    def perform_create(self, serializer):
        usuario = self.request.user
        local = Locales.objects.get(id=self.request['local'])
        tramo_horario = Tramos_Horarios.objects.get(id=self.request['tramo_horario'])
        serializer.save(local=local, usuario=usuario, tramo_horario=tramo_horario, estado=1)
        

class DetailedReservas(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservasSerializer

    def get_object(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        reserva = Reservas.objects.get(id=self.kwargs['pk'], local=local)
        if self.request.user.rol == 3:
            return reserva
        elif self.request.user.is_superuser:
            return reserva
        elif self.request.user == reserva.usuario:
            return reserva
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        reserva = self.get_object()
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                reserva.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        elif reserva.usuario == self.request.user:
            reserva.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        reserva = self.get_object()
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
        elif self.request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        elif self.request.user == reserva.usuario:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def patch(self, request, *args, **kwargs):
        reserva = self.get_object()
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs['local'])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
        elif self.request.user.is_superuser:
            return super().partial_update(request, *args, **kwargs)
        elif self.request.user == reserva.usuario:
            return super().partial_update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)

# Comentarios
class ListComentarios(generics.ListCreateAPIView):
    serializer_class = ComentariosSerializer

    def get_queryset(self):
        local = Locales.objects.get(id=self.kwargs['local'])
        return Comentarios.objects.filter(local=local)

    def perform_create(self, serializer):
        usuario = self.request.user
        local = Locales.objects.get(id=self.request['local'])
        serializer.save(local=local, usuario=usuario)

class DetailedComentarios(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComentariosSerializer

    def get_object(self):
        comentario = Comentarios.objects.get(id=self.kwargs['pk'])
    def delete(self, request, *args, **kwargs):
        comentario = self.get_object()
        if self.request.user == comentario.usuario:
            comentario.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def update(self, request, *args, **kwargs):
        comentario = self.get_object()
        if self.request.user == comentario.usuario:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    def partial_update(self, request, *args, **kwargs):
        comentario = self.get_object()
        if self.request.user == comentario.usuario:
            return super().partial_update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)