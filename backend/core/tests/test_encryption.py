from django.test import TestCase, override_settings
from cryptography.fernet import Fernet
from core.models import Credential
from core.crypto import encrypt, decrypt


TEST_KEY = Fernet.generate_key().decode()

@override_settings(CREDENTIALS_ENCRYPTION_KEY=TEST_KEY)
class CredentialEncryptionTest(TestCase):
    def test_plaintext_is_unreadable_in_db(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user("alice@test.com", "pw12345678")

        plaintext = "sk-live-very-secret-api-key-AAAABBBBCCCC1234"
        cred = Credential(user=user, name="Stripe", provider="http")
        cred.set_value(plaintext)
        cred.save()

        # Read the raw row, bypassing the ORM layer entirely.
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute(
                "SELECT encrypted_value FROM core_credential WHERE id = %s",
                [cred.pk],
            )
            (raw,) = cur.fetchone()

        # 1. The plaintext must not appear anywhere in the stored value.
        self.assertNotIn(plaintext, raw)
        # 2. Even a recognizable fragment of it must not appear.
        self.assertNotIn(plaintext[:16], raw)
        # 3. The stored value should look like a Fernet token (starts with gAAAAA).
        self.assertTrue(raw.startswith("gAAAAA"), f"Token header did not match Fernet parameters: {raw[:20]}")

        # Sanity: the helper decrypts back to the original.
        self.assertEqual(decrypt(raw), plaintext)