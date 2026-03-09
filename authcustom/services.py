from django.db import connections
from django.db import connection,transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail  
from django.utils import timezone
from datetime import timedelta  
from django.contrib.auth.hashers import make_password




def makeDict(cursor, row):
    return dict((cursor.description[i][0], value) for i, value in enumerate(row))



class userService:
    
    def RegisterUser(self, username, email, password):
        with connections['default'].cursor() as cursor:
            cursor.execute("select * from register_user(%s, %s, %s);", [username, email, password])
             
            row= cursor.fetchone()
            if row:
                 return makeDict(cursor, row)
            return None


   
        return True
    
    
    def Get_user_by_username(self, username):
        with connections['default'].cursor() as cursor:
            cursor.execute("select * from get_user_for_login(%s);", [username])
            row= cursor.fetchone()
            if row:
                 return makeDict(cursor, row)
            return None
        
    def get_user_by_id(self, user_id):

        query = "SELECT id, username FROM users WHERE id = %s"

        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
        "id": row[0],
        "username": row[1],
        
            }
    def Get_user_by_email(self, email):
            query = "SELECT * FROM users WHERE email = %s"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, [email])
                    row = cursor.fetchone()

                if not row:
                    return None

                return {
                "id": row[0],
                "username": row[1],
            
                }
            except Exception as e:
                print(e)
                return None 
    def reset_password(self, email, password):
        hash_password = make_password(password)
        query = "UPDATE users SET password_hash = %s WHERE email = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [hash_password, email])
            return True
        except Exception as e:
            print(e)
            return False  
     # 🔎 RAW SQL LOGIN LOGGER
    def log_login_activity(self, user_id, email, ip, user_agent, status_value, reason, session_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO login_activity
            (user_id, email, ip_address, user_agent, status,
             failure_reason, session_id, login_time, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), TRUE)
        """, [user_id, email, ip, user_agent, status_value, reason, session_id])


def insert_role(user_id, role_id=3):
    """
    Assign role to user and return role_id
    Default role_id = 3 (employee)
    """

    query = """
        INSERT INTO user_roles (user_id, role_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """
    print(user_id)
    
    with transaction.atomic():
        with connection.cursor() as cursor:

            # Insert role
            cursor.execute(query, [user_id, role_id])

            # Fetch role
            cursor.execute(
                "SELECT get_user_role_id(%s)",
                [user_id]
            )

            role = cursor.fetchone()[0]

    return role
    

    



def assign_role(user_id: int, role_id: int) -> int:

    query = "SELECT assign_role(%s, %s);"
    
    
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id, role_id])
        assigned_role = cursor.fetchone()[0]

    return assigned_role    
    
        

import secrets  

def generate_reset_link(user):
    print(user['id'])
   
    try:
        uid = urlsafe_base64_encode(force_bytes(user['id']))
        token =secrets.token_urlsafe(32)
        create_reset_token(user['id'], token)   
    except Exception as e:
        print(e)
        return None 

    print(token)


    reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"
    return reset_url
    
    
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def Send_reset_link(email, reset_url):
    try:
        subject = "Password Reset"

        # Render HTML template
        html_content = render_to_string(
            "email/reset_password.html",
            {
                "reset_url": reset_url
            }
        )

        # Optional plain text fallback
        text_content = f"Click the link to reset your password: {reset_url}"

        email_message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )

        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return True

    except Exception as e:
        print(e)
        return False  
    
def create_reset_token(user_id, token):
    expires_at = timezone.now() + timedelta(minutes=15)

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO password_reset_token (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, [user_id, token, expires_at])

    return token



def verify_reset_token(token):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, expires_at, is_used
            FROM password_reset_token
            WHERE token = %s
        """, [token])

        row = cursor.fetchone()

    if not row:
        return None

    user_id, expires_at, is_used = row
    expires_at = timezone.make_aware(expires_at)
    print(expires_at)
    print(timezone.now()    )
    print(timezone.is_aware(expires_at))

    if is_used:
        return None
    print("here")
    if expires_at<timezone.now():
        return None

    return user_id





def mark_token_used(token):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE password_reset_token
            SET is_used = TRUE
            WHERE token = %s
        """, [token])




import hashlib

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()





import uuid
from datetime import timedelta
from django.db import connection, transaction
from django.utils import timezone


def insert_refresh_token(user_id, refresh_token):
    """
    Store refresh token in DB
    """

    token_hash = hash_token(refresh_token)
    print(token_hash)
    query = """
        INSERT INTO refresh_tokens
        (id, user_id, token_hash, expires_at)
        VALUES (%s, %s, %s, %s)
    """

    expires_at = timezone.now() + timedelta(days=7)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(query, [
                str(uuid.uuid4()),
                user_id,
                token_hash,
                expires_at
            ])


def validate_refresh_token(refresh_token):
    """
    Validate refresh token and return user_id
    """

    token_hash = hash_token(refresh_token)

    query = """
        SELECT user_id
        FROM refresh_tokens
        WHERE token_hash = %s
        AND revoked = FALSE
        AND expires_at > NOW()
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [token_hash])

        result = cursor.fetchone()

    if not result:
        return None

    return result[0]




def revoke_all_user_tokens(user_id):
    """
    Logout user from all devices
    """

    query = """
        UPDATE refresh_tokens
        SET revoked = TRUE,
            revoked_at = NOW()
        WHERE user_id = %s
    """

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])