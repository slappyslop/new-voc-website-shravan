from django.test import TestCase
from django.contrib.auth import get_user_model
from membership.models import Profile

import datetime
from django.db.utils import IntegrityError

class ProfileTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='example@example.com',
            password='testpassword123'
        )

        self.user2 = self.User.objects.create_user(
            email='example2@example.com',
            password='testpassword456'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            pronouns='Test/Case',
            phone='(111)-111-1111',
            student_number='12345678',
            birthdate=datetime.date(2000, 1, 1),
            blurb='This is a test blurb',
            acc=True,
            vocene=True,
            trip_org_email=True
        )

    def test_creation(self):
        self.assertEqual(self.profile.user.email, 'example@example.com')
        self.assertTrue(self.profile.user.check_password('testpassword123'))
        self.assertEqual(self.profile.first_name, 'Test')
        self.assertEqual(self.profile.last_name, 'User')
        self.assertEqual(self.profile.pronouns, 'Test/Case')
        self.assertEqual(self.profile.phone, '(111)-111-1111')
        self.assertEqual(self.profile.student_number, '12345678')
        self.assertEqual(self.profile.birthdate, datetime.date(2000, 1, 1))
        self.assertEqual(self.profile.blurb, 'This is a test blurb')
        self.assertTrue(self.profile.acc)
        self.assertTrue(self.profile.vocene)
        self.assertTrue(self.profile.trip_org_email)

    def test_str_method(self):
        self.assertEqual(str(self.profile), 'Test User')

    def test_default_values(self):
        user = self.User.objects.create_user(
            email='example3@example.com',
            password='testpassword789'
        )
        profile = Profile.objects.create(
            user=user,
            first_name='Test',
            last_name='User',
            phone='(111)-111-1111'
        )
        self.assertTrue(profile.acc)
        self.assertTrue(profile.vocene)
        self.assertTrue(profile.trip_org_email)

    def test_null_user(self):
        with self.assertRaises(IntegrityError):
            Profile.objects.create(
                user=None,
                first_name='Test',
                last_name='User',
                phone='(111)-111-1111'
            )

    def test_verbose_names(self):
        first_name_field_label = Profile._meta.get_field('first_name').verbose_name
        last_name_field_label = Profile._meta.get_field('last_name').verbose_name
        pronouns_field_label = Profile._meta.get_field('pronouns').verbose_name
        phone_field_label = Profile._meta.get_field('phone').verbose_name
        student_number_field_label = Profile._meta.get_field('student_number').verbose_name
        birthdate_field_label = Profile._meta.get_field('birthdate').verbose_name
        blurb_field_label = Profile._meta.get_field('blurb').verbose_name
        acc_field_label = Profile._meta.get_field('acc').verbose_name
        vocene_field_label = Profile._meta.get_field('vocene').verbose_name
        trip_org_email_field_label = Profile._meta.get_field('trip_org_email').verbose_name

        self.assertEqual(first_name_field_label, 'first name')
        self.assertEqual(last_name_field_label, 'last name')
        self.assertEqual(pronouns_field_label, 'pronouns')
        self.assertEqual(phone_field_label, 'phone')
        self.assertEqual(student_number_field_label, 'student number')
        self.assertEqual(birthdate_field_label, 'birthdate')
        self.assertEqual(blurb_field_label, 'blurb')
        self.assertEqual(acc_field_label, 'acc')
        self.assertEqual(vocene_field_label, 'vocene')
        self.assertEqual(trip_org_email_field_label, 'trip org email')
