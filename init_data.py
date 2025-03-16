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
# from user_profile.models.coach_profile import CoachProfile
# from user_profile.models.customer_profile import CustomerProfile
# from workout.models.workout_schedule import WorkoutSchedule
# from workout.models.workout_goal import WorkoutGoal
# from workout.models.training_plan import TrainingPlan
# from workout.models.exercise import Exercise
# from service.models.service import PTService, NonPTService
# from service.models.service_response import ServiceResponse
# from message.models.message import Message
# from notification.models.notification import Notification
# from notification.models.notification_user import NotificationUser
# from workout.models.category import Category
from django.db import transaction
# from service.models.contract import Contract
from django.db.models import F

from faker import Faker

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
    
    
        


# def create_categories():
#     categories = [
#     "Abductors", "Abs", "Adductors", "Biceps", "Calves", "Chest",
#     "Forearms", "Glutes", "Hamstring", "Hip Flexors", "IT Band",
#     "Lats", "Lower Back", "Upper Back", "Neck", "Obliques",
#     "Palmar Fascia", "Plantar Fascia", "Quads", "Shoulders", "Traps", "Triceps", "Flexibility",
#     "Cardio"
# ]

#     for category_name in categories:
#         category = Category(name=category_name)
#         category.save()
#         print('Create category ' + category_name)


# def create_exercises():
#     category_mapping = {
#         'Push-ups': ['Chest', 'Triceps', 'Shoulders'],
#         'Squats': ['Quads', 'Glutes', 'Hamstring'],
#         'Plank': ['Abs', 'Lower Back'],
#         'Lunges': ['Quads', 'Glutes', 'Hamstring'],
#         'Burpees': ['Abs', 'Chest', 'Shoulders'],
#         'Bench Press': ['Chest', 'Triceps', 'Shoulders'],
#         'Deadlift': ['Hamstring', 'Glutes', 'Lower Back'],
#         'Overhead Press': ['Shoulders', 'Triceps'],
#         'Bicep Curls': ['Biceps'],
#         'Tricep Dips': ['Triceps'],
#         'Leg Press': ['Quads', 'Glutes'],
#         'Leg Curls': ['Hamstring'],
#         'Leg Extensions': ['Quads'],
#         'Calf Raises': ['Calves'],
#         'Chest Fly': ['Chest', 'Shoulders'],
#         'Pull-ups': ['Lats', 'Biceps'],
#         'Chin-ups': ['Lats', 'Biceps'],
#         'Kettlebell Swings': ['Glutes', 'Hamstring', 'Shoulders'],
#         'Mountain Climbers': ['Abs', 'Quads'],
#         'Russian Twists': ['Obliques', 'Abs'],
#         'Box Jumps': ['Quads', 'Glutes', 'Calves'],
#         'Jump Rope': ['Calves', 'Cardio'],
#         'Seated Rows': ['Back', 'Biceps'],
#         'Lat Pulldowns': ['Lats', 'Biceps'],
#         'Face Pulls': ['Rear Deltoids', 'Traps'],
#         'Cable Tricep Extensions': ['Triceps'],
#         'Cable Bicep Curls': ['Biceps'],
#         'Dumbbell Shoulder Press': ['Shoulders', 'Triceps'],
#         'Dumbbell Fly': ['Chest'],
#         'Dumbbell Rows': ['Back', 'Biceps'],
#         'Side Lunges': ['Glutes', 'Quads'],
#         'Hip Thrusts': ['Glutes', 'Hamstring'],
#         'Medicine Ball Slams': ['Abs', 'Obliques', 'Full Body'],
#         'Battle Ropes': ['Cardio'],
#         'Tire Flips': ['Full Body'],
#         'Sled Push': ['Full Body'],
#         'Wall Sit': ['Quads'],
#         'Farmers Walk': ['Grip', 'Forearms'],
#         'Pistol Squats': ['Quads', 'Glutes'],
#         'Single-leg Deadlifts': ['Hamstring', 'Glutes'],
#         'Treadmill Sprints': ['Cardio'],
#         'Stair Climber': ['Cardio'],
#         'Rowing Machine': ['Cardio', 'Back'],
#         'Elliptical Machine': ['Cardio'],
#         'Yoga': ['Flexibility', 'Abs', 'Obliques'],
#         'Pilates': ['Abs', 'Obliques', 'Flexibility'],
#         'Tai Chi': ['Flexibility'],
#         'Core Training': ['Abs', 'Obliques'],
#         'Stretching': ['Flexibility'],
#     }

