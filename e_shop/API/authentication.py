from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


# Exercise #4
class TokenWithTimeToLiveAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key=key)
        if (timezone.now() - token.created).seconds > (60 * 10):
            raise exceptions.AuthenticationFailed("Token is dead :(")
        return user, token
