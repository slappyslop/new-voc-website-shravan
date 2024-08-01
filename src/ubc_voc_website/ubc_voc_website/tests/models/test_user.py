from django.test import TestCase

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

class UserTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )
        self.assertEqual(user.email, 'example@example.com')
        self.assertTrue(user.check_password('testpassword123'))

    def test_create_superuser(self):
        admin_user = self.User.objects.create_superuser(
            email='admin@example.com',
            password='testadminpassword123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('testadminpassword123'))

    def test_email_normalization(self):
        user = self.User.objects.create_user(
            email='example@EXAMPLE.com',
            password='testpassword123'
        )
        self.assertEqual(user.email, 'example@example.com')

    def test_null_email(self):
        with self.assertRaises(ValueError):
            self.User.objects.create_user(
                email='',
                password='testpassword123'
            )

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            self.User.objects.create_user(
                email='example',
                password='testpassword123'
            )

    def test_str_method(self):
        user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )
        self.assertEqual(str(user), 'example@example.com')

    def test_verbose_names(self):
        email_field_label = self.User._meta.get_field('email').verbose_name
        self.assertEqual(email_field_label, 'email')

    def test_no_duplicate_email(self):
        self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                email='example@example.com',
                password='testpassword456'
            )