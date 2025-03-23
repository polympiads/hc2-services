
from django.test import TestCase
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
            assert team.team_slug == "nameless-silly-moons"
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

    def test_team (self):
        self.check_default_db()