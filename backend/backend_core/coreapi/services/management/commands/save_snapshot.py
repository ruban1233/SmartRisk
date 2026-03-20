from django.core.management.base import BaseCommand
from coreapi.services.snapshot_service import save_snapshot


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        save_snapshot("NIFTY")