import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from random import choice
import pytz
import uuid


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from user.models.role import Role
from django.db import transaction
from django.db.models import F
from chat.models.conversation import Conversation
from faker import Faker
from chat.models.message import Message
from service.models.service import Service
from service.models.appointment import Appointment
from service.models.appointment_service import AppointmentService
from service.models.category import Category
from notification.models.notification import Notification
from notification.models.notification_user import NotificationUser
from user.models.car import Car

fake = Faker()
User = get_user_model()


def create_roles():
    roles = [
        {"name": "admin", "permissions": {}},
        {"name": "sale", "permissions": {}},
        {"name": "customer", "permissions": {}},
    ]
    for role_data in roles:
        Role.objects.create(**role_data)


def create_users():
    emails = [
        "kienos.gym@gmail.com",
        "phantuananh170703@gmail.com",
        "hoangdanh.165@gmail.com",
        "huutung2003@gmail.com",
    ]

    emails_customer = [
        "customer1@gmail.com",
        "customer2@gmail.com",
        "customer3@gmail.com",
        "customer4@gmail.com",
        "customer5@gmail.com",
        "customer6@gmail.com",
    ]

    admin_role = Role.objects.filter(name="admin").first()
    customer_role = Role.objects.filter(name="customer").first()

    for email in emails:
        admin_user = User.objects.create_user(
            full_name="ADMINISTRATOR",
            email=email,
            password="12345678",
            is_staff=True,
            is_superuser=True,
            role=admin_role,
        )
        admin_user.save()
        print(f"Created admin user: {email}")

    for email in emails_customer:
        customer_user = User.objects.create_user(
            email=email,
            full_name=fake.name(),
            phone=fake.phone_number(),
            address=fake.address(),
            avatar="https://example.com/avatar.jpg",
            password="12345678",
            is_staff=False,
            is_superuser=False,
            role=customer_role,
        )
        customer_user.save()
        print(f"Created customer user: {email}")


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

    print(f"Created conversations!")


SERVICE_GROUPS = {
    "MAINTENANCE": [
        "Oil Change",
        "Tire Rotation",
        "Brake Inspection",
        "Fluid Flush",
        "Timing Belt Replacement",
        "Wheel Alignment",
    ],
    "REPAIR": [
        "Engine Tune-up",
        "Battery Replacement",
        "Transmission Repair",
        "Suspension Repair",
        "Exhaust System Repair",
        "Clutch Replacement",
        "Fuel Pump Repair",
    ],
    "CARE": [
        "Car Wash",
        "Car Detailing",
        "Air Conditioning Service",
        "Ceramic Coating",
        "Paint Protection",
    ],
    "UPGRADE": [
        "Window Tinting",
        "Sound System Upgrade",
        "Body Kit Installation",
        "LED Headlight Upgrade",
        "Dashcam Installation",
    ],
    "INSPECTION": [
        "Pre-purchase Inspection",
        "General Vehicle Inspection",
        "Emissions Testing",
    ],
    "EXTRA": [
        "Vehicle Pickup & Delivery",
        "Roadside Assistance",
        "Registration Renewal",
    ],
}


def create_service_categories():
    for key in SERVICE_GROUPS.keys():
        category, _ = Category.objects.get_or_create(
            name=key.capitalize(),
            description=f"{key.capitalize()} related services",
        )

        print(f"✅ Created/Found category: {category.name}")


def create_services():
    categories = {
        category.name.upper(): category for category in Category.objects.all()
    }
    services = []

    for category_key, names in SERVICE_GROUPS.items():
        category = categories.get(category_key)
        if not category:
            print(f"❌ Category '{category_key}' not found in DB.")
            continue

        for name in names:
            if category_key == "MAINTENANCE":
                price = random.uniform(30, 100)
                duration = timedelta(hours=random.randint(1, 2))
            elif category_key == "REPAIR":
                price = random.uniform(100, 400)
                duration = timedelta(hours=random.randint(2, 4))
            elif category_key == "CARE":
                price = random.uniform(20, 150)
                duration = timedelta(hours=random.randint(1, 3))
            elif category_key == "UPGRADE":
                price = random.uniform(50, 300)
                duration = timedelta(hours=random.randint(2, 5))
            elif category_key == "INSPECTION":
                price = random.uniform(30, 80)
                duration = timedelta(hours=1)
            elif category_key == "EXTRA":
                price = random.uniform(20, 60)
                duration = timedelta(hours=1)

            service = Service.objects.create(
                name=name,
                description=fake.sentence(nb_words=12),
                price=round(price, 2),
                estimated_duration=duration,
                category=category,
            )
            services.append(service)

            print(
                f"🛠️ Created service: {name} | Price: ${round(price, 2)} | Duration: {duration}"
            )
    print("🎉 All services created successfully!")


