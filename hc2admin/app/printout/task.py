
import logging
from printout.consumers import PrintoutConsumer
from printout.models import Printout
from utils.printapi import PrinterAPI

from django.conf import settings

from telemetry.traces import get_tracer

tracer = get_tracer("printout.task")
logger = logging.getLogger("printout.task")

def printout_query_task ():
    with tracer.start_as_current_span("query_task") as span:
        api = PrinterAPI(settings.CODEFORCES_PRINTER_TOKEN)
        
        while (entry := api.read_entry()) is not None:
            with tracer.start_as_current_span("found_printout") as fspan:
                fspan.set_attribute("print.team", entry.team)
                fspan.set_attribute("print.url", entry.url)
                fspan.set_attribute("print.content", entry.content)
                
                logger.info(f"Generating printout for team '{entry.team}' out of url '{entry.url}'.")
                
                printout = Printout.create_printout(entry.team, entry.url, entry.content)
                PrintoutConsumer.on_new(printout)
