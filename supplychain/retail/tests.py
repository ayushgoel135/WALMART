from django.test import TestCase
from django.contrib.auth.models import User
from .models import Retailer, Product

class RetailerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='testpass')
        self.retailer = Retailer.objects.create(
            user=self.user,
            company_name="Test Retailer",
            contact_number="1234567890"
        )

    def test_retailer_creation(self):
        self.assertEqual(self.retailer.company_name, "Test Retailer")

class ProductViewTest(TestCase):
    def test_inventory_view(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 302)  # Redirects to login