from django.test import TestCase
from django.contrib.auth import get_user_model
from membership.models import PSG

from django.db.utils import IntegrityError

class PSGTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )

        self.psg = PSG.objects.create(
            user=self.user,
        )

    def test_creation(self):
        self.assertEqual(self.psg.user.email, 'example@example.com')

    def test_str_method(self):
        self.assertEqual(str(self.psg), 'example@example.com (PSG)')

    def test_null_user(self):
        with self.assertRaises(IntegrityError):
            PSG.objects.create(
                user=None
            )
            