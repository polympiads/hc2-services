
import csv
from io import StringIO
from unittest.mock import Mock, patch, call
from django.test import TestCase
from functools import wraps
from django.core.management import call_command, CommandError

def using_config (*teams):
    csv_target = StringIO()
    csv_writer = csv.writer( csv_target )
    csv_writer.writerows( teams )

    csv_data = csv_target.getvalue()

    def decorator (func):
        @patch("teams.management.commands.loadteamscsv.call_command")
        @patch("teams.management.commands.loadteamscsv.open")
        def wrapped (self, *args, **kwargs):
            open, call_command = args[-2:]
            open.return_value = StringIO(csv_data)
            func(self, call_command, open, *args[:-2], **kwargs)
        wrapped.__name__ = func.__name__
        wrapped.__qualname__ = func.__qualname__
        return wrapped
    return decorator

class LoadTeamCSVTestCase (TestCase):
    @using_config()
    def test_empty_csv (self, _call_command: Mock, open: Mock):
        call_command("loadteamscsv", "example.csv")

        _call_command.assert_not_called()
        open.assert_called_once_with("example.csv", "r")
    @using_config(
        ("1","Nameless Silly Moons","2.6.3"),
        ("2","Nameless Funny Moons","2.6.4"),
        ("3","Nameless Happy Moons","1.4.1")
    )
    def test_example_csv (self, _call_command: Mock, open: Mock):
        call_command("loadteamscsv", "example.csv")
        
        _call_command.assert_has_calls([
            call("addteam","1","Nameless Silly Moons","2.6.3"),
            call("addteam","2","Nameless Funny Moons","2.6.4"),
            call("addteam","3","Nameless Happy Moons","1.4.1")
        ])
        open.assert_called_once_with("example.csv", "r")
