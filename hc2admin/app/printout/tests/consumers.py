
from django.test import TestCase
from django.contrib.auth.models import User

from channels.testing import WebsocketCommunicator
import pytest
from hc2admin.asgi import application
from printout.consumers import PrintoutConsumer
from printout.models import Printout, PrintoutStatus
from teams.models import Team, TeamLocation

from asgiref.sync import sync_to_async

class TestPrintoutManagerConsumer (TestCase):
    def setUp(self):
        self.uS = User.objects.create_superuser( "staff", password="staff" )
        self.uP = User.objects.create_superuser( "printer", password="staff" )
        self.uA = User.objects.create_user( "user",  password="user" )

        self.loc  = TeamLocation.create_location("1.6.3")
        self.team = Team.create_team(1, "Team01", self.loc)

        uuid = 0
        def create_printout (user = "", status = PrintoutStatus.RECEIVED):
            nonlocal uuid
            uuid += 1
            return Printout.objects.create(
                team = self.team,
                user = user,
                url  = f"url{uuid}",
                code = f"code{uuid}",
                status = status,
                target = f"target{uuid}"
            )

        self.p1  = create_printout()
        self.p2a = create_printout("pr1",   PrintoutStatus.HAS_STAFF)
        self.p2b = create_printout("staff", PrintoutStatus.HAS_STAFF)
        self.p3  = create_printout("staff", PrintoutStatus.DOWNLOAD)
        self.p4  = create_printout("staff", PrintoutStatus.PRINTED)
        self.p5  = create_printout("staff", PrintoutStatus.SENT_STAFF)
        self.p6  = create_printout("staff", PrintoutStatus.ARRIVED)
        
        return super().setUp()

    def verify_content (self, pk: int, json):
        printout = Printout.objects.get(pk = pk)

        self.assertListEqual(
            [ { "id": printout.pk, "user": printout.user, "team": {
                "team_id": printout.team.team_id,
                "team_name": printout.team.team_name,
                "team_location": printout.team.team_location.as_readable_string()
            } }, printout.status.name ],
            json
        )

    def verify_db (self, array):
        printouts = list( Printout.objects.all() )

        assert len(printouts) == len(array)

        for p, a in zip(printouts, array):
            self.verify_content(p.pk, a)

    async def create_communicator (self, user = None):
        self.communicator = WebsocketCommunicator(application, "ws/printout/admin/")
        if user is not None:
            self.communicator.scope["user"] = user
    async def connect_staff_communicator (self, user = None):
        if user is None:
            user = self.uS
        await self.create_communicator(user)
        connected, _ = await self.communicator.connect()
        assert connected
        return self.communicator
    async def dump_message (self, type):
        message = await self.communicator.receive_json_from()
        assert message['type'] == type
        return message

    async def test_anonymous_connect (self):
        await self.create_communicator()
        
        connected, _ = await self.communicator.connect()

        assert not connected
        await self.communicator.disconnect()
    async def test_standard_connect (self):
        await self.create_communicator(self.uA)
        
        connected, _ = await self.communicator.connect()

        assert not connected
        await self.communicator.disconnect()
    async def test_staff_connect (self):
        await self.create_communicator(self.uS)
        
        connected, _ = await self.communicator.connect()

        assert connected
        await self.communicator.disconnect()
    
    async def test_staff_load_message (self):
        await self.connect_staff_communicator()

        message = await self.communicator.receive_json_from()
        assert message['user'] == 'staff'
        
        await sync_to_async(self.verify_db)(list(reversed(message['data'])))

        await self.communicator.disconnect()
    async def test_staff_update_message (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        self.p4.status = PrintoutStatus.ARRIVED
        await sync_to_async(self.p4.save)()
        await sync_to_async(PrintoutConsumer.on_update)( self.p4 )

        message = await self.dump_message("update")
        await sync_to_async(self.verify_content)(self.p4.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    async def test_staff_new_message (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        self.p7 = await sync_to_async(Printout.objects.create)(
            team = self.team,
            user = "",
            url  = f"url{8}",
            code = f"code{8}",
            status = PrintoutStatus.RECEIVED,
            target = f"target{8}"
        )
        await sync_to_async(PrintoutConsumer.on_new)( self.p7 )

        message = await self.dump_message("new")
        await sync_to_async(self.verify_content)(self.p7.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    
    async def test_staff_send_update (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        await self.communicator.send_json_to({ 'printout': self.p2b.pk, 'status': 'DOWNLOAD' })
        await sync_to_async(self.p2b.refresh_from_db)()
        assert self.p2b.user == "staff"

        message = await self.dump_message("update")
        assert message['status'] == 'DOWNLOAD'
        await sync_to_async(self.verify_content)(self.p2b.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    async def test_staff_send_update_get_ownership (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        await self.communicator.send_json_to({ 'printout': self.p2a.pk, 'status': 'DOWNLOAD' })
        
        message = await self.dump_message("update")
        await sync_to_async(self.p2a.refresh_from_db)()
        assert self.p2a.user == "staff"

        assert message['status'] == 'DOWNLOAD'
        await sync_to_async(self.verify_content)(self.p2a.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    async def test_staff_send_update_get_ownership_of_received (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        await self.communicator.send_json_to({ 'printout': self.p1.pk, 'status': 'HAS_STAFF' })
        
        message = await self.dump_message("update")
        await sync_to_async(self.p1.refresh_from_db)()
        assert self.p1.user == "staff"

        assert message['status'] == 'HAS_STAFF'
        await sync_to_async(self.verify_content)(self.p1.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    
    async def test_staff_send_update_lose_ownership (self):
        await self.connect_staff_communicator()
        _ = await self.dump_message('load')

        await self.communicator.send_json_to({ 'printout': self.p2a.pk, 'status': 'RECEIVED' })
        
        message = await self.dump_message("update")
        await sync_to_async(self.p2a.refresh_from_db)()
        assert self.p2a.user == ""

        assert message['status'] == 'RECEIVED'
        await sync_to_async(self.verify_content)(self.p2a.pk, [ message['printout'], message['status'] ])
        await self.communicator.disconnect()
    async def test_staff_send_update_received_by_everyone (self):
        c1 = await self.connect_staff_communicator()
        c2 = await self.connect_staff_communicator(self.uP)
        await c1.receive_json_from()
        await c2.receive_json_from()
        
        await c2.send_json_to({ 'printout': self.p2b.pk, 'status': 'DOWNLOAD' })

        message = await c1.receive_json_from()
        await sync_to_async(self.p2b.refresh_from_db)()
        assert self.p2b.user == "printer"

        assert message['type'] == 'update'
        assert message['status'] == 'DOWNLOAD'
        await sync_to_async(self.verify_content)(self.p2b.pk, [ message['printout'], message['status'] ])
        
        message = await c2.receive_json_from()
        assert message['type'] == 'update'
        assert message['status'] == 'DOWNLOAD'
        await sync_to_async(self.verify_content)(self.p2b.pk, [ message['printout'], message['status'] ])
        
        await c1.disconnect()
        await c2.disconnect()