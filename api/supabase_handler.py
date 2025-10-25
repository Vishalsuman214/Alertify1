from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import datetime

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')

supabase: Client = None

def get_supabase_client():
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def read_users():
    response = get_supabase_client().table('users').select('*').execute()
    return response.data

def write_users(users):
    # This function is not needed in Supabase, but kept for compatibility
    pass

def add_user(email, password):
    # Check if user already exists
    existing_user = get_supabase_client().table('users').select('*').eq('email', email).execute()
    if existing_user.data:
        return None

    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)

    user_data = {
        'id': user_id,
        'email': email,
        'password_hash': password_hash,
        'is_email_confirmed': True,
        'verification_token': '',
        'reset_token': '',
        'reset_token_expiry': '',
        'profile_picture': '',
        'bio': '',
        'email_credentials': '',
        'app_password': ''
    }

    response = get_supabase_client().table('users').insert(user_data).execute()
    return user_id if response.data else None

def get_user_by_email(email):
    response = get_supabase_client().table('users').select('*').eq('email', email).execute()
    return response.data[0] if response.data else None

def get_user_by_id(user_id):
    response = get_supabase_client().table('users').select('*').eq('id', user_id).execute()
    return response.data[0] if response.data else None

def update_user_password(user_id, new_password_hash):
    response = get_supabase_client().table('users').update({'password_hash': new_password_hash}).eq('id', user_id).execute()
    return len(response.data) > 0

def update_user_profile_picture(user_id, filename):
    response = get_supabase_client().table('users').update({'profile_picture': filename}).eq('id', user_id).execute()
    return len(response.data) > 0

def update_user_bio(user_id, bio):
    response = get_supabase_client().table('users').update({'bio': bio}).eq('id', user_id).execute()
    return len(response.data) > 0

def update_user_email_credentials(user_id, email, app_password):
    response = get_supabase_client().table('users').update({'email_credentials': email, 'app_password': app_password}).eq('id', user_id).execute()
    return len(response.data) > 0

def update_user_reminder_email(user_id, email):
    response = get_supabase_client().table('users').update({'reminder_email': email}).eq('id', user_id).execute()
    return len(response.data) > 0

def update_user_reminder_app_password(user_id, app_password):
    response = get_supabase_client().table('users').update({'reminder_app_password': app_password}).eq('id', user_id).execute()
    return len(response.data) > 0

def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)

# Stub functions for removed email verification features
def generate_verification_token(email):
    return str(uuid.uuid4())

def set_verification_token(user_id, token):
    pass

def verify_email(token):
    return True

def generate_reset_token(email):
    return str(uuid.uuid4())

def set_reset_token(user_id, token, expiry):
    response = get_supabase_client().table('users').update({'reset_token': token, 'reset_token_expiry': str(expiry)}).eq('id', user_id).execute()
    return len(response.data) > 0

def reset_password(token, new_password):
    response = get_supabase_client().table('users').update({'password_hash': generate_password_hash(new_password), 'reset_token': '', 'reset_token_expiry': ''}).eq('reset_token', token).execute()
    return len(response.data) > 0

# Reminder functions
def get_all_reminders():
    response = get_supabase_client().table('reminders').select('*').execute()
    return response.data

def mark_reminder_completed(reminder_id, completed=True):
    response = get_supabase_client().table('reminders').update({'is_completed': completed}).eq('id', reminder_id).execute()
    return len(response.data) > 0

def add_reminder(user_id, title, description, reminder_time, recipient_email):
    reminder_id = str(uuid.uuid4())
    reminder_data = {
        'id': reminder_id,
        'user_id': user_id,
        'title': title,
        'description': description,
        'reminder_time': reminder_time.strftime('%Y-%m-%d %H:%M:%S'),
        'recipient_email': recipient_email,
        'is_completed': False
    }

    response = get_supabase_client().table('reminders').insert(reminder_data).execute()
    return reminder_id if response.data else None

def get_reminders_by_user_id(user_id):
    response = get_supabase_client().table('reminders').select('*').eq('user_id', user_id).execute()
    return response.data

def get_reminder_by_id(reminder_id):
    response = get_supabase_client().table('reminders').select('*').eq('id', reminder_id).execute()
    return response.data[0] if response.data else None

def update_reminder(reminder_id, title=None, description=None, reminder_time=None, recipient_email=None, is_completed=None):
    update_data = {}
    if title is not None:
        update_data['title'] = title
    if description is not None:
        update_data['description'] = description
    if reminder_time is not None:
        update_data['reminder_time'] = reminder_time.strftime('%Y-%m-%d %H:%M:%S')
    if recipient_email is not None:
        update_data['recipient_email'] = recipient_email
    if is_completed is not None:
        update_data['is_completed'] = is_completed

    if update_data:
        response = get_supabase_client().table('reminders').update(update_data).eq('id', reminder_id).execute()
        return len(response.data) > 0
    return False

def delete_reminder(reminder_id):
    response = get_supabase_client().table('reminders').delete().eq('id', reminder_id).execute()
    return len(response.data) > 0

def delete_all_reminders_by_user(user_id):
    # Soft delete all reminders by marking them as deleted
    response = get_supabase_client().table('reminders').update({'is_deleted': True, 'deleted_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).eq('user_id', user_id).neq('is_deleted', True).execute()
    return len(response.data)

def soft_delete_reminder(reminder_id):
    response = get_supabase_client().table('reminders').update({'is_deleted': True, 'deleted_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).eq('id', reminder_id).execute()
    return len(response.data) > 0

def restore_reminder(reminder_id):
    response = get_supabase_client().table('reminders').update({'is_deleted': None, 'deleted_at': None}).eq('id', reminder_id).execute()
    return len(response.data) > 0

def get_deleted_reminders_by_user(user_id):
    response = get_supabase_client().table('reminders').select('*').eq('user_id', user_id).eq('is_deleted', True).execute()
    return response.data

def permanently_delete_reminder(reminder_id):
    response = get_supabase_client().table('reminders').delete().eq('id', reminder_id).execute()
    return len(response.data) > 0

def permanently_delete_all_deleted_reminders(user_id):
    response = get_supabase_client().table('reminders').delete().eq('user_id', user_id).eq('is_deleted', True).execute()
    return len(response.data)
