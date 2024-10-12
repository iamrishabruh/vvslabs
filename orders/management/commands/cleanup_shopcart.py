# orders/management/commands/cleanup_shopcart.py

from django.core.management.base import BaseCommand
from orders.models import ShopCart

class Command(BaseCommand):
    help = 'Cleans up ShopCart entries with missing or deleted products.'

    def handle(self, *args, **kwargs):
        orphaned_entries = ShopCart.objects.filter(product__isnull=True)
        count = orphaned_entries.count()

        orphaned_entries.delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} orphaned ShopCart entries.'))
