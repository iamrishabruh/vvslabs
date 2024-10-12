# user/management/commands/create_userprofiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile instances for users without one.'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        count = users_without_profile.count()

        for user in users_without_profile:
            UserProfile.objects.create(user=user, image='images/users/user.png')
            self.stdout.write(self.style.SUCCESS(f'Created UserProfile for user: {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} UserProfile instances.'))