def generate_license_plate():
    """Tạo biển số xe ngẫu nhiên theo định dạng ZZY XXX.XX"""
    ma_vung = random.choice(
        [
            "11",
            "12",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",  # Các tỉnh miền núi phía Bắc
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",  # Các tỉnh Đông Bắc
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",  # Hà Nội
            "34",
            "35",
            "36",
            "37",
            "38",  # Bắc Trung Bộ
            "43",
            "92",  # Đà Nẵng
            "47",
            "48",
            "49",  # Tây Nguyên
            "50",
            "51",
            "52",
            "53",
            "54",
            "55",
            "56",
            "57",
            "58",
            "59",  # TP. Hồ Chí Minh
            "60",
            "61",
            "62",
            "63",
            "64",
            "65",  # Đông Nam Bộ (trừ TP.HCM)
            "66",
            "67",
            "68",
            "69",  # Đồng bằng sông Cửu Long
            "80",  # Xe ngoại giao, cơ quan trung ương
        ]
    )
    chu_cai = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    so1 = random.randint(0, 9)
    so2 = random.randint(0, 9)
    so3 = random.randint(0, 9)
    so4 = random.randint(0, 9)
    so5 = random.randint(0, 9)
    return f"{ma_vung}{chu_cai} {so1}{so2}{so3}.{so4}{so5}"


def generate_vin():
    """Tạo số VIN (Vehicle Identification Number) ngẫu nhiên 17 ký tự"""
    characters = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
    vin = "".join(random.choice(characters) for _ in range(17))
    return vin


def generate_car_data():
    """Tạo dữ liệu ngẫu nhiên cho một xe dựa trên Car model"""
    car_brands = [
        "Toyota",
        "Honda",
        "Ford",
        "Hyundai",
        "Kia",
        "Mazda",
        "Mercedes-Benz",
        "BMW",
        "Audi",
    ]
    car_models = {
        "Toyota": ["Vios", "Camry", "Fortuner", "Innova"],
        "Honda": ["City", "Civic", "CR-V", "HR-V"],
        "Ford": ["Ranger", "Everest", "Focus", "Ecosport"],
        "Hyundai": ["Grand i10", "Accent", "Elantra", "Tucson"],
        "Kia": ["Morning", "Cerato", "Seltos", "Sportage"],
        "Mazda": ["Mazda2", "Mazda3", "CX-5", "CX-8"],
        "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC"],
        "BMW": ["3 Series", "5 Series", "X3", "X5"],
        "Audi": ["A3", "A4", "Q3", "Q5"],
    }
    provinces = [
        "Hà Nội",
        "Hồ Chí Minh",
        "Đà Nẵng",
        "Hải Phòng",
        "Cần Thơ",
        "Huế",
        "Nha Trang",
        "Vũng Tàu",
        "Đà Lạt",
        "Quy Nhơn",
    ]
    colors = ["Đỏ", "Xanh", "Trắng", "Đen", "Bạc", "Xám"]
    engine_types = ["Xăng", "Dầu", "Điện", "Hybrid"]

    brand = random.choice(car_brands)
    model = random.choice(car_models[brand])
    year = random.randint(2010, 2024)
    odometer = random.randint(5000, 200000)  # Realistic odometer range in km

    return {
        "name": f"{brand} {model}",
        "brand": f"{brand}",
        "color": random.choice(colors),
        "year": year,
        "engine_type": random.choice(engine_types),
        "current_odometer": odometer,
        "license_plate": generate_license_plate(),
        "registration_province": random.choice(provinces),
        "vin": generate_vin(),
    }


