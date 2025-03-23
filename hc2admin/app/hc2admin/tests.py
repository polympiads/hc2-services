
import time
from unittest.mock import Mock, call, patch
from django.test import TestCase

from hc2admin.admin import ReadOnlyAdmin
from hc2admin.tasks import TaskThread, run_task_thread, run_tasks
import printout.task
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

class TestTaskManager (TestCase):
    def test_run_task_thread (self):
        mock = Mock()
        run_task_thread(mock, 0.5)
        time.sleep(1.1)
        TaskThread.join_all()
        assert mock.call_count == 3 # t=0, t=0.5, t=1
    @patch("hc2admin.tasks.run_task_thread")
    def test_run_tasks (self, run_task_thread: Mock):
        run_tasks()
        run_task_thread.assert_called_once_with(printout.task.printout_query_task)