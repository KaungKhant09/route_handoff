from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.models import Session
from .models import PickUpLocation, DropOffLocation, NavigationSession


class PickUpLocationModelTest(TestCase):
    """Test PickUpLocation model."""

    def test_create_pickup_location(self):
        """Test creating a pickup location."""
        location = PickUpLocation.objects.create(
            name="Test Pickup",
            latitude=37.7749,
            longitude=-122.4194
        )
        self.assertEqual(location.name, "Test Pickup")
        self.assertEqual(float(location.latitude), 37.7749)
        self.assertEqual(float(location.longitude), -122.4194)
        self.assertIsNotNone(location.created_at)


class DropOffLocationModelTest(TestCase):
    """Test DropOffLocation model."""

    def test_create_dropoff_location(self):
        """Test creating a dropoff location."""
        location = DropOffLocation.objects.create(
            name="Test Dropoff",
            latitude=37.7849,
            longitude=-122.4094
        )
        self.assertEqual(location.name, "Test Dropoff")
        self.assertEqual(float(location.latitude), 37.7849)
        self.assertEqual(float(location.longitude), -122.4094)


class NavigationSessionModelTest(TestCase):
    """Test NavigationSession model."""

    def setUp(self):
        self.pickup = PickUpLocation.objects.create(
            name="Pickup Point",
            latitude=37.7749,
            longitude=-122.4194
        )
        self.dropoff = DropOffLocation.objects.create(
            name="Dropoff Point",
            latitude=37.7849,
            longitude=-122.4094
        )

    def test_create_navigation_session(self):
        """Test creating a navigation session."""
        session = NavigationSession.objects.create(
            session_key="test_session_key",
            state="no_selection"
        )
        self.assertEqual(session.state, "no_selection")
        self.assertIsNone(session.pickup)
        self.assertIsNone(session.dropoff)

    def test_navigation_session_state_transitions(self):
        """Test navigation session state transitions."""
        session = NavigationSession.objects.create(
            session_key="test_session_key",
            pickup=self.pickup,
            state="pickup_selected"
        )
        self.assertEqual(session.state, "pickup_selected")
        
        session.state = "navigated_to_pickup"
        session.save()
        self.assertEqual(session.state, "navigated_to_pickup")
        
        session.dropoff = self.dropoff
        session.state = "dropoff_selected"
        session.save()
        self.assertEqual(session.state, "dropoff_selected")


class LocationViewsTest(TestCase):
    """Test location CRUD views."""

    def setUp(self):
        self.client = Client()

    def test_pickup_create_view_get(self):
        """Test GET request to pickup create view."""
        response = self.client.get(reverse('routes:pickup_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/location_form.html')

    def test_pickup_create_view_post(self):
        """Test POST request to create pickup location."""
        data = {
            'name': 'Test Pickup',
            'latitude': '37.7749',
            'longitude': '-122.4194'
        }
        response = self.client.post(reverse('routes:pickup_add'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(PickUpLocation.objects.filter(name='Test Pickup').exists())

    def test_pickup_list_view(self):
        """Test pickup list view."""
        PickUpLocation.objects.create(
            name="Pickup 1",
            latitude=37.7749,
            longitude=-122.4194
        )
        response = self.client.get(reverse('routes:pickup_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes/location_list.html')
        self.assertContains(response, "Pickup 1")

    def test_invalid_coordinates(self):
        """Test form validation for invalid coordinates."""
        data = {
            'name': 'Invalid Location',
            'latitude': '100',  # Invalid: > 90
            'longitude': '-122.4194'
        }
        response = self.client.post(reverse('routes:pickup_add'), data)
        self.assertEqual(response.status_code, 200)  # Form errors, not redirect
        self.assertFalse(PickUpLocation.objects.filter(name='Invalid Location').exists())


class NavigationFlowTest(TestCase):
    """Test navigation flow and state management."""

    def setUp(self):
        self.client = Client()
        self.pickup = PickUpLocation.objects.create(
            name="Pickup Point",
            latitude=37.7749,
            longitude=-122.4194
        )
        self.dropoff = DropOffLocation.objects.create(
            name="Dropoff Point",
            latitude=37.7849,
            longitude=-122.4094
        )

    def test_select_locations(self):
        """Test selecting pickup and dropoff locations."""
        # GET request
        response = self.client.get(reverse('routes:select_locations'))
        self.assertEqual(response.status_code, 200)
        
        # POST request to select pickup
        data = {'pickup_id': str(self.pickup.id)}
        response = self.client.post(reverse('routes:select_locations'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check session was created and pickup selected
        session_key = self.client.session.session_key
        nav_session = NavigationSession.objects.get(session_key=session_key)
        self.assertEqual(nav_session.pickup, self.pickup)
        self.assertEqual(nav_session.state, 'pickup_selected')

    def test_navigate_view_requires_pickup(self):
        """Test that navigate view redirects if no pickup selected."""
        response = self.client.get(reverse('routes:navigate_view'))
        self.assertEqual(response.status_code, 302)  # Redirect to select_locations

    def test_navigate_action_updates_state(self):
        """Test that navigate action updates state correctly."""
        # Create session with pickup selected
        session_key = self.client.session.session_key
        nav_session = NavigationSession.objects.create(
            session_key=session_key,
            pickup=self.pickup,
            state='pickup_selected'
        )
        
        # Navigate action
        response = self.client.post(reverse('routes:navigate_action'))
        self.assertEqual(response.status_code, 302)  # Redirect to maps
        
        # Check state updated
        nav_session.refresh_from_db()
        self.assertEqual(nav_session.state, 'navigated_to_pickup')

    def test_start_over_resets_session(self):
        """Test start_over view resets navigation session."""
        session_key = self.client.session.session_key
        nav_session = NavigationSession.objects.create(
            session_key=session_key,
            pickup=self.pickup,
            dropoff=self.dropoff,
            state='navigated_to_dropoff'
        )
        
        response = self.client.get(reverse('routes:start_over'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        nav_session.refresh_from_db()
        self.assertIsNone(nav_session.pickup)
        self.assertIsNone(nav_session.dropoff)
        self.assertEqual(nav_session.state, 'no_selection')


class UtilityFunctionsTest(TestCase):
    """Test utility functions."""

    def setUp(self):
        self.location = PickUpLocation.objects.create(
            name="Test Location",
            latitude=37.7749,
            longitude=-122.4194
        )

    def test_generate_maps_url_mobile(self):
        """Test generating maps URL for mobile."""
        from .utils import generate_maps_url
        urls = generate_maps_url(self.location, is_mobile=True)
        self.assertIn('deep_link', urls)
        self.assertIn('web_fallback', urls)
        self.assertIn('google.navigation', urls['deep_link'])

    def test_generate_maps_url_desktop(self):
        """Test generating maps URL for desktop."""
        from .utils import generate_maps_url
        urls = generate_maps_url(self.location, is_mobile=False)
        self.assertIn('web_fallback', urls)
        self.assertIn('google.com/maps', urls['web_fallback'])

    def test_is_mobile_device(self):
        """Test mobile device detection."""
        from .utils import is_mobile_device
        from django.test import RequestFactory
        
        factory = RequestFactory()
        
        # Mobile user agent
        request = factory.get('/', HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)')
        self.assertTrue(is_mobile_device(request))
        
        # Desktop user agent
        request = factory.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        self.assertFalse(is_mobile_device(request))
