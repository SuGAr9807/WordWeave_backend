from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from datetime import timedelta


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp + timedelta(hours=24).total_seconds())
            + six.text_type(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()