def create_appointments(n=10):
    customers = User.objects.filter(role__name="customer")
    services = list(Service.objects.all())
    today = timezone.now().date()

    if not customers.exists() or not services:
        print("❌ Không có customer hoặc service nào trong DB!")
        return

    car_brands = [
        "Toyota",
        "Honda",
        "Ford",
        "Hyundai",
        "Kia",
        "Mazda",
        "Mercedes-Benz",
        "BMW",
        "Audi",
    ]
    car_models = {
        "Toyota": ["Vios", "Camry", "Fortuner", "Innova"],
        "Honda": ["City", "Civic", "CR-V", "HR-V"],
        "Ford": ["Ranger", "Everest", "Focus", "Ecosport"],
        "Hyundai": ["Grand i10", "Accent", "Elantra", "Tucson"],
        "Kia": ["Morning", "Cerato", "Seltos", "Sportage"],
        "Mazda": ["Mazda2", "Mazda3", "CX-5", "CX-8"],
        "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC"],
        "BMW": ["3 Series", "5 Series", "X3", "X5"],
        "Audi": ["A3", "A4", "Q3", "Q5"],
    }
    provinces = [
        "Hà Nội",
        "Hồ Chí Minh",
        "Đà Nẵng",
        "Hải Phòng",
        "Cần Thơ",
        "Huế",
        "Nha Trang",
        "Vũng Tàu",
        "Đà Lạt",
        "Quy Nhơn",
    ]

    for _ in range(n):
        customer = random.choice(customers)

        start_hour = random.randint(7, 16)
        start_minute = random.choice([0, 15, 30, 45])
        random_date = today + timedelta(days=random.randint(0, 30))

        date = timezone.make_aware(
            datetime.combine(random_date, datetime.min.time()).replace(
                hour=start_hour, minute=start_minute
            )
        )
        total_duration = timedelta()

        service_count = random.randint(3, 6)
        selected_services = random.sample(services, k=min(service_count, len(services)))

        for service in selected_services:
            if isinstance(service.estimated_duration, timedelta):
                duration_minutes = service.estimated_duration.total_seconds() / 60
                total_duration += timedelta(minutes=duration_minutes)

        vehicle_ready_time = date + total_duration

        # Fake data for vehicle_information
        brand = random.choice(car_brands)
        model = random.choice(car_models[brand])
        license_plate_number = generate_license_plate()
        year = random.randint(2015, 2024)
        color = random.choice(["Đỏ", "Xanh", "Trắng", "Đen", "Bạc"])
        province = random.choice(provinces)

        vehicle_information_data = {
            "name": f"{brand} {model}",
            "license_plate_number": license_plate_number,
            "year": year,
            "color": color,
            "registration_province": province,
            "engine_type": random.choice(["Xăng", "Dầu", "Điện", "Hybrid"]),
            "current_odometer": random.randint(10000, 150000),
        }

        appointment = Appointment.objects.create(
            customer=customer,
            date=date,
            vehicle_ready_time=vehicle_ready_time,
            status=random.choice(["pending", "confirmed", "completed", "cancelled"]),
            total_price=0,
            title=f"{customer.full_name}",
            vehicle_information=vehicle_information_data,
        )

        total_price = 0

        for service in selected_services:
            price = service.price
            AppointmentService.objects.create(
                appointment=appointment, service=service, price=price
            )
            total_price += price

        appointment.total_price = total_price
        appointment.save()

        print(
            f"📅 Created appointment {appointment.id} for {customer.email} | {len(selected_services)} services | 💰 {total_price}"
        )


def create_cars_for_customers():
    customers = User.objects.filter(role__name="customer")

    if not customers.exists():
        print("Không có user nào với role customer trong DB!")
        return

    for customer in customers:
        for _ in range(2):  # Create 2 cars per customer
            car_data = generate_car_data()
            car = Car.objects.create(
                user=customer,
                name=car_data["name"],
                brand=car_data["brand"],
                color=car_data["color"],
                year=car_data["year"],
                engine_type=car_data["engine_type"],
                current_odometer=car_data["current_odometer"],
                license_plate=car_data["license_plate"],
                registration_province=car_data["registration_province"],
                vin=car_data["vin"],
            )
            print(
                f"Created car for {customer.email}: {car.name} | "
                f"License: {car.license_plate} | Year: {car.year}"
            )
    print("All cars created successfully!")


def create_notifications(num_notifications):
    for _ in range(num_notifications):
        notification = Notification.objects.create(
            message=fake.sentence(),
            params={"key": fake.word()},
            create_url=fake.url(),
        )

        users = User.objects.all()
        for user in users:
            NotificationUser.objects.create(
                notification=notification,
                user=user,
                is_read=fake.boolean(),
                create_at=timezone.now(),
            )
        print(f"Created notification number {_}")


if __name__ == "__main__":
    # create_roles()
    # create_users()
    # create_conversations()
    # create_service_categories()
    # create_services()
    create_cars_for_customers()
    # create_appointments(10)
    # create_notifications(50)
    print("Fake data created successfully!")
