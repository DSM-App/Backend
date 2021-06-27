from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EmailVerificationTokens(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    tries = models.IntegerField(default=0)
    expires_at = models.DateTimeField()


# The expires_at line is buggy it only sets the time once and uses same time for all next objects
# So instead of passing default time we pass it from the object getting created
