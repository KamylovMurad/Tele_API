from django.db import models


class UserProfile(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    invite_code = models.CharField(max_length=6, null=True, blank=True)
    entered_invite = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invite_code_activated = models.BooleanField(default=False)
    authorized = models.BooleanField(default=False)

    def __str__(self):
        return self.phone_number
