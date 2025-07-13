from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from retail.models import Retailer

class Command(BaseCommand):
    help = 'Creates retailer profiles for existing users'

    def handle(self, *args, **options):
        users_without_retailer = User.objects.filter(retailer__isnull=True)
        
        for user in users_without_retailer:
            Retailer.objects.create(
                user=user,
                company_name=f"{user.username}'s Store",
                address="Please update your address",
                contact_number="0000000000"
            )
            self.stdout.write(f'Created retailer for {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully processed all users'))