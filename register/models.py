from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .notifications import validate_phone_number, get_expiration_time, generate_client_id, generate_client_secret, \
    generate_token, ACCESS_TOKEN_EXPIRATION


class User(AbstractUser):
    email = models.EmailField(_('email address'), blank=False, unique=True)
    city = models.CharField(max_length=50, blank=True)
    friends = models.ManyToManyField('User')
    phone_number = models.CharField(
        max_length=20,
        blank=False,
        validators=[validate_phone_number],
        unique=True,
        help_text='Input full number with country code'
    )
    photo = models.ImageField(upload_to='avatars', blank=True, null=True)

    def __str__(self):
        return self.username


class FriendshipStatus(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    status = models.BooleanField()


class MyApplication(models.Model):
    GRANT_CLIENT_CREDENTIALS = "client-credentials"
    client_id = models.CharField(max_length=150, default=generate_client_id, unique=True, db_index=True)
    client_secret = models.CharField(max_length=255, default=generate_client_secret, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def create_token(self):
        token = AccessToken.objects.create(
            application=self,
            scope='read write',
        )
        return token


class AccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True, default=generate_token)
    application = models.ForeignKey(MyApplication, on_delete=models.CASCADE, blank=True, null=True,)
    expires = models.DateTimeField(default=get_expiration_time)
    scope = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.
        :param scopes: An iterable containing the scopes to check or None
        """
        return not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes
        :param scopes: An iterable containing the scopes to check
        """
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)

    def revoke(self):
        """
        Convenience method to uniform tokens' interface, for now
        simply remove this token from the database in order to revoke it.
        """
        self.delete()

    @property
    def scopes(self):
        """
        Returns a dictionary of allowed scope names (as keys) with their descriptions (as values)
        """
        all_scopes = {"read": "Reading scope", "write": "Writing scope"}
        token_scopes = self.scope.split()
        return {name: desc for name, desc in all_scopes.items() if name in token_scopes}

    def make_response_body(self):
        token = {
            'access_token': self.token,
            'expires_in': ACCESS_TOKEN_EXPIRATION,
            'token_type': 'Bearer',
            'scope': self.scope,
        }
        return token

    def __str__(self):
        return self.token
