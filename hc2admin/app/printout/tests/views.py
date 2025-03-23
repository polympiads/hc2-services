
from unittest.mock import Mock, patch
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase, Client
from django.contrib.auth.models import User

from printout.models import Printout, PrintoutStatus
from teams.models import Team, TeamLocation

def patch_test_view (func):
    @patch("printout.views.open")
    @patch("printout.views.FileResponse")
    def patched (self, file_response: Mock, open: Mock):
        open.return_value = Mock()
        file_response.return_value = HttpResponse("")
        func(self, open, open.return_value, file_response, file_response.return_value)
    patched.__name__ = func.__name__
    patched.__qualname__ = func.__qualname__
    return patched

class TestViewPDF (TestCase):
    def setUp (self):
        self.uS = User.objects.create_superuser( "staff", password="staff" )
        self.uA = User.objects.create_user( "user",  password="user" )

        self.cli_anonymous = Client()
        self.cli_standard  = Client()
        self.cli_standard.login(username="user", password="user")
        self.cli_staff = Client()
        self.cli_staff.login(username="staff", password="staff")

        self.location = TeamLocation.objects.create(room=1, row=1, column=1)
        self.team = Team.objects.create(team_name="name", team_id=1, team_location=self.location)
        self.printout = Printout.objects.create(
            team = self.team,
            url  = "url",
            status = PrintoutStatus.RECEIVED,
            target = "target",
            code  = "content"
        )

    @patch_test_view
    def test_anonymous (self, open: Mock, open_result: Mock, file_response: Mock, file_response_result: Mock):
        response = self.cli_anonymous.get("/printout/pdf/1/")
        
        assert isinstance(response, HttpResponseForbidden)
    @patch_test_view
    def test_normal_user (self, open: Mock, open_result: Mock, file_response: Mock, file_response_result: Mock):
        response = self.cli_standard.get("/printout/pdf/1/")
        
        assert isinstance(response, HttpResponseForbidden)
    @patch_test_view
    def test_staff_user (self, open: Mock, open_result: Mock, file_response: Mock, file_response_result: Mock):
        response = self.cli_staff.get("/printout/pdf/1/")
        
        open.assert_called_once_with(f"./bucket/target", "rb")
        file_response.assert_called_once_with(open_result, content_type="application/pdf")
        assert response is file_response_result
    @patch_test_view
    def test_staff_user_no_pdf (self, open: Mock, open_result: Mock, file_response: Mock, file_response_result: Mock):
        response = self.cli_staff.get("/printout/pdf/2/")
        assert isinstance(response, HttpResponseNotFound)