#     exercises = [
#         {'name': 'Push-ups', 'duration': 10, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Squats', 'duration': 15, 'repetitions': '3x15', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Plank', 'duration': 5, 'repetitions': '3x60s', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Lunges', 'duration': 20, 'repetitions': '3x12 each leg', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Burpees', 'duration': 30, 'repetitions': '5x10', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Bench Press', 'duration': 20, 'repetitions': '3x8', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Deadlift', 'duration': 25, 'repetitions': '3x5', 'image_url': '', 'rest_period': '120 seconds'},
#         {'name': 'Overhead Press', 'duration': 25, 'repetitions': '3x8', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Bicep Curls', 'duration': 15, 'repetitions': '3x12', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Tricep Dips', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Leg Press', 'duration': 20, 'repetitions': '3x10', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Leg Curls', 'duration': 20, 'repetitions': '3x12', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Leg Extensions', 'duration': 15, 'repetitions': '3x12', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Calf Raises', 'duration': 20, 'repetitions': '3x15', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Chest Fly', 'duration': 20, 'repetitions': '3x10', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Pull-ups', 'duration': 20, 'repetitions': '3x5', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Chin-ups', 'duration': 25, 'repetitions': '3x5', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Kettlebell Swings', 'duration': 25, 'repetitions': '3x15', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Mountain Climbers', 'duration': 15, 'repetitions': '3x30s', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Russian Twists', 'duration': 15, 'repetitions': '3x15 each side', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Box Jumps', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Jump Rope', 'duration': 15, 'repetitions': '3x60s', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Seated Rows', 'duration': 20, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Lat Pulldowns', 'duration': 25, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Face Pulls', 'duration': 15, 'repetitions': '3x12', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Cable Tricep Extensions', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Cable Bicep Curls', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Dumbbell Shoulder Press', 'duration': 20, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Dumbbell Fly', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Dumbbell Rows', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Side Lunges', 'duration': 15, 'repetitions': '3x10 each leg', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Hip Thrusts', 'duration': 15, 'repetitions': '3x12', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Medicine Ball Slams', 'duration': 15, 'repetitions': '3x10', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Battle Ropes', 'duration': 20, 'repetitions': '3x30s', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Tire Flips', 'duration': 20, 'repetitions': '3x10', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Sled Push', 'duration': 15, 'repetitions': '3x20m', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Wall Sit', 'duration': 15, 'repetitions': '3x30s', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Farmers Walk', 'duration': 15, 'repetitions': '3x40m', 'image_url': '', 'rest_period': '30 seconds'},
#         {'name': 'Pistol Squats', 'duration': 20, 'repetitions': '3x5 each leg', 'image_url': '', 'rest_period': '90 seconds'},
#         {'name': 'Single-leg Deadlifts', 'duration': 15, 'repetitions': '3x10 each leg', 'image_url': '', 'rest_period': '60 seconds'},
#         {'name': 'Treadmill Sprints', 'duration': 20, 'repetitions': '5x30s', 'image_url': '', 'rest_period': '30 seconds'},
#     ]


#     for exercise_data in exercises:
#         exercise = Exercise(
#             name=exercise_data['name'],
#             duration=exercise_data['duration'],
#             repetitions=exercise_data['repetitions'],
#             image_url=exercise_data['image_url']
#         )
#         exercise.save()
#         print('Created exercise: ' + exercise_data['name'])
        
#         categories = category_mapping.get(exercise_data['name'], [])
#         for category_name in categories:
#             try:
#                 category = Category.objects.get(name=category_name)
#                 exercise.categories.add(category)  
#                 print(f'  - Added category: {category_name}')
#             except Category.DoesNotExist:
#                 print(f'  - Category does not exist: {category_name}')


