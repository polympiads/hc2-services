import json

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from printout.models import Printout, PrintoutStatus

class PrintoutConsumer (WebsocketConsumer):
    channel_group = "group_printout"

    @property
    def user (self) -> User:
        return self.scope['user']
    
    def printout_as_message (self, printout: Printout):
        return [ { "id": printout.pk, "user": printout.user, "team": {
            "team_id": printout.team.team_id,
            "team_name": printout.team.team_name,
            "team_location": printout.team.team_location.as_readable_string()
        } }, printout.status.name ]

    def update_message (self, printout: Printout):
        printout, status = self.printout_as_message(printout)
        return { "type": "update", "printout": printout, "status": status }
    def new_message (self, printout: Printout):
        printout, status = self.printout_as_message(printout)
        return { "type": "new", "printout": printout, "status": status }
    def load_message (self):
        printouts = Printout.objects.all()

        message = []
        for printout in printouts:
            message.append(self.printout_as_message(printout))
        message.reverse()
        return { "type": "load", "data": message, "user": self.user.username }

    def connect(self):
        if not self.user.is_staff:
            return self.close()
        
        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.channel_group, self.channel_name
        )

        self.send( text_data=json.dumps(self.load_message()) )
        
    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)

        pk = data['printout']
        new_status = data['status']

        printout = Printout.objects.get(pk = pk)
        printout.status = PrintoutStatus.get(new_status)

        if printout.status == PrintoutStatus.RECEIVED:
            printout.user = ""
        else:
            printout.user = self.user.username

        printout.save()
        PrintoutConsumer.on_update(printout)

    def printout_change (self, event):
        pk = event['pk']
        printout = Printout.objects.get(pk = pk)
        
        self.send( text_data=json.dumps(self.update_message(printout)) )
    def printout_new (self, event):
        pk = event['pk']
        printout = Printout.objects.get(pk = pk)

        self.send( text_data=json.dumps(self.new_message(printout)) )

    @staticmethod
    def on_update (printout: Printout):
        channel_layer = get_channel_layer()
        async_to_sync(
            channel_layer.group_send
        )(PrintoutConsumer.channel_group, { "type": "printout.change", "pk": printout.pk })
    @staticmethod
    def on_new (printout: Printout):
        channel_layer = get_channel_layer()
        async_to_sync(
            channel_layer.group_send
        )(PrintoutConsumer.channel_group, { "type": "printout.new", "pk": printout.pk })
