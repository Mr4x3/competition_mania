# Python Imports
import base64
from datetime import datetime, timedelta

# Django Imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Third Party Django Imports
from Crypto.Cipher import XOR

# Inter App Imports

# Local Imports


def get_first_and_last_name(name):
    """
    Returns first and last name from a given name
    """
    name = name.strip()
    name_parts = name.split()
    if len(name_parts) > 1:
        first_name = ' '.join(name_parts[:-1])
        last_name = name_parts[-1]
        return first_name, last_name

    dot_parts = name.split('.')
    if len(dot_parts) > 1 and name[-1] != '.':
        first_name = ' '.join(dot_parts[:-1])
        last_name = dot_parts[-1]
        return first_name, last_name

    return name, ''


def encode_token(email, token_type, days=settings.EMAIL_TOKEN_EXPIRY_DAYS_LIMIT, hours=0):
    """
    Encodes token. Used for autologin token in emails
    """

    token_expiry_date = (datetime.now() + timedelta(days=days, hours=hours)).strftime(settings.TOKEN_DATE_FORMAT)

    input_string = '{salt}|{email}|{token_type}|{token_expiry_date}'.format(salt=settings.TOKEN_ENCODE_SALT, email=email, token_type=token_type, token_expiry_date=token_expiry_date)
    input_bytestring = bytes(input_string, 'utf-8')  # Create a Bytestring of Plaintext For Encryption

    xor_cipher = XOR.new(key=settings.TOKEN_ENCODE_SALT)  # Create a Cipher to Encrypt Data
    token = xor_cipher.encrypt(plaintext=input_bytestring)  # Encrypt the Data with the Cipher
    encoded_token = base64.urlsafe_b64encode(token)  # Encode the Token in Base64
    encoded_token = encoded_token.decode('utf-8')  # Convert Bytestring to String
    return encoded_token


def decode_token(token):
    """
    Decodes token.
    token parameter must be in string format.

    Returns:

        token -> (user, token_type, token_expired)
    """
    try:
        token_bytestring = bytes(token, 'utf-8')
        decoded_token = base64.urlsafe_b64decode(token_bytestring)
    except TypeError:
        if '=3D' in token:  # Because = is encoded as =3d
            token = str(token).replace('=3D', '=')
            token_bytestring = bytes(token, 'utf-8')
            decoded_token = base64.urlsafe_b64decode(token_bytestring)
        else:
            return None, None, True

    try:
        xor_cipher = XOR.new(key=settings.TOKEN_ENCODE_SALT)
        input_bytestring = xor_cipher.decrypt(decoded_token)
        input_string = input_bytestring.decode('utf-8')
        input_string_parameters = input_string.split('|')

        email = input_string_parameters[1]
        token_type = int(input_string_parameters[2])
        token_expiry_date = datetime.strptime(input_string_parameters[3], settings.TOKEN_DATE_FORMAT)
        token_expired = token_expiry_date < datetime.now()

        auth_user_model = get_user_model()
        users = list(auth_user_model.objects.filter(email=email))
        if users:
            user = users[0]
            return user, token_type, token_expired
        else:
            return None, None, True

    except:
        # Some Thing Is Wrong with Token
        return None, None, True


def is_token_valid(token):
    user, token_type, token_expired = decode_token(token)
    if not user or token_expired:
        return False
    return True


def send_email_verification_mail(user, host='www.sportsvitae.com'):
    subject = 'Important: Verify Email for your Sportsvitae.com account now'
    context = {
        'user': user,
        'token': encode_token(user.email, 1),
        'host': host
        }
    body = render_to_string('accounts/mailers/email_verification_mail.html', context=context)

    send_mail(subject=subject, message='', from_email='support@sportsvitae.com', recipient_list=[user.email], html_message=body)


def send_forgot_password_mail(user, host='www.sportsvitae.com'):
    subject = 'Sportsvitae.com: Choose a new password'
    context = {
        'user': user,
        'token': encode_token(user.email, 1),
        'host': host
        }
    body = render_to_string('accounts/mailers/forgot_password.html', context=context)

    send_mail(subject=subject, message='', from_email='support@sportsvitae.com', recipient_list=[user.email], html_message=body)


def send_admin_mail_on_user_profile_completion(new_user_email, host='www.sportsvitae.com'):
    subject = '[Important] New User Has Joined!'

    auth_user_model = get_user_model()
    users_count = auth_user_model.objects.filter(is_email_verified=True, registration_midout=False).count()
    body = 'New User email: {} Total Registered Users Currently: {}'.format(new_user_email, users_count)

    send_mail(subject=subject, message='', from_email='root@sportsvitae.com', recipient_list=['care@sportsvitae.com'], html_message=body)