# def create_workout_schedules():
#     customers = CustomerProfile.objects.all()
#     exercises = Exercise.objects.all()
#     vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

#     for customer in customers:
#         valid_contract = Contract.objects.filter(
#             customer=customer,
#             ptservice__isnull=False,
#             coach__isnull=False,
#             start_date__lte=datetime.now().date(),
#             expire_date__gte=datetime.now().date(),
#             is_purchased=True,
#             used_sessions__lt=F('number_of_session'),
#         ).first()

#         if valid_contract:
#             coach = valid_contract.coach
#             used_sessions = valid_contract.used_sessions
            

#             for i in range(used_sessions):
#                 selected_exercises = random.sample(list(exercises), k=random.randint(5, 7))

#                 training_plan = TrainingPlan.objects.create(
#                     customer=customer,
#                     estimated_duration=random.randint(45, 90), 
#                     overview=f"Giáo án cho buổi tập thứ {i+1}",
#                     note="",
#                 )

#                 training_plan.exercises.set(selected_exercises)
#                 # Vấn đề chọn giờ chọn ngày gây ra giáo án không khớp với buổi tập
#                 # Chọn ngày ngẫu nhiên từ ngày mai đến 10 ngày sau
#                 random_days = random.randint(1, 10)
#                 workout_date = datetime.now().date() + timedelta(days=random_days)

#                 # Đảm bảo thời gian nằm trong khoảng 7h đến 21h
#                 start_hour = random.randint(7, 20)  # Giới hạn start_time từ 7h đến 20h
#                 start_time = datetime.combine(workout_date, datetime.min.time()).replace(hour=start_hour, minute=0)
#                 start_time = vn_tz.localize(start_time)
                
#                 duration = random.randint(45, 90)
#                 end_time = start_time + timedelta(minutes=duration)

#                 with transaction.atomic():  
#                     WorkoutSchedule.objects.create(
#                         customer=customer,
#                         coach=coach,
#                         start_time=start_time,
#                         end_time=end_time,
#                         training_plan=training_plan,
#                     )
                    
#                 print(f"Created workout schedule for customer: {customer} with coach: {coach}")

#         else:
#             print(f"Skipped creating workout schedule for customer: {customer} - No valid PT contract found")


# def create_services(num_service):
#     for i in range(num_service):
#         PTService.objects.create(
#             name=f'Gói tập luyện với PT {i}' ,
#             session_duration=60,
#             cost_per_session=random.randint(300_000, 500_000),
#             validity_period=random.choice([30, 45, 60]),
#         )
#         print(f"Created PT Service {i}")

#     for i in range(num_service):
#         NonPTService.objects.create(
#             name=f'Gói tháng {i}',
#             number_of_month=random.randint(1, 12),
#             cost_per_month=random.randint(300_000, 500_000),
#         )
#         print(f"Created Non PT Service {i}")


# def create_workout_goals(num_records):
#     for _ in range(num_records):
#         WorkoutGoal.objects.create(
#             weight=round(random.uniform(55.0, 90.0), 1),  
#             body_fat=round(random.uniform(10.0, 30.0), 1),  
#             muscle_mass=round(random.uniform(10.0, 20.0), 1),
#         )


# def create_service_responses():
#     contracts = Contract.objects.filter(is_purchased=True)
#     positive_keywords = ["hài lòng", "hữu ích", "tốt", "tiện lợi", "hiệu quả", "thân thiện", "chuyên nghiệp", "sạch sẽ", "thoải mái"]
#     negative_keywords = ["không hài lòng", "chán", "lãng phí", "cũ", "bẩn", "không gọn gàng", "ngột ngạt", "không đủ tiện nghi", "kém chất lượng"]

#     for contract in contracts:
#         customer = contract.customer

#         random_days = random.randint(-20, 20)
#         random_date = timezone.now() + timedelta(days=random_days)

#         random_hour = random.randint(7, 23)  
#         random_minute = random.randint(0, 59) 

