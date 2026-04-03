import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # WICHTIG
from .models import Message, Project # Importiere deine Models

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("--- RECEIVE START ---")
        data = json.loads(text_data)
        message_text = data.get('message')
        user = self.scope["user"]

        print(f"Empfange: '{message_text}' von User: {user} (ID: {user.id if user.id else 'Keine'})")

        if user.is_authenticated:
            print(f"Versuche Speichern für Projekt ID: {self.project_id}")
            try:
                # Wir warten hier explizit auf das Ergebnis
                saved_msg = await self.save_message(user, self.project_id, message_text)
                print(f"ERFOLG: Nachricht gespeichert mit ID: {saved_msg.id}")
            except Exception as e:
                print(f"FEHLER beim Speichern: {str(e)}")
        else:
            print("WARNUNG: User ist nicht authentifiziert, Speichern übersprungen.")

        # Senden an die Gruppe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'username': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    # Diese Methode speichert die Nachricht in der DB
    @database_sync_to_async
    def save_message(self, user, project_id, message):
        # Wir importieren hier zur Sicherheit lokal, falls es ein Zirkel-Import Problem gibt
        from .models import Message, Project
        
        # Prüfen, ob das Projekt existiert
        try:
            project = Project.objects.get(id=project_id)
            return Message.objects.create(
                project=project,
                sender=user,
                content=message
            )
        except Project.DoesNotExist:
            print(f"KRITISCH: Projekt mit ID {project_id} nicht gefunden!")
            raise