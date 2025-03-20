import socketio
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from .models import Message



User = get_user_model()

sio = socketio.AsyncServer(cors_allowed_origins="*")  # Cho phép mọi domain kết nối
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"User {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"User {sid} disconnected")

@sio.event
async def send_message(sid, data):
    sender = await get_user(data['sender'])
    receiver = await get_user(data['receiver'])
    message = data['message']

    if sender and receiver:
        chat_message = Message.objects.create(sender=sender, receiver=receiver, message=message)
        await sio.emit("receive_message", {"sender": sender.username, "message": message}, room=data['receiver'])

@sio.event
async def join_room(sid, data):
    room = data['room']
    sio.enter_room(sid, room)
    print(f"User {sid} joined room {room}")

@sio.event
async def leave_room(sid, data):
    room = data['room']
    sio.leave_room(sid, room)
    print(f"User {sid} left room {room}")

async def get_user(user_id):
    try:
        return await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        return None