#         random_datetime = timezone.make_aware(datetime(
#             year=random_date.year,
#             month=random_date.month,
#             day=random_date.day,
#             hour=random_hour,
#             minute=random_minute
#         ))

#         coach = contract.coach if contract.coach else None

#         if contract.ptservice: 
#             comment = random.choice([
#                 "Buổi tập rất hữu ích, huấn luyện viên hướng dẫn tận tình!",
#                 "Huấn luyện viên rất chuyên nghiệp và có kiến thức.",
#                 "Tôi học được nhiều điều và cảm thấy có động lực.",
#                 "Bài tập khá thử thách nhưng mang lại kết quả tốt.",
#                 "Rất mong đợi buổi tập tiếp theo!",
#                 "Không cảm thấy tiến bộ nhiều, huấn luyện viên chưa sát sao.",
#                 "Bài tập hơi nhàm chán và không phù hợp với tôi.",
#                 "Huấn luyện viên không hướng dẫn kỹ, chưa đạt yêu cầu.",
#                 "Không hài lòng về buổi tập, không như mong đợi.",
#                 "Huấn luyện viên ít quan tâm đến nhu cầu của tôi.",
#                 "Tôi thấy buổi tập phù hợp và hiệu quả.",
#                 "Bài tập thực sự khiến tôi tiến bộ từng ngày!",
#                 "Buổi tập diễn ra rất chuyên nghiệp và hữu ích.",
#                 "Huấn luyện viên thân thiện và hỗ trợ nhiệt tình.",
#                 "Phương pháp tập luyện rõ ràng và hiệu quả.",
#                 "Không có sự đổi mới, buổi tập khá chán.",
#                 "Không thấy sự cải thiện rõ rệt.",
#                 "Cảm thấy mệt mỏi và không đạt hiệu quả.",
#                 "Huấn luyện viên cần nâng cao kỹ năng giảng dạy.",
#                 "Không phù hợp, cảm thấy lãng phí thời gian."
#             ])
#         else:  
#             comment = random.choice([
#                 "Phòng tập sạch sẽ và đầy đủ thiết bị.",
#                 "Cơ sở vật chất rất tốt, tôi thấy hài lòng.",
#                 "Dịch vụ phòng tập đáp ứng nhu cầu của tôi.",
#                 "Tôi thích sự tiện lợi và thoải mái ở đây.",
#                 "Trang thiết bị đa dạng và hiện đại.",
#                 "Phòng tập quá đông, không thể sử dụng thiết bị.",
#                 "Không hài lòng, thiết bị cũ và thiếu nhiều thứ.",
#                 "Nhân viên không thân thiện và hỗ trợ kém.",
#                 "Phòng thay đồ bẩn và không gọn gàng.",
#                 "Không gian phòng tập nhỏ và ngột ngạt.",
#                 "Phòng tập rất sạch sẽ và thoáng mát.",
#                 "Tôi hài lòng với dịch vụ và thái độ nhân viên.",
#                 "Giá cả hợp lý so với chất lượng dịch vụ.",
#                 "Không gian tập luyện tốt và thoải mái.",
#                 "Tôi cảm thấy rất tiện lợi khi tập ở đây.",
#                 "Dịch vụ không tốt, phòng tập không đủ tiện nghi.",
#                 "Không gian không sạch sẽ, thiếu vệ sinh.",
#                 "Trang thiết bị kém chất lượng và thiếu nhiều.",
#                 "Không hài lòng với dịch vụ và cách phục vụ.",
#                 "Phòng tập cần nâng cấp để đáp ứng nhu cầu."
#             ])
#         if any(keyword in comment for keyword in positive_keywords):
#             score = random.randint(4, 5)
#         elif any(keyword in comment for keyword in negative_keywords):
#             score = random.randint(1, 2)
#         else:
#             score = random.randint(3, 4)

#         ServiceResponse.objects.create(
#             customer=customer,
#             coach=coach,  
#             create_date=random_datetime,
#             comment=comment,
#             score=score
#         )
#         print(f"Created service response by customer: {customer.id}")


# def create_messages():
#     coach_messages = [
#         "Hôm nay bạn muốn tập gì? Chúng ta có thể thử một số bài tập mới.",
#         "Tôi thấy bạn tiến bộ rất nhiều, nhưng cần tăng cường sức mạnh cho phần thân trên.",
#         "Cảm ơn bạn đã tham gia buổi tập hôm nay! Hãy nhớ uống đủ nước sau khi tập.",
#         "Hãy thử tăng mức độ bài tập lên một chút, tôi nghĩ bạn có thể làm được!",
#         "Chúc mừng bạn đã đạt được mục tiêu của mình, tiếp tục cố gắng nhé!",
#         "Hôm nay chúng ta sẽ tập các bài tập cardio để cải thiện thể lực chung.",
#         "Bạn cảm thấy như thế nào sau buổi tập hôm qua? Cần giảm độ khó không?",
#         "Mình thấy bạn chưa hoàn thành một số bài tập trong buổi hôm qua, cố gắng hơn nữa nhé!",
#         "Hãy chú ý đến form khi tập, điều này rất quan trọng để tránh chấn thương.",
#         "Hôm nay chúng ta sẽ tập trung vào cơ bụng và chân, tôi nghĩ bạn sẽ thích các bài tập này.",
#         "Nếu cảm thấy quá mệt, hãy giảm cường độ nhưng đừng dừng lại hẳn nhé.",
#         "Hãy chia nhỏ buổi tập thành nhiều phần, như vậy bạn sẽ không cảm thấy quá mệt mỏi.",
#         "Tôi muốn bạn thử tập bài tập này trong tuần, nó sẽ giúp tăng cường sức mạnh cơ thể.",
#         "Bạn cảm thấy như thế nào sau buổi tập kéo dài hôm qua? Chắc chắn đã mệt mỏi!",
#         "Cố gắng giữ thăng bằng trong các bài tập, đừng quên hít thở đều nhé.",
#         "Buổi tập hôm nay có khó khăn gì không? Hãy chia sẻ với tôi để điều chỉnh.",
#         "Tôi rất ấn tượng với sự kiên trì của bạn, cố gắng hơn nữa nhé!",
#         "Tập luyện mỗi ngày sẽ giúp bạn đạt được mục tiêu, hãy tiếp tục như thế này!",
#         "Hãy thử thách bản thân một chút, đừng sợ thất bại, bạn có thể làm được!",
#         "Chúc bạn một buổi tập vui vẻ và hiệu quả!"
#     ]
    
#     customer_messages = [
#         "Tôi cảm thấy khá mệt sau buổi tập hôm qua, nhưng tôi sẽ cố gắng hơn.",
#         "Hôm nay tôi muốn tập bụng và chân, bạn có bài tập nào không?",
#         "Cảm ơn huấn luyện viên đã chỉ dẫn chi tiết hôm nay, tôi sẽ cố gắng hết sức.",
#         "Mức độ bài tập hôm qua có hơi khó, bạn có thể giảm độ khó một chút không?",
#         "Tôi cảm thấy cơ thể mình đang tiến bộ, hy vọng sẽ nhanh chóng đạt được mục tiêu.",
#         "Hôm nay tôi có thể tập những bài tập nào để tăng cường sức mạnh phần thân trên?",
#         "Cảm ơn huấn luyện viên đã khích lệ, tôi rất vui khi thấy sự thay đổi trong cơ thể.",
#         "Tôi cảm thấy khá căng cơ sau buổi tập hôm qua, bạn có bài tập phục hồi nào không?",
#         "Bài tập hôm nay rất thú vị, tôi sẽ thử sức với những bài tập khó hơn.",
#         "Tôi cảm thấy hơi đau ở vai, có cách nào giảm đau không?",
#         "Có thể chỉ tôi cách giữ đúng tư thế khi tập không? Tôi vẫn cảm thấy hơi khó.",
#         "Tôi đã cố gắng hoàn thành hết bài tập, nhưng cảm thấy hơi mệt.",
#         "Cảm ơn bạn đã giúp tôi hoàn thành các bài tập, tôi sẽ cố gắng duy trì luyện tập.",
#         "Tôi đang cố gắng cải thiện sức mạnh, nhưng có vẻ vẫn chưa tiến bộ nhiều.",
#         "Hôm qua tôi tập khá mệt, hôm nay có thể giảm cường độ không?",
#         "Tôi rất thích các bài tập bạn chọn cho tôi, cảm thấy rất hiệu quả.",
#         "Tôi cần giúp đỡ về việc duy trì động lực tập luyện, bạn có lời khuyên nào không?",
#         "Mình cần được động viên để tiếp tục duy trì lịch tập, cảm ơn huấn luyện viên rất nhiều.",
#         "Có thể cho tôi thêm bài tập cardio không? Tôi muốn cải thiện thể lực.",
#         "Hôm nay tôi không thể tập lâu như mọi khi, có thể tập ngắn hơn được không?"
#     ]

#     distinct_pairs = Contract.objects.filter(
#         coach__isnull=False,  
#         customer__isnull=False  
#     ).values('coach_id', 'customer_id').distinct()
#     print(distinct_pairs)

#     for pair in distinct_pairs:
#         coach_id = pair['coach_id']
#         customer_id = pair['customer_id']
        
#         coach = User.objects.get(coach_profile__id=coach_id)
#         customer = User.objects.get(customer_profile__id=customer_id)

#         for i in range(20):  
#             Message.objects.create(
#                 content=random.choice(coach_messages),
#                 sent_at=timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
#                 coach_id=coach,
#                 customer_id=customer,
#                 is_read=random.choice([True, False]),
#                 is_ai=False,
#                 extra_data={}
#             )

#             Message.objects.create(
#                 content=random.choice(customer_messages),
#                 sent_at=timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
#                 coach_id=coach,
#                 customer_id=customer,
#                 is_read=random.choice([True, False]),
#                 is_ai=False,
#                 extra_data={}
#             )

#         print(f"Created 40 messages for customer: {customer} and coach: {coach}")


# def create_notifications(num_notifications):
#     for _ in range(num_notifications):
#         notification = Notification.objects.create(
#             message=fake.sentence(),
#             params={"key": fake.word()},
#             create_url=fake.url(),
#         )

#         users = User.objects.all()
#         for user in users:
#             NotificationUser.objects.create(
#                 notification=notification,
#                 user=user,
#                 is_read=fake.boolean(),  
#                 create_date=timezone.now()
#             )
#         print(f"Created notification number {_}")


# def create_contracts():
#     customers = CustomerProfile.objects.all()

#     for customer in customers:
#         start_date = timezone.now().date()

#         ptservice = None
#         coach = None
#         nonptservice = None
#         no_of_session = None

#         if choice([True, False]):  
#             ptservice = choice(PTService.objects.all())
#             coach = choice(CoachProfile.objects.all())
#         else:
#             nonptservice = choice(NonPTService.objects.all())

#         if ptservice:
#             validity_period = ptservice.validity_period
#             expire_date = start_date + timedelta(days=validity_period)
#             no_of_session = random.randint(15, 20)
#             used_sessions = random.randint(0, round(no_of_session / 2))
#         elif nonptservice:
#             number_of_month = nonptservice.number_of_month
#             expire_date = start_date + timedelta(days=number_of_month * 30)
#             used_sessions = random.randint(0, number_of_month * 30)
#         else:
#             expire_date = start_date

#         contract = Contract(
#             ptservice=ptservice,
#             nonptservice=nonptservice,
#             start_date=start_date,
#             expire_date=expire_date,
#             coach=coach,
#             customer=customer,
#             is_purchased=True,
#             used_sessions=used_sessions,
#             number_of_session=no_of_session,
#         )
#         contract.save()
#         print(f'Created contract for customer {customer.id}')

if __name__ == '__main__':
    # create_services(5)
    create_roles()
    create_users()
    # create_categories()
    # create_exercises()
    # create_service_responses()
    # create_messages()
    # create_notifications(20)
    # create_contracts()
    # create_workout_schedules()
    
    print("Fake data created successfully!")