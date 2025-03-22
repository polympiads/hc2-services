
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

from telemetry.traces import get_tracer
import logging
import csv

tracer = get_tracer("teams.loadteamscsv")
logger = logging.getLogger("teams.loadteamscsv")

class Command (BaseCommand):
    help = "Load a CSV of teams for the helvetic coding contest"

    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    @transaction.atomic
    def handle(self, csvfile: str, *args, **options):
        with tracer.start_as_current_span("load_teams") as span:
            logger.info(f"Trying to load the teams from '{csvfile}'")
            with open(csvfile, "r") as file:
                reader = csv.reader(file)
                
                for row in reader:
                    call_command("addteam", *row)
