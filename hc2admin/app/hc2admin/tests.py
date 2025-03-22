
from django.test import TestCase

from hc2admin.admin import ReadOnlyAdmin
from teams.models import Team

class TestReadonlyAdmin(TestCase):
    def setUp(self):
        self.admin = ReadOnlyAdmin(Team, None)
    def test_has_add_permission(self, *args, **kwargs):
        assert not self.admin.has_add_permission()
    def test_has_delete_permission(self, *args, **kwargs):
        assert not self.admin.has_delete_permission()
    def test_has_change_permission(self, *args, **kwargs):
        assert not self.admin.has_change_permission()
