from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from authcustom.user import CustomUser
from .services import userService
from .utils import get_user_role


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        print("COOKIES:", request.COOKIES)

        raw_token = request.COOKIES.get("access_token")

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError):
            return None


        # ✅ Get user_id from JWT
        user_id = validated_token.get("user_id")
        session_id = validated_token.get("session_id")
        

        if not user_id:
            return None


        # ✅ Load user from DB
        service = userService()
        user = service.get_user_by_id(user_id)
        
        if not user:
            return None


        # ✅ Get role from DB function
        role = get_user_role(user_id)


        # ✅ Build custom user object
        custom_user = CustomUser(
            user_id=user_id,
            username=user["username"],
            role=role,
            session_id=session_id
        )

        return (custom_user, validated_token)
