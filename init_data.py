import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from random import choice
import pytz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from user.models.role import Role
from django.db import transaction
from django.db.models import F
from chat.models.conversation import Conversation
from faker import Faker
from chat.models.message import Message
import uuid
fake = Faker()
User = get_user_model()


def create_roles():
    roles = [
        {'name': 'admin', 'permissions': {}},
        {'name': 'sale', 'permissions': {}},
        {'name': 'customer', 'permissions': {}},
    ]
    for role_data in roles:
        Role.objects.create(**role_data)


def create_users():
    emails = [
        'kienos.gym@gmail.com',
        'phantuananh170703@gmail.com',
        'hoangdanh.165@gmail.com',
        'huutung2003@gmail.com'
    ]

    admin_role = Role.objects.filter(name='admin').first()

    for email in emails:
        admin_user = User.objects.create_user(
            email=email,
            password='12345678',
            is_staff=True,
            is_superuser=True,
            role=admin_role
        )
        admin_user.save()
        print(f"Created admin user: {email}")
    
def create_conversations():
    my_user_id = "a711dca6-a6a6-4976-b5a6-331b71624123"
    try:
        me = User.objects.get(id=my_user_id)
    except User.DoesNotExist:
        print(f"❌ Không tìm thấy user với ID {my_user_id}")
        return

    other_users = list(User.objects.exclude(id=my_user_id))

    if len(other_users) < 3:
        print("❌ Không đủ 5 người khác để tạo cuộc trò chuyện!")
        return

    selected_users = random.sample(other_users, 3)  # Chọn 5 người bất kỳ
    created_conversations = []

    for user in selected_users:
        conversation = Conversation.objects.create()
        conversation.participants.set([me, user])

        # 📝 Tạo 10 tin nhắn ngẫu nhiên
        messages = []
        for _ in range(10):
            sender = random.choice([me, user])
            receiver = me if sender == user else user

            message = Message.objects.create(
                id=uuid.uuid4(),
                conversation=conversation,
                sender=sender,
                receiver=receiver,
                message=f"Tin nhắn test từ {sender.email}",
                message_type="text",
                status=random.choice(["sent", "received", "seen"]),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            messages.append(message)

        # Cập nhật tin nhắn cuối cùng trong conversation
        conversation.last_message = messages[-1].message
        conversation.last_sender = sender
        conversation.save()

        created_conversations.append(conversation)

    print(f"✅ Đã tạo {len(created_conversations)} cuộc trò chuyện giữa mày và 5 người khác, mỗi cuộc có 10 tin nhắn!")
        
if __name__ == '__main__':
    # create_roles()
    # create_users()
    create_conversations()
    print("Fake data created successfully!")