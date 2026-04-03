from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailChangeTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # We exclude the email from the hash, as it should be able to change.
        # We use the PK and the password hash.
        # If the password is changed, this token will become invalid.
        return (
            str(user.pk) + str(timestamp) + str(user.password)
        )

email_change_token_generator = EmailChangeTokenGenerator()