from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.timezone import now, timedelta
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from datetime import datetime
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError
import jwt
import requests
from twilio.rest import Client
from django.http import HttpRequest


def send_sms(to_phone_number):

    # The key from one of your Verification Apps, found here https://dashboard.sinch.com/verification/apps
    applicationKey = settings.SINCH_KEY_ID

    # The secret from the Verification App that uses the key above, found here https://dashboard.sinch.com/verification/apps
    applicationSecret = settings.SINCH_KEY_SECRET

    # The number that will receive the SMS. Test accounts are limited to verified numbers.
    # The number must be in E.164 Format, e.g. Netherlands 0639111222 -> +31639111222

    sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications"

    payload = {
        "identity": {
            "type": "number",
            "endpoint": to_phone_number
        },
        "method": "sms"
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        sinchVerificationUrl, 
        json=payload, 
        headers=headers, 
        auth=(applicationKey, applicationSecret)
    )

    data = response.json()
    return data

def verify_sms_code(code, number):

    applicationKey = settings.SINCH_KEY_ID

    applicationSecret = applicationSecret = settings.SINCH_KEY_SECRET

    to_number = number

    code = code

    sinchVerificationUrl = "https://verification.api.sinch.com/verification/v1/verifications/number/" + to_number

    payload = {
        "method": "sms",
        "sms": {
            "code": code
        }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.put(
        sinchVerificationUrl, 
        json=payload, 
        headers=headers, 
        auth=(applicationKey, applicationSecret))

    data = response.json()
    return data

def generate_token(user):
    token_lifetime = datetime.now() + timedelta(hours=3)

    payload = {
        'user_id': str(user.id),
        'exp': token_lifetime
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token, token_lifetime  


def verify_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        user_id = payload['user_id']

        return user_id 
    except ExpiredSignatureError:
        return None  
    except InvalidTokenError:
        return None 

# bỏ, để fe gọi trực tiếp
def validate_email(email):
    api_key = '6b9adf5a-ed37-48bb-99a4-8fedd4103646'  
    url = f'https://api.mails.so/v1/validate?email={email}'
    
    headers = {
        'x-mails-api-key': api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        result = data['data'].get('reason', 'rejected_email')
        return result
    else:
        return None
  

def send_verification_email(user):
    token, token_lifetime = generate_token(user)
    subject = 'Xác nhận email của bạn!'

    default_host = settings.DEFAULT_HOST
    default_scheme = (
        "http"
        if default_host.startswith("localhost") or default_host.startswith("127.0.0.1")
        else "https"
    )

    expiration_time = token_lifetime.strftime("%H:%M %d/%m/%Y")
    
    verification_url = f'{ default_scheme }://{ default_host }/api/v1/users/verify-email?token={token}'
    type_of_action = 'xác thực email'

    html_content = render_to_string('user/email/email_verification.html', {
        'verification_url': verification_url,
        'expiration_time': expiration_time,
        'type_of_action': type_of_action,
    })
    
    text_content = strip_tags(html_content)  
    text_content += f'\n\nXác nhận email: {verification_url}'  

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")  
    email.send()

def send_password_reset_email(user):
    token, token_lifetime = generate_token(user)
    subject = 'Đặt lại mật khẩu của bạn!'
    default_host = settings.DEFAULT_HOST
    default_scheme = (
        "http" if default_host.startswith("localhost") or default_host.startswith("127.0.0.1")
        else "https"
    )
    expiration_time = token_lifetime.strftime("%H:%M %d/%m/%Y")
    type_of_action = 'đặt lại mật khẩu'
    url = f'{default_scheme}://{default_host}/api/v1/users/handle-forgot-password?token={token}'
    
    html_content = render_to_string('user/email/reset-password.html', {
        'url': url,
        'expiration_time': expiration_time,
        'type_of_action': type_of_action,
    })
    
    text_content = strip_tags(html_content)
    text_content += f'\n\nĐặt lại mật khẩu tại: {url}'

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def handle_reset_password():
    pass