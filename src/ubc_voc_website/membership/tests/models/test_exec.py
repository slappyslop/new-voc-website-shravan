from django.test import TestCase
from django.contrib.auth import get_user_model
from membership.models import Exec

from django.db.utils import IntegrityError

class ExecTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )

        self.exec = Exec.objects.create(
            user=self.user,
            exec_role='test exec role'
        )

    def test_creation(self):
        self.assertEqual(self.exec.user.email, 'example@example.com')
        self.assertTrue(self.exec.user.check_password('testpassword123'))
        self.assertEqual(self.exec.exec_role, 'test exec role')

    def test_str_method(self):
        self.assertEqual(str(self.exec), 'example@example.com - test exec role')

    def test_null_user(self):
        with self.assertRaises(IntegrityError):
            Exec.objects.create(
                user=None,
                exec_role='test exec role'
            )

    def test_verbose_names(self):
        exec_role_field_label = Exec._meta.get_field('exec_role').verbose_name

        self.assertEqual(exec_role_field_label, 'exec role')