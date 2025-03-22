
from django.test import TestCase
from django.core.management import call_command, CommandError

from teams.models import Team, TeamLocation

class AddTeamTest (TestCase):
    def setUp(self):
        loc = TeamLocation.create_location( "2.6.3" )
        tem = Team.create_team( 12, "Nameless Silly Moons", loc )

        self.db_tem = (12, "Nameless Silly Moons", (2, 6, 3))

    def check_db (self, *teams):
        assert TeamLocation.objects.count() == Team.objects.count()

        for team, (id, name, (room, row, col)) in zip(Team.objects.all(), teams):
            assert team.team_name == name
            assert team.team_id == id
            assert team.team_location.room == room
            assert team.team_location.row == row
            assert team.team_location.column == col

            assert str(team.team_location) == repr(team.team_location) == f"<Location {room}.{row}.{col}>"
            assert team.team_location.as_readable_string() == f"{room}.{row}.{col}"
            
            assert team.team_id_readable == f"Team {id}"
            assert str(team) == repr(team) \
                == f"<Team '{name}' (Team {id}) location={team.team_location.as_readable_string()}>"
    def check_default_db (self):
        self.check_db(self.db_tem)

    def test_add_team (self):
        call_command("addteam", "11", "Nameless Funny Moons", "1.4.7")

        self.check_db(
            self.db_tem,
            (11, "Nameless Funny Moons", (1, 4, 7))
        )
    def test_add_team_id_not_int (self):
        with self.assertRaisesMessage(CommandError, "The id of the team should be an integer."):
            call_command("addteam", "1a", "Nameless Funny Moons", "1.4.7")

        self.check_default_db()
    def test_add_team_id_invalid_location (self):
        with self.assertRaisesMessage(CommandError, "Invalid location, found '1.4', expected '<room>.<row>.<col>'"):
            call_command("addteam", "11", "Nameless Funny Moons", "1.4")

        self.check_default_db()
    def test_add_team_id_invalid_location_not_int (self):
        with self.assertRaisesMessage(CommandError, "Invalid location, found '1.4.a', expected '<room>.<row>.<col>', that should all be integers"):
            call_command("addteam", "11", "Nameless Funny Moons", "1.4.a")

        self.check_default_db()
    def test_add_team_id_invalid_location_already_exists (self):
        with self.assertRaisesMessage(CommandError, "Invalid location, the location '2.6.3' already exists in the database."):
            call_command("addteam", "11", "Nameless Funny Moons", "2.6.3")

        self.check_default_db()
    def test_add_team_id_already_exists (self):
        with self.assertRaisesMessage(CommandError, "UNIQUE constraint failed: teams_team.team_id"):
            call_command("addteam", "12", "Nameless Funny Moons", "2.6.4")

        self.check_default_db()
    def test_add_team_name_already_exists (self):
        with self.assertRaisesMessage(CommandError, "UNIQUE constraint failed: teams_team.team_name"):
            call_command("addteam", "11", "Nameless Silly Moons", "2.6.4")

        self.check_default_db()
