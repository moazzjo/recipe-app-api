"""
Django command to wait for the database to be avalible
"""
import time
from psycopg2 import OperationalError as psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """ Entrypoint for command"""
        self.stdout.write("wating for Database ...")
        db_up = False
        while db_up is False:
            try:
                self.check(database =['default'])
                db_up = True
            except(psycopg2Error,  OperationalError):
                self.stdout.write('Database unavailble, waiting 1 second ...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Databases available!'))
