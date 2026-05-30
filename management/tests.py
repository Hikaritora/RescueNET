from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from management.models import Incident, Resource, User
from management.forms import IncidentForm, ResourceForm

class UserModelTests(TestCase):
    """Test the User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='dispatcher'
        )

    def test_user_creation(self):
        """Test creating a user"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'dispatcher')

    def test_user_model_table_name(self):
        """Test that User model uses correct database table"""
        self.assertEqual(User._meta.db_table, 'management_user')

    def test_user_str_method(self):
        """Test User __str__ method"""
        expected = f"{self.user.username} (dispatcher)"
        self.assertIn('testuser', str(self.user))

    def test_auth_user_model_configured(self):
        """Test AUTH_USER_MODEL is set correctly"""
        AuthUser = get_user_model()
        self.assertEqual(AuthUser, User)


class IncidentModelTests(TestCase):
    """Test the Incident model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='reporter',
            password='pass123',
            role='rescuer'
        )
        self.incident = Incident.objects.create(
            type='Fire',
            latitude=51.1079,
            longitude=17.0385,
            priority='high',
            status='reported',
            reporter=self.user,
            notes='Test incident'
        )

    def test_incident_creation(self):
        """Test creating an incident"""
        self.assertEqual(self.incident.type, 'Fire')
        self.assertEqual(self.incident.priority, 'high')
        self.assertEqual(self.incident.status, 'reported')

    def test_incident_model_table_name(self):
        """Test that Incident model uses correct database table"""
        self.assertEqual(Incident._meta.db_table, 'management_incident')

    def test_incident_reporter_relationship(self):
        """Test Incident FK to User"""
        self.assertEqual(self.incident.reporter, self.user)

    def test_incident_str_method(self):
        """Test Incident __str__ method"""
        incident_str = str(self.incident)
        self.assertIn('Incident', incident_str)
        self.assertIn('Fire', incident_str)

    def test_incident_meta_index(self):
        """Test that Incident has status index"""
        indexes = Incident._meta.indexes
        self.assertTrue(any('status' in index.fields for index in indexes))


class ResourceModelTests(TestCase):
    """Test the Resource model"""

    def setUp(self):
        self.resource = Resource.objects.create(
            name='Ambulance-1',
            type='Ambulance',
            specialization='Life Support',
            status='available',
            latitude=51.1079,
            longitude=17.0385
        )

    def test_resource_creation(self):
        """Test creating a resource"""
        self.assertEqual(self.resource.name, 'Ambulance-1')
        self.assertEqual(self.resource.type, 'Ambulance')
        self.assertEqual(self.resource.status, 'available')

    def test_resource_model_table_name(self):
        """Test that Resource model uses correct database table"""
        self.assertEqual(Resource._meta.db_table, 'management_resource')

    def test_resource_str_method(self):
        """Test Resource __str__ method"""
        self.assertEqual(str(self.resource), 'Ambulance-1')

    def test_resource_meta_index(self):
        """Test that Resource has status index"""
        indexes = Resource._meta.indexes
        self.assertTrue(any('status' in index.fields for index in indexes))


class ForeignKeyRelationshipTests(TestCase):
    """Test ForeignKey relationships between models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='dispatcher',
            password='pass123',
            role='dispatcher'
        )
        self.incident = Incident.objects.create(
            type='Medical Emergency',
            latitude=51.1079,
            longitude=17.0385,
            priority='critical',
            status='reported',
            reporter=self.user
        )
        self.resource = Resource.objects.create(
            name='Ambulance-A',
            type='Ambulance',
            status='available',
            assigned_to=self.incident
        )

    def test_incident_reporter_fk(self):
        """Test Incident.reporter ForeignKey works"""
        self.assertEqual(self.incident.reporter, self.user)

    def test_resource_assigned_to_fk(self):
        """Test Resource.assigned_to ForeignKey works"""
        self.assertEqual(self.resource.assigned_to, self.incident)

    def test_incident_assigned_resources_reverse(self):
        """Test reverse relationship: Incident.assigned_resources"""
        assigned = self.incident.assigned_resources.all()
        self.assertIn(self.resource, assigned)


class IncidentViewAuthTests(TestCase):
    """Test incident views with authentication"""

    def setUp(self):
        self.client = Client()
        self.dispatcher = User.objects.create_user(
            username='dispatcher',
            password='testpass123',
            role='dispatcher'
        )
        self.rescuer = User.objects.create_user(
            username='rescuer',
            password='testpass123',
            role='rescuer'
        )
        self.incident = Incident.objects.create(
            type='Fire',
            latitude=51.1079,
            longitude=17.0385,
            priority='high',
            status='reported',
            reporter=self.dispatcher
        )

    def test_incident_list_view_unauthenticated(self):
        """Test incident list returns 200 without login (public view)"""
        response = self.client.get(reverse('incident_list'))
        self.assertEqual(response.status_code, 200)

    def test_incident_detail_view_authenticated(self):
        """Test incident detail view with authenticated user"""
        self.client.force_login(self.dispatcher)
        response = self.client.get(reverse('incident_detail', args=[self.incident.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_incident_requires_dispatcher(self):
        """Test create_incident redirects non-dispatcher"""
        # As rescuer (not dispatcher)
        self.client.force_login(self.rescuer)
        response = self.client.get(reverse('create_incident'))
        # user_passes_test redirects to login (302) even for authenticated users
        self.assertEqual(response.status_code, 302)

    def test_create_incident_dispatcher_access(self):
        """Test dispatcher can access create_incident view"""
        self.client.force_login(self.dispatcher)
        response = self.client.get(reverse('create_incident'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        """Test dashboard redirects unauthenticated user"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        """Test dashboard loads for authenticated user"""
        self.client.force_login(self.dispatcher)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class ResourceViewAuthTests(TestCase):
    """Test resource views with authentication"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='rescuer'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )
        self.resource = Resource.objects.create(
            name='Fire-Truck-1',
            type='Fire Truck',
            status='available'
        )

    def test_resource_list_requires_login(self):
        """Test resource list redirects unauthenticated user"""
        response = self.client.get(reverse('resource_list'))
        self.assertEqual(response.status_code, 302)

    def test_resource_list_authenticated(self):
        """Test resource list loads for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('resource_list'))
        self.assertEqual(response.status_code, 200)

    def test_add_resource_requires_admin(self):
        """Test add_resource redirects non-admin"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('add_resource'))
        self.assertEqual(response.status_code, 302)

    def test_add_resource_admin_access(self):
        """Test admin can access add_resource view"""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('add_resource'))
        self.assertEqual(response.status_code, 200)


class FormTests(TestCase):
    """Test form classes"""

    def test_incident_form_valid(self):
        """Test IncidentForm with valid data"""
        form = IncidentForm(data={
            'type': 'Fire',
            'priority': 'high',
            'latitude': '51.1079',
            'longitude': '17.0385',
            'notes': 'Test notes'
        })
        self.assertTrue(form.is_valid())

    def test_incident_form_missing_required_field(self):
        """Test IncidentForm with missing required field"""
        form = IncidentForm(data={
            'type': 'Fire',
            'priority': 'high',
            # missing latitude, longitude, notes
        })
        self.assertFalse(form.is_valid())

    def test_resource_form_valid(self):
        """Test ResourceForm with valid data"""
        form = ResourceForm(data={
            'name': 'Ambulance-999',
            'type': 'Ambulance',
            'specialization': '',
            'latitude': '51.1079',
            'longitude': '17.0385'
        })
        self.assertTrue(form.is_valid())


class AdminRegistrationTests(TestCase):
    """Test that models are registered in Django admin"""

    def test_user_registered_in_admin(self):
        """Test User is registered in Django admin"""
        from django.contrib import admin
        self.assertTrue(admin.site.is_registered(User))

    def test_incident_registered_in_admin(self):
        """Test Incident is registered in Django admin"""
        from django.contrib import admin
        self.assertTrue(admin.site.is_registered(Incident))

    def test_resource_registered_in_admin(self):
        """Test Resource is registered in Django admin"""
        from django.contrib import admin
        self.assertTrue(admin.site.is_registered(Resource))


class DataIntegrityTests(TestCase):
    """Test maintaining data integrity after migrations"""

    def test_can_query_users(self):
        """Test User model queries work"""
        User.objects.create_user('user1', 'pass1', role='dispatcher')
        User.objects.create_user('user2', 'pass1', role='rescuer')

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.filter(role='dispatcher').count(), 1)

    def test_can_query_incidents(self):
        """Test Incident model queries work"""
        user = User.objects.create_user('user', 'pass', role='rescuer')
        Incident.objects.create(
            type='Fire',
            latitude=51.1079,
            longitude=17.0385,
            priority='high',
            reporter=user
        )

        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(Incident.objects.filter(priority='high').count(), 1)

    def test_can_query_resources(self):
        """Test Resource model queries work"""
        Resource.objects.create(
            name='Resource-1',
            type='Ambulance',
            status='available'
        )
        Resource.objects.create(
            name='Resource-2',
            type='Fire Truck',
            status='unavailable'
        )

        self.assertEqual(Resource.objects.count(), 2)
        self.assertEqual(Resource.objects.filter(status='available').count(), 1)
