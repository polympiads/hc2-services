
from django.http import FileResponse, HttpResponseForbidden, HttpRequest
from django.shortcuts import get_object_or_404

from printout.models import Printout

def view_pdf (request: HttpRequest, id: int):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    printout = get_object_or_404(Printout, id = id)

    return FileResponse( open(f"./bucket/{printout.target}", "rb"), content_type='application/pdf' )
