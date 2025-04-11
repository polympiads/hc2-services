from django_enumfield import enum
from django.db import models

from teams.models import Team
from utils.printrenderer import render_template

from telemetry.traces import get_tracer
import logging

tracer = get_tracer("printout.models")
logger = logging.getLogger("printout.models")

class PrintoutStatus(enum.Enum):
    RECEIVED   = 0 # The status was just received by the hc2admin service
    HAS_STAFF  = 1 # A staff's websocket has started working on it
    DOWNLOAD   = 2 # The staff has downloaded the file
    PRINTED    = 3 # The staff has sent the file to the printer
    SENT_STAFF = 4 # A staff was sent to get the printout
    ARRIVED    = 5 # The printout arrived to the team

class Printout (models.Model):
    team   = models.ForeignKey( Team, verbose_name="Team", on_delete=models.CASCADE )
    user   = models.TextField( default="", verbose_name="" )
    url    = models.TextField( verbose_name="URL" )
    code   = models.TextField( verbose_name="Code" )
    status = enum  .EnumField( PrintoutStatus, verbose_name="Printout Status" )
    target = models.TextField( verbose_name="Bucket Target" )

    @staticmethod
    def create_printout (team: str, url: str, code: str):
        with tracer.start_as_current_span("create_printout") as span:
            span.set_attribute("print.team", team)
            span.set_attribute("print.url", url)
            span.set_attribute("print.content", code)

            if team.startswith("POLYMPIADS"):
                team_objs = Team.objects.filter(team_id = int(team[10:]))
            else:
                team_objs = Team.objects.filter(team_slug=team)
            if len(team_objs) != 1:
                logger.critical(f"Could not find the team with slug '{team}' ({len(team_objs)} != 1).")
                logger.critical(f"Please ask the members of the Technical Committee to manually print.")
                return None
            team_obj = team_objs[0]
            
            target = render_template(
                team_obj.team_id_readable,
                team_obj.team_name,
                team_obj.team_location.as_readable_string(),
                code
            )

            return Printout.objects.create(
                team   = team_obj,
                url    = url,
                code   = code,
                status = PrintoutStatus.RECEIVED,
                target = target
            )
