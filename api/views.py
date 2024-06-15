from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
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
from django.utils import timezone

GENERIC_ERROR = "No tienes permisos para realizar esta accion."


# Autenticación
@api_view(["POST"])
def login(request):
    user = get_object_or_404(Usuarios, email=request.data["email"])
    if not user.check_password(request.data["password"]):
        return Response(
            {"details": "Invalid credentials"}, status=status.HTTP_404_NOT_FOUND
        )
    update_last_login(None, user)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UsuariosSerializer(instance=user)
    return Response(
        {"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
def logout(request):
    try:
        token = request.auth
        token.delete()
        return Response({"result": "Sesión cerrada"}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response(
            {"result": "Token no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def signup(request):
    serializer = UsuariosSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            # Asegúrate de que la contraseña se haya seteado correctamente
            user.set_password(request.data["password"])
            user.save()
            # Crear el token para el usuario
            token, created = Token.objects.get_or_create(user=user)

            # Si se proporciona local_id, asignar al usuario a ese local
            local_id = request.data.get("local_id")
            if local_id:
                local = get_object_or_404(Locales, id=local_id)
                user.locales.add(local)

        return Response(
            {"token": token.key, "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Usuarios
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def mi_usuario(request):
    if request.method == "GET":
        user = request.user
        serializer = UsuariosSerializer(user)
        return Response(serializer.data)
    elif request.method == "PATCH":
        user = request.user
        data = request.data

        if "old_password" in data and "password" in data and "password_confirm" in data:
            old_password = data.get("old_password")
            new_password = data.get("password")
            password_confirm = data.get("password_confirm")

            if not user.check_password(old_password):
                return Response(
                    {"detail": "La contraseña actual es incorrecta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if new_password != password_confirm:
                return Response(
                    {"detail": "Las nuevas contraseñas no coinciden."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()
            return Response({"detail": "Contraseña actualizada correctamente."})

        serializer = UsuariosSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListUsers(generics.ListCreateAPIView):
    serializer_class = UsuariosSerializer
    permission_classes = [
        IsAuthenticated
    ]  # Asegúrate de que la vista requiere autenticación

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Usuarios.objects.all()
        else:
            queryset = [user]
        return queryset


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
                serializer.save(usuario=self.request.user, confirmado=False, localNum=0)
            else:
                raise PermissionDenied("Ya tienes una empresa registrada.")
        else:
            raise PermissionDenied("No tienes permisos para realizar esta acción.")


# Locales
@api_view(["GET"])
def get_locales(request):
    locales = Locales.objects.all()
    locales_list = []
    for local in locales:
        fotos = Fotos_Locales.objects.filter(local=local)
        fotos_list = [{"id": foto.id, "imagen": foto.imagen.url} for foto in fotos]
        locales_list.append(
            {
                "id": local.id,
                "nombre": local.nombre,
                "direccion": local.direccion,
                "categoria_culinaria": (
                    {
                        "id": local.categoria_culinaria.id,
                        "nombre": local.categoria_culinaria.nombre,
                        "descripcion": local.categoria_culinaria.descripcion,
                    }
                    if local.categoria_culinaria
                    else None
                ),
                "empresa": (
                    {
                        "id": local.empresa.id,
                        "nombre": local.empresa.nombre,
                        "confirmado": local.empresa.confirmado,
                        "usuario": local.empresa.usuario.id,
                        "localNum": local.empresa.locales.count(),
                    }
                    if local.empresa
                    else None
                ),
                "fotos": fotos_list,
            }
        )
    return JsonResponse(locales_list, safe=False)


@api_view(["GET"])
def get_locales_empresas(request, id):
    locales = Locales.objects.filter(empresa=id)
    locales_list = []
    for local in locales:
        fotos = Fotos_Locales.objects.filter(local=local)
        fotos_list = [{"id": foto.id, "imagen": foto.imagen.url} for foto in fotos]
        locales_list.append(
            {
                "id": local.id,
                "nombre": local.nombre,
                "direccion": local.direccion,
                "categoria_culinaria": (
                    {
                        "id": local.categoria_culinaria.id,
                        "nombre": local.categoria_culinaria.nombre,
                        "descripcion": local.categoria_culinaria.descripcion,
                    }
                    if local.categoria_culinaria
                    else None
                ),
                "empresa": (
                    {
                        "id": local.empresa.id,
                        "nombre": local.empresa.nombre,
                        "confirmado": local.empresa.confirmado,
                        "usuario": local.empresa.usuario.id,
                        "localNum": local.empresa.locales.count(),
                    }
                    if local.empresa
                    else None
                ),
                "fotos": fotos_list,
            }
        )
    return JsonResponse(locales_list, safe=False)


@api_view(["GET"])
def get_mi_local(request):
    try:
        local = request.user.locales.first()
        if not local:
            return Response(
                {"detail": "Local no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve related data
        fotos = Fotos_Locales.objects.filter(local=local)
        productos = Productos.objects.filter(local=local)
        horarios = Horarios.objects.filter(local=local)
        tramos_horarios = Tramos_Horarios.objects.filter(local=local)
        comentarios = Comentarios.objects.filter(local=local)

        # Prepare data for the response
        fotos_list = [{"id": foto.id, "imagen": foto.imagen.url} for foto in fotos]
        productos_list = [
            {
                "id": producto.id,
                "nombre_producto": producto.nombre_producto,
                "descripcion": producto.descripcion,
                "precio": producto.precio,
                "categoria": producto.categoria,
                "imagen": producto.imagen.url,
            }
            for producto in productos
        ]
        horarios_list = [
            {
                "id": horario.id,
                "hora_apertura": horario.hora_apertura,
                "hora_cierre": horario.hora_cierre,
                "dias": {
                    "L": horario.L,
                    "M": horario.M,
                    "X": horario.X,
                    "J": horario.J,
                    "V": horario.V,
                    "S": horario.S,
                    "D": horario.D,
                },
            }
            for horario in horarios
        ]
        tramos_horarios_list = [
            {
                "id": tramo.id,
                "h_inicio": tramo.h_inicio,
                "h_final": tramo.h_final,
                "nombre": tramo.nombre,
                "clientes_maximos": tramo.clientes_maximos,
            }
            for tramo in tramos_horarios
        ]
        comentarios_list = [
            {
                "id": comentario.id,
                "usuario": comentario.usuario.id,
                "fecha": comentario.fecha,
                "comentario": comentario.comentario,
                "estrellas": comentario.estrellas,
                "respuesta": comentario.respuesta,
            }
            for comentario in comentarios
        ]

        local_return = {
            "id": local.id,
            "nombre": local.nombre,
            "direccion": local.direccion,
            "categoria_culinaria": (
                {
                    "id": local.categoria_culinaria.id,
                    "nombre": local.categoria_culinaria.nombre,
                    "descripcion": local.categoria_culinaria.descripcion,
                }
                if local.categoria_culinaria
                else None
            ),
            "empresa": (
                {
                    "id": local.empresa.id,
                    "nombre": local.empresa.nombre,
                    "confirmado": local.empresa.confirmado,
                    "localNum": local.empresa.locales.count(),
                }
                if local.empresa
                else None
            ),
            "fotos": fotos_list,
            "productos": productos_list,
            "horarios": horarios_list,
            "tramos_horarios": tramos_horarios_list,
            "comentarios": comentarios_list,
        }

        return Response(local_return, status=status.HTTP_200_OK)
    except Locales.DoesNotExist:
        return Response(
            {"detail": "Local no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["DELETE"])
def delete_local(request, id):
    try:
        local = get_object_or_404(Locales, id=id)
        if request.user.is_superuser or (
            request.user.rol == 4 and request.user == local.empresa.usuario
        ):
            # Eliminar encargados asociados al local
            encargados = Usuarios.objects.filter(locales=local)
            for encargado in encargados:
                encargado.delete()
            local.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "No tienes permisos para realizar esta acción."},
                status=status.HTTP_403_FORBIDDEN,
            )
    except Locales.DoesNotExist:
        return Response(
            {"detail": "Local no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


class ListCategoriasCulinarias(generics.ListCreateAPIView):
    serializer_class = CategoriasCulinariasSerializer

    def get_queryset(self):
        return Categorias_Culinarias.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)


# Reservas
@api_view(["GET"])
def get_reservas_cliente(request):
    if request.user.is_authenticated:
        reservas = Reservas.objects.filter(usuario=request.user)
        serializer = ReservasSerializerAll(reservas, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {"detail": "Authentication credentials were not provided."}, status=401
        )


class DetailedReservas(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservasSerializer

    def get_object(self):
        local = Locales.objects.get(id=self.kwargs["local"])
        return get_object_or_404(Reservas, local=local, id=self.kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        reserva = self.get_object()
        if (
            self.request.user.rol == 3
            or self.request.user.is_superuser
            or self.request.user == reserva.usuario
        ):
            reserva.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        reserva = self.get_object()
        if (
            self.request.user.rol == 3
            or self.request.user.is_superuser
            or self.request.user == reserva.usuario
        ):
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        reserva = self.get_object()
        if (
            self.request.user.rol == 3
            or self.request.user.is_superuser
            or self.request.user == reserva.usuario
        ):
            return super().partial_update(request, *args, **kwargs)
        else:
            raise PermissionDenied(GENERIC_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_reservas(request, local):
    if request.user.rol == 3:
        local = Locales.objects.get(id=local)
        if request.user == local.usuario:
            reservas = Reservas.objects.filter(local=local)
            serializer = ReservasSerializerAll(reservas, many=True)
            return Response(serializer.data)
        else:
            raise PermissionDenied(GENERIC_ERROR)
    else:
        raise PermissionDenied(GENERIC_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_reserva(request):
    serializer = ReservasSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def cancelar_reserva(request, pk):
    try:
        reserva = Reservas.objects.get(pk=pk, usuario=request.user)
        if request.user.is_authenticated and reserva.fecha >= timezone.now().date():
            reserva.estado = Reservas.Estado.RECHAZADA
            reserva.save()
            return Response({"detail": "Reserva cancelada."}, status=200)
        else:
            return Response(
                {
                    "detail": "No puedes cancelar una reserva pasada o no tienes permiso."
                },
                status=403,
            )
    except Reservas.DoesNotExist:
        return Response({"detail": "Reserva no encontrada."}, status=404)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_reserva(request, pk):
    try:
        reserva = Reservas.objects.get(pk=pk, usuario=request.user.id)
        if request.user.is_authenticated and (
            reserva.fecha < timezone.now().date() or reserva.estado == 3
        ):
            reserva.delete()
            return Response({"detail": "Reserva eliminada."}, status=200)
        else:
            return Response(
                {
                    "detail": "No puedes eliminar una reserva futura o no tienes permiso."
                },
                status=403,
            )
    except Reservas.DoesNotExist:
        return Response({"detail": "Reserva no encontrada."}, status=404)


@api_view(["DELETE"])
def delete_reserva_as_local(request, pk):
    try:
        local = Locales.objects.get(usuario=request.user)
        reserva = Reservas.objects.get(pk=pk, local=local)
        if request.user.is_authenticated and (
            reserva.fecha < timezone.now().date() or reserva.estado == 3
        ):
            reserva.delete()
            return Response({"detail": "Reserva eliminada."}, status=200)
        else:
            return Response(
                {
                    "detail": "No puedes eliminar una reserva futura o no tienes permiso."
                },
                status=403,
            )
    except Reservas.DoesNotExist:
        return Response({"detail": "Reserva no encontrada."}, status=404)


class DetailedUsers(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if self.request.user.is_superuser:
            return Usuarios.objects.get(id=self.kwargs["pk"])
        else:
            if self.request.user.id == self.kwargs["pk"]:
                return self.request.user
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser or user.id == self.request.user.id:
            if user.rol == 4:  # Verificar si el usuario es un empresario
                empresas = Empresas.objects.filter(usuario=user)
                for empresa in empresas:
                    locales = Locales.objects.filter(empresa=empresa)
                    for local in locales:
                        # Eliminar encargados asociados a los locales
                        encargados = Usuarios.objects.filter(locales=local)
                        for encargado in encargados:
                            encargado.delete()
                        local.delete()
                    empresa.delete()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser:
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
                request.data.pop(
                    "password"
                )  # Remove password from request data to avoid rehashing
            return super().update(request, *args, **kwargs)
        else:
            if user.id == self.request.user.id:
                if "password" in request.data:
                    user.set_password(request.data["password"])
                    user.save()
                    request.data.pop("password")
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if self.request.user.is_superuser:
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
                request.data.pop(
                    "password"
                )  # Remove password from request data to avoid rehashing
            return super().partial_update(request, *args, **kwargs)
        else:
            if user.id == self.request.user.id:
                if "password" in request.data:
                    user.set_password(request.data["password"])
                    user.save()
                    request.data.pop("password")
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)


class DetailedFotosLocales(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FotosLocalesSerializer

    def get_object(self):
        local_id = self.kwargs.get("local")
        if local_id:
            local = Locales.objects.get(id=local_id)
            return get_object_or_404(Fotos_Locales, local=local, id=self.kwargs["pk"])
        raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs["local"])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)


class DetailedProductos(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductosSerializer

    def get_object(self):
        local_id = self.kwargs.get("local")
        if local_id:
            local = Locales.objects.get(id=local_id)
            return get_object_or_404(Productos, local=local, id=self.kwargs["pk"])
        raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs["local"])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

@api_view(["GET"])
def get_tramos_horarios_local(request, local):
    try:
        local_obj = Locales.objects.get(id=local, usuario=request.user)
        tramo_horario = Tramos_Horarios.objects.filter(local=local_obj)
    except Tramos_Horarios.DoesNotExist:
        raise JsonResponse({'Tramos horarios not exists'}, status=404)
    return JsonResponse(tramo_horario, status=200)

class DetailedTramosHorarios(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TramosHorariosSerializer

    def get_object(self):
        local_id = self.kwargs.get("local")
        if local_id:
            local = Locales.objects.get(id=local_id)
            return get_object_or_404(Tramos_Horarios, local=local, id=self.kwargs["pk"])
        raise PermissionDenied(GENERIC_ERROR)

    def delete(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.request.user.rol == 3:
                local = Locales.objects.get(id=self.kwargs["local"])
                if self.request.user == local.usuario:
                    self.get_object().delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    raise PermissionDenied(GENERIC_ERROR)
            else:
                raise PermissionDenied(GENERIC_ERROR)

    def update(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)

    def patch(self, request, *args, **kwargs):
        if self.request.user.rol == 3:
            local = Locales.objects.get(id=self.kwargs["local"])
            if self.request.user == local.usuario:
                return super().partial_update(request, *args, **kwargs)
            else:
                raise PermissionDenied(GENERIC_ERROR)
        else:
            raise PermissionDenied(GENERIC_ERROR)


class DetailedEmpresas(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmpresasSerializer

    def get_object(self):
        empresa = get_object_or_404(Empresas, id=self.kwargs["pk"])
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
        if self.request.user.is_superuser or (
            self.request.user.rol == 4 and self.request.user == empresa.usuario
        ):
            locales = Locales.objects.filter(empresa=empresa)
            for local in locales:
                encargados = Usuarios.objects.filter(locales=local)
                for encargado in encargados:
                    encargado.delete()
                local.delete()
            empresa.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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
        serializer = self.get_serializer(empresa, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["GET"])
def get_local(request, id):
    try:
        local = Locales.objects.get(id=id)
    except Locales.DoesNotExist:
        return JsonResponse({"error": "Local not found"}, status=404)

    # Retrieve related data
    fotos = Fotos_Locales.objects.filter(local=local)
    productos = Productos.objects.filter(local=local)
    horarios = Horarios.objects.filter(local=local)
    tramos_horarios = Tramos_Horarios.objects.filter(local=local)
    comentarios = Comentarios.objects.filter(local=local, respuesta=False)

    # Helper function to get nested responses
    def get_respuestas(comentario):
        respuestas = Comentarios.objects.filter(respuesta_a=comentario)
        return [
            {
                "id": respuesta.id,
                "usuario": UsuariosSerializer(respuesta.usuario).data,
                "fecha": respuesta.fecha,
                "comentario": respuesta.comentario,
                "estrellas": respuesta.estrellas,
                "respuesta": respuesta.respuesta,
                "respuestas": get_respuestas(respuesta),  # Recursive call
            }
            for respuesta in respuestas
        ]

    # Prepare data for the response
    fotos_list = [{"id": foto.id, "imagen": foto.imagen.url} for foto in fotos]
    productos_list = [
        {
            "id": producto.id,
            "nombre_producto": producto.nombre_producto,
            "descripcion": producto.descripcion,
            "precio": producto.precio,
            "categoria": producto.categoria,
            "imagen": producto.imagen.url,
        }
        for producto in productos
    ]
    horarios_list = [
        {
            "id": horario.id,
            "hora_apertura": horario.hora_apertura,
            "hora_cierre": horario.hora_cierre,
            "dias": {
                "L": horario.L,
                "M": horario.M,
                "X": horario.X,
                "J": horario.J,
                "V": horario.V,
                "S": horario.S,
                "D": horario.D,
            },
        }
        for horario in horarios
    ]
    tramos_horarios_list = [
        {
            "id": tramo.id,
            "h_inicio": tramo.h_inicio,
            "h_final": tramo.h_final,
            "nombre": tramo.nombre,
            "clientes_maximos": tramo.clientes_maximos,
        }
        for tramo in tramos_horarios
    ]
    comentarios_list = [
        {
            "id": comentario.id,
            "usuario": UsuariosSerializer(comentario.usuario).data,
            "fecha": comentario.fecha,
            "comentario": comentario.comentario,
            "estrellas": comentario.estrellas,
            "respuesta": comentario.respuesta,
            "respuestas": get_respuestas(comentario),
        }
        for comentario in comentarios
    ]

    local_return = {
        "id": local.id,
        "nombre": local.nombre,
        "direccion": local.direccion,
        "categoria_culinaria": (
            {
                "id": local.categoria_culinaria.id,
                "nombre": local.categoria_culinaria.nombre,
                "descripcion": local.categoria_culinaria.descripcion,
            }
            if local.categoria_culinaria
            else None
        ),
        "empresa": (
            {
                "id": local.empresa.id,
                "nombre": local.empresa.nombre,
                "confirmado": local.empresa.confirmado,
                "localNum": local.empresa.locales.count(),
            }
            if local.empresa
            else None
        ),
        "fotos": fotos_list,
        "productos": productos_list,
        "horarios": horarios_list,
        "tramos_horarios": tramos_horarios_list,
        "comentarios": comentarios_list,
    }

    return JsonResponse(local_return, safe=False)


class DetailedCategoriasCulinarias(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoriasCulinariasSerializer

    def get_object(self):
        return get_object_or_404(Categorias_Culinarias, id=self.kwargs["pk"])

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


class ListHorarios(generics.ListCreateAPIView):
    serializer_class = HorariosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        local_id = (
            self.request.user.locales.first().id
            if self.request.user.locales.exists()
            else None
        )
        if local_id:
            return Horarios.objects.filter(local_id=local_id)
        return Horarios.objects.none()

    def perform_create(self, serializer):
        local = self.request.user.locales.first()
        existing_horario = Horarios.objects.filter(local=local).first()
        if existing_horario:
            serializer = self.get_serializer(
                existing_horario, data=self.request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer.save(local=local)


class CrearLocales(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LocalesSerializer

    def perform_create(self, serializer):
        if self.request.user.is_superuser or self.request.user.rol == 4:
            empresa = get_object_or_404(Empresas, usuario=self.request.user)
            if not empresa.confirmado:
                raise PermissionDenied(
                    GENERIC_ERROR
                    + " Espera a que un administrador confirme tu empresa."
                )
            else:
                local = serializer.save(empresa=empresa)
                empresa.localNum += 1
                empresa.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(GENERIC_ERROR)


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


class ListFotosLocales(generics.ListCreateAPIView):
    serializer_class = FotosLocalesSerializer

    def get_queryset(self):
        local_id = self.kwargs.get("local")
        if local_id:
            return Fotos_Locales.objects.filter(local_id=local_id)
        return Fotos_Locales.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif self.request.user.rol == 3:
            local = Locales.objects.get(usuario=self.request.user)
            serializer.save(local=local)
        else:
            raise PermissionDenied(GENERIC_ERROR)


class CrearComentario(generics.CreateAPIView):
    serializer_class = ComentariosSerializer

    def perform_create(self, serializer):
        usuario = self.request.user
        local = get_object_or_404(Locales, id=self.kwargs["local"])
        respuesta_a_id = self.request.data.get("respuesta_a")
        respuesta_a = None
        if respuesta_a_id:
            respuesta_a = get_object_or_404(Comentarios, id=respuesta_a_id)
        serializer.save(local=local, usuario=usuario, respuesta_a=respuesta_a)


class DetailedComentarios(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComentariosSerializer

    def get_object(self):
        comentario = Comentarios.objects.get(id=self.kwargs["pk"])

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
