from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Usuarios, Empresas, Locales, Reservas, Tramos_Horarios

# Caso de prueba para la creación de usuarios
class UserCreationTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()

    def test_user_creation(self):
        # Datos del nuevo usuario a crear
        data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "tel": "1234-5678901",  # Ajuste el formato del teléfono
            "rol": 2,
            "password": "testpassword",
        }
        # Realiza una solicitud POST para crear el usuario
        response = self.client.post('/api/register', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica que haya un usuario en la base de datos
        self.assertEqual(Usuarios.objects.count(), 1)
        # Verifica que el email del usuario sea el esperado
        self.assertEqual(Usuarios.objects.get().email, 'testuser@example.com')

# Caso de prueba para el login de usuarios
class UserLoginTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario para las pruebas de login
        self.user = Usuarios.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            tel="1234-5678901",
            rol=2,
            password="testpassword"
        )

    def test_user_login(self):
        # Datos de login del usuario
        data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        # Realiza una solicitud POST para hacer login
        response = self.client.post('/api/login', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica que la respuesta contenga un token
        self.assertIn('token', response.data)

# Caso de prueba para la creación de empresas
class EmpresaCreationTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario para asociar con la empresa
        self.user = Usuarios.objects.create_user(
            username="empresario",
            first_name="Empresario",
            last_name="Test",
            email="empresario@example.com",
            tel="1234-5678901",
            rol=4,
            password="testpassword"
        )
        # Autentica el cliente con el usuario creado
        self.client.force_authenticate(user=self.user)

    def test_empresa_creation(self):
        # Datos de la nueva empresa a crear
        data = {
            "nombre": "Mi Empresa",
            "usuario": self.user.id
        }
        # Realiza una solicitud POST para crear la empresa
        response = self.client.post('/api/empresas', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica que haya una empresa en la base de datos
        self.assertEqual(Empresas.objects.count(), 1)
        # Verifica que el nombre de la empresa sea el esperado
        self.assertEqual(Empresas.objects.get().nombre, 'Mi Empresa')

# Caso de prueba para la creación de locales
class LocalCreationTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario para asociar con el local
        self.user = Usuarios.objects.create_user(
            username="empresario",
            first_name="Empresario",
            last_name="Test",
            email="empresario@example.com",
            tel="1234-5678901",
            rol=4,
            password="testpassword"
        )
        # Crea una empresa asociada con el usuario
        self.empresa = Empresas.objects.create(nombre="Mi Empresa", usuario=self.user, confirmado=True)
        # Autentica el cliente con el usuario creado
        self.client.force_authenticate(user=self.user)

    def test_local_creation(self):
        # Datos del nuevo local a crear
        data = {
            "nombre": "Mi Local",
            "direccion": "Calle Falsa 123",
            "categoria_culinaria": None,
            "empresa": self.empresa.id
        }
        # Realiza una solicitud POST para crear el local
        response = self.client.post('/api/crear_local', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica que haya un local en la base de datos
        self.assertEqual(Locales.objects.count(), 1)
        # Verifica que el nombre del local sea el esperado
        self.assertEqual(Locales.objects.get().nombre, 'Mi Local')

# Caso de prueba para la creación de reservas
class ReservaCreationTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario para asociar con la reserva
        self.user = Usuarios.objects.create_user(
            username="cliente",
            first_name="Cliente",
            last_name="Test",
            email="cliente@example.com",
            tel="1234-5678901",
            rol=2,
            password="testpassword"
        )
        # Crea una empresa asociada con el usuario
        self.empresa = Empresas.objects.create(nombre="Mi Empresa", usuario=self.user, confirmado=True)
        # Crea un local asociado con la empresa
        self.local = Locales.objects.create(
            nombre="Mi Local",
            direccion="Calle Falsa 123",
            categoria_culinaria=None,
            empresa=self.empresa
        )
        # Crea un tramo horario asociado con el local
        self.tramo_horario = Tramos_Horarios.objects.create(
            local=self.local,
            h_inicio="12:00:00",
            h_final="14:00:00",
            nombre="Almuerzo",
            clientes_maximos=20
        )
        # Autentica el cliente con el usuario creado
        self.client.force_authenticate(user=self.user)

    def test_reserva_creation(self):
        # Datos de la nueva reserva a crear
        data = {
            "usuario": self.user.id,  # Añadimos el campo usuario
            "local": self.local.id,
            "fecha": "2024-12-31",
            "hora": "12:00:00",
            "tramo_horario": self.tramo_horario.id,
            "estado": 1,
            "numero_personas": 2
        }
        # Realiza una solicitud POST para crear la reserva
        response = self.client.post('/api/reserva/crear', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica que haya una reserva en la base de datos
        self.assertEqual(Reservas.objects.count(), 1)
        # Verifica que el local de la reserva sea el esperado
        self.assertEqual(Reservas.objects.get().local, self.local)

# Caso de prueba para la actualización de usuarios
class UserUpdateTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario para las pruebas de actualización de usuario
        self.user = Usuarios.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            tel="1234-5678901",
            rol=2,
            password="testpassword"
        )
        # Autentica el cliente con el usuario creado
        self.client.force_authenticate(user=self.user)

    def test_user_update(self):
        # Datos a actualizar del usuario
        data = {
            "first_name": "Updated"
        }
        # Realiza una solicitud PATCH para actualizar el usuario
        response = self.client.patch('/api/mi_usuario', data, format='json')
        # Verifica que la respuesta tenga el estado HTTP 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Refresca el usuario desde la base de datos
        self.user.refresh_from_db()
        # Verifica que el nombre del usuario se haya actualizado
        self.assertEqual(self.user.first_name, "Updated")

# Caso de prueba para la eliminación de locales
class LocalDeletionTestCase(TestCase):
    def setUp(self):
        # Configura el cliente de pruebas para la API
        self.client = APIClient()
        # Crea un usuario superusuario para las pruebas de eliminación de local
        self.user = Usuarios.objects.create_user(
            username="superuser",
            first_name="Super",
            last_name="User",
            email="superuser@example.com",
            tel="1234-5678901",
            rol=1,
            password="testpassword",
            is_superuser=True
        )
        # Crea un local para las pruebas de eliminación
        self.local = Locales.objects.create(
            nombre="Local a eliminar",
            direccion="Calle Falsa 123",
            categoria_culinaria=None,
            empresa=None
        )
        # Autentica el cliente con el superusuario
        self.client.force_authenticate(user=self.user)

    def test_local_deletion(self):
        # Realiza una solicitud DELETE para eliminar el local
        response = self.client.delete(f'/api/eliminar_local/{self.local.id}')
        # Verifica que la respuesta tenga el estado HTTP 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verifica que el local se haya eliminado de la base de datos
        self.assertEqual(Locales.objects.count(), 0)
