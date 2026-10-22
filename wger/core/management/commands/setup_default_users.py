# Django
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# wger
from wger.core.models import (
    UserCache,
    UserProfile,
)
from wger.measurements.models import Category


class Command(BaseCommand):
    help = 'Create or reset default credentials for admin and demo users'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@healthyfy.com',
                'password': 'Admin@12345',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'Healthyfy',
            },
            {
                'username': 'demo',
                'email': 'demo@healthyfy.com',
                'password': 'Demo@12345',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Demo',
                'last_name': 'User',
            },
        ]

        for data in users_data:
            user, created = User.objects.get_or_create(username=data['username'])
            user.email = data['email']
            user.set_password(data['password'])
            user.is_staff = data['is_staff']
            user.is_superuser = data['is_superuser']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.is_active = True
            user.save()

            # Ensure profile exists
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.save()

            # Ensure user cache exists
            UserCache.objects.get_or_create(user=user)

            # Ensure body weight category exists
            try:
                Category.get_or_create_body_weight(user, unit=profile.weight_unit)
            except Exception:
                pass

            # Ensure allauth email address is verified
            email_address, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
            )
            email_address.verified = True
            email_address.primary = True
            email_address.save()

            action = 'Created' if created else 'Reset credentials for'
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} {user.username} (Email: {user.email}, Superuser: {user.is_superuser})"
                )
            )
