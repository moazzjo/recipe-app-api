"""
Django command to wait for the database to be avalible
"""
from typing import Any
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args: Any):
        pass