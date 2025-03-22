from django.db import models
from django.forms import ValidationError

from telemetry.traces import get_tracer
import logging

tracer = get_tracer("teams.models")
logger = logging.getLogger("teams.models")

class TeamLocation (models.Model):
    # room identifier
    room = models.IntegerField( verbose_name="room_id" )
    # row in the room
    row = models.IntegerField( verbose_name="row_id" )
    # column in the room
    column = models.IntegerField( verbose_name="column_id" )

    def as_readable_string (self):
        return f"{self.room}.{self.row}.{self.column}"
    def __str__(self):
        return f"<Location {self.as_readable_string()}>"
    def __repr__(self):
        return str(self)
    
    @staticmethod
    def create_location (location: str) -> "TeamLocation":
        with tracer.start_as_current_span("create_location") as span:
            span.set_attribute("location.string", location)

            logger.info(f"Trying to create a TeamLocation from '{location}'")
            words = location.split(".")
            if len(words) != 3:
                logger.critical("The location is invalid, expected three integers '<room>.<row>.<col>'")
                raise ValidationError(f"Invalid location, found '{location}', expected '<room>.<row>.<col>'")

            room_str, row_str, col_str = words

            try:
                room_idx = int(room_str)
                row_idx  = int(row_str)
                col_idx  = int(col_str)
            except Exception:
                logger.critical("The location is invalid, expected three integers '<room>.<row>.<col>'")
                raise ValidationError(f"Invalid location, found '{location}', expected '<room>.<row>.<col>', that should all be integers.")
            span.set_attribute("location.room", room_idx)
            span.set_attribute("location.row", row_idx)
            span.set_attribute("location.col", col_idx)
            
            already_in_db = TeamLocation.objects.filter(room = room_idx, row = row_idx, column = col_idx)
            if len(already_in_db) != 0:
                logger.critical("This location already exists.")
                raise ValidationError(f"Invalid location, the location '{location}' already exists in the database.")
            
            return TeamLocation.objects.create(room = room_idx, row = row_idx, column = col_idx)

class Team (models.Model):
    team_id       = models.IntegerField  ( verbose_name="Team UUID", unique=True )
    team_name     = models.TextField     ( verbose_name="Team Name", unique=True )
    team_location = models.OneToOneField ( TeamLocation, verbose_name="Team Location", on_delete=models.PROTECT )

    @property
    def team_id_readable (self) -> str:
        return f"Team {self.team_id}"
    
    def __str__(self):
        return f"<Team '{self.team_name}' ({self.team_id_readable}) " \
             + f"location={self.team_location.as_readable_string()}>"
    def __repr__(self):
        return str(self)

    @staticmethod
    def create_team (id: int, name: str, location: TeamLocation) -> "Team":
        with tracer.start_as_current_span("create_team") as span:
            logger.info(f"Creating team {id} with name '{name}' and location {location}")

            span.set_attribute("team.id", id)
            span.set_attribute("team.name", name)
            span.set_attribute("team.location", location.as_readable_string())
            
            try:
                return Team.objects.create(
                    team_id = id,
                    team_name = name,
                    team_location = location
                )
            except Exception as exception:
                logger.critical(f"An error occured when creating the team: {exception}")
                raise exception
