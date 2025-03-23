
from django.urls import path

from printout.views import view_pdf

urlpatterns = [
    path('pdf/<int:id>/', view_pdf, name="view_pdf")
]
