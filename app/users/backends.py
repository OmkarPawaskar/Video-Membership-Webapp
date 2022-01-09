"""
This module contains Authentication Middleware to identify authenticated and guest users
"""

from starlette.authentication import(
    AuthenticationBackend,
    AuthCredentials,
    SimpleUser,
    UnauthenticatedUser
)
from . import auth

class JWTCookieBackend(AuthenticationBackend):
    async def authenticate(self, request):
        session_token = request.cookies.get('session_id')
        user_data = auth.verify_user_id(session_token)
        if user_data is None:
            #guest user 
            roles = ['anonymous']
            return AuthCredentials(roles), UnauthenticatedUser()
        user_id = user_data.get('user_id')
        roles = ['authenticated']
        return AuthCredentials(roles), SimpleUser(user_id)