
from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from teams.models import Team, TeamLocation

from telemetry.traces import get_tracer

import logging

tracer = get_tracer("teams.addteam")
logger = logging.getLogger("teams.addteam")

class Command (BaseCommand):
    help = "Add a team for the Helvetic Coding Contest"

    def add_arguments(self, parser):
        parser.add_argument("id")
        parser.add_argument("name")
        parser.add_argument("location")
    
    @transaction.atomic
    def handle(self, id: str, name: str, location: str, *args, **kwargs):
        with tracer.start_as_current_span("add team") as span:
            span.set_attribute("team.id", id)
            span.set_attribute("team.name", name)
            span.set_attribute("team.location", location)

            logger.info(f"Trying to add a team with id {id}, name '{name}' and location '{location}'")

            try:
                id_int = int(id)
            except Exception:
                logger.critical("The id of the team should be an integer")
                raise CommandError("The id of the team should be an integer.")
            
            try:
                location_obj: TeamLocation = TeamLocation.create_location(location)

                Team.create_team(id_int, name, location_obj)
            except Exception as exception:
                logger.critical("Could not create the team.")
                raise CommandError(str(exception))
