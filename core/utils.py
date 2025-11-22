"""
Core utility functions
"""
import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta


def generate_otp(length=6):
    """
    Generate a random OTP code
    """
    return ''.join(random.choices(string.digits, k=length))


def store_otp(activity_id, otp_code, validity_minutes=None):
    """
    Store OTP in Redis cache with expiration
    """
    if validity_minutes is None:
        validity_minutes = settings.OTP_VALIDITY_MINUTES
    
    cache_key = f'otp_activity_{activity_id}'
    timeout = validity_minutes * 60  # Convert to seconds
    
    cache.set(cache_key, otp_code, timeout)
    
    # Store expiration time for display
    expiry_key = f'otp_expiry_{activity_id}'
    expiry_time = datetime.now() + timedelta(minutes=validity_minutes)
    cache.set(expiry_key, expiry_time.isoformat(), timeout)
    
    return expiry_time


def verify_otp(activity_id, otp_code):
    """
    Verify if the OTP code is valid for the activity
    """
    cache_key = f'otp_activity_{activity_id}'
    stored_otp = cache.get(cache_key)
    
    if stored_otp is None:
        return False, "Code OTP expiré ou invalide"
    
    if stored_otp != otp_code:
        return False, "Code OTP incorrect"
    
    return True, "Code OTP valide"


def invalidate_otp(activity_id):
    """
    Invalidate an OTP code
    """
    cache_key = f'otp_activity_{activity_id}'
    expiry_key = f'otp_expiry_{activity_id}'
    cache.delete(cache_key)
    cache.delete(expiry_key)


def get_otp_expiry(activity_id):
    """
    Get OTP expiration time
    """
    expiry_key = f'otp_expiry_{activity_id}'
    expiry_str = cache.get(expiry_key)
    
    if expiry_str:
        return datetime.fromisoformat(expiry_str)
    return None


def send_otp_email(email, otp_code, activity_name):
    """
    Send OTP code via email
    """
    subject = f'Code OTP pour {activity_name}'
    message = f'''
    Bonjour,
    
    Votre code OTP pour l'activité "{activity_name}" est : {otp_code}
    
    Ce code est valide pour {settings.OTP_VALIDITY_MINUTES} minutes (3 heures).
    
    Cordialement,
    L'équipe AESI
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def compress_image(image, max_size=(1920, 1080), quality=85):
    """
    Compress and resize uploaded images
    """
    from PIL import Image
    from io import BytesIO
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import sys
    
    img = Image.open(image)
    
    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Resize if larger than max_size
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image.name.split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output),
        None
    )
