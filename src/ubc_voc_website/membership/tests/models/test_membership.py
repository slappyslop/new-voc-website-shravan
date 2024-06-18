from django.test import TestCase
from django.contrib.auth import get_user_model
from membership.models import Membership

from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.utils import IntegrityError

class MembershipTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )

        self.membership = Membership.objects.create(
            user=self.user,
            start_date=date.today(),
            end_date=date.today() + relativedelta(years=1),
            type=Membership.MembershipType.REGULAR,
            active=True
        )

    def test_creation(self):
        self.assertEqual(self.membership.user.email, 'example@example.com')
        self.assertTrue(self.membership.user.check_password('testpassword123'))
        self.assertEqual(self.membership.start_date, date.today())
        self.assertEqual(self.membership.end_date, date.today() + relativedelta(years=1))
        self.assertEqual(self.membership.type, Membership.MembershipType.REGULAR)
        self.assertTrue(self.membership.active)

    def test_str_method(self):
        self.assertEqual(str(self.membership), 'example@example.com - R')

    def test_default_values(self):
        user = self.User.objects.create_user(
            email='example2@example.com',
            password='testpassword456'
        )

        membership = Membership.objects.create(
            user=user,
            start_date=date.today(),
            end_date=date.today() + relativedelta(years=1)
        )

        self.assertEqual(membership.type, Membership.MembershipType.REGULAR)
        self.assertEqual(membership.active, False)

    def test_null_user(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                user=None,
                start_date=date.today(),
                end_date=date.today() + relativedelta(years=1)
            )

    def test_verbose_names(self):
        start_date_field_label = Membership._meta.get_field('start_date').verbose_name
        end_date_field_label = Membership._meta.get_field('end_date').verbose_name
        type_field_label = Membership._meta.get_field('type').verbose_name
        active_field_label = Membership._meta.get_field('active').verbose_name

        self.assertEqual(start_date_field_label, 'start date')
        self.assertEqual(end_date_field_label, 'end date')
        self.assertEqual(type_field_label, 'type')
        self.assertEqual(active_field_label, 'active')