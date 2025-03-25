
from django.urls import path

from printout.views import view_manager, view_pdf

urlpatterns = [
    path('pdf/<int:id>/', view_pdf, name="view_pdf"),
    path('manager/', view_manager,  name="view_manager")
]
