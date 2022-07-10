from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from model_history.models import History


class ModelLogTestCase(TestCase):
    def setUp(self):
        History.register(User, exclude=["password"])

    def tearDown(self):
        History.unregister(User)

    def test_1(self):
        count = History.objects.count()
        self.assertEqual(count, 0)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(History.objects.count(), 0)
        user = User.objects.create_user(username="test")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(History.objects.count(), 1)
        history = History.objects.fetch(user)
        self.assertEqual(history.logs.count(), 1)
        user.username = "test2"
        user.save(update_fields=["username"])
        self.assertEqual(history.logs.count(), 2)

    def test_already(self):
        with self.assertRaises(History.AlreadyRegistered):
            History.register(User)
