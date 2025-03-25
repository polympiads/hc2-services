
from unittest.mock import Mock, call, patch
from django.test import TestCase

from printout.models import Printout, PrintoutStatus
from printout.task import printout_query_task
from django.core.management import call_command
from teams.models import Team
from utils.printapi import PrinterEntry

class TestQueryTask(TestCase):
    def setUp(self):
        call_command("addteam", "1", "Team01", "2.6.3")

        self.team1 = Team.objects.all()[0]
        return 
    @patch("printout.task.PrintoutConsumer")
    @patch("printout.task.PrinterAPI")
    @patch("printout.models.render_template")
    def test_two_prints (self, render_template: Mock, printer_api: Mock, consumer: Mock):
        printer_obj  = printer_api.return_value = Mock()
        read_entry   = printer_obj.read_entry   = Mock()
        on_new       = consumer.on_new          = Mock()

        queue  = [
            PrinterEntry("team01", "url1", "content1"),
            PrinterEntry("team01", "url2", "content2"),
            None
        ]
        offset = 0

        def _read_entry (*args, **kwargs):
            nonlocal queue, offset
            offset += 1

            return queue[offset - 1]
        def _render_template (*args, **kwargs):
            nonlocal offset
            return f"file{offset}.pdf"

        read_entry.side_effect = _read_entry
        render_template.side_effect = _render_template

        printout_query_task()

        assert Printout.objects.count() == 2
        p1, p2 = Printout.objects.all()
        assert p1.code   == "content1"
        assert p1.url    == "url1"
        assert p1.team   == self.team1
        assert p1.status == PrintoutStatus.RECEIVED
        assert p1.target == "file1.pdf"
        assert p2.code   == "content2"
        assert p2.url    == "url2"
        assert p2.team   == self.team1
        assert p2.status == PrintoutStatus.RECEIVED
        assert p2.target == "file2.pdf"

        on_new.assert_has_calls([
            call( p1 ),
            call( p2 )
        ])

    @patch("printout.task.PrintoutConsumer")
    @patch("printout.task.PrinterAPI")
    @patch("printout.models.render_template")
    def test_print_team_does_not_exist (self, render_template: Mock, printer_api: Mock, consumer: Mock):
        printer_obj  = printer_api.return_value = Mock()
        read_entry   = printer_obj.read_entry   = Mock()
        consumer_obj = consumer.return_value    = Mock()
        on_new       = consumer_obj.on_new      = Mock()

        queue  = [
            PrinterEntry("team02", "url1", "content1"),
            None
        ]
        offset = 0

        def _read_entry (*args, **kwargs):
            nonlocal queue, offset
            offset += 1

            return queue[offset - 1]
        def _render_template (*args, **kwargs):
            nonlocal offset
            return f"file{offset}.pdf"

        read_entry.side_effect = _read_entry
        render_template.side_effect = _render_template

        printout_query_task()
        on_new.assert_not_called()
        render_template.assert_not_called()

        assert Printout.objects.count() == 0
        