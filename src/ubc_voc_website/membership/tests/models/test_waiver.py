from django.test import TestCase
from django.contrib.auth import get_user_model
from membership.models import Membership, Waiver

from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.files import File
from pathlib import Path

class WaiverTests(TestCase):
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

        path = Path("media/test_files/signature.png")
        with path.open(mode="rb") as f:
            self.signature = File(f, name=path.name)

            self.waiver = Waiver.objects.create(
                membership=self.membership,
                full_name='Test User',
                student_number='12345678',
                signature=self.signature
            )

    def test_creation(self):
        self.assertEqual(self.waiver.membership, self.membership)
        self.assertEqual(self.waiver.full_name, 'Test User')
        self.assertEqual(self.waiver.student_number, '12345678')
        self.assertFalse(self.waiver.paper_waiver)

    def test_str_method(self):
        self.assertEqual(str(self.waiver), f'Waiver for Test User (Membership {str(self.membership)})')