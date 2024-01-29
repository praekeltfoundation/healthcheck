import logging

from django.test import Client, TestCase
from django.urls import reverse  # noqa: F401, E261

from .models import User

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class AdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.all().delete()
        User.objects.create_superuser(
            username="testadmin",
            password="testadminpassword",
        )

        logger.info("Created superuser")

        self.client.login(
            username="testadmin",
            password="testadminpassword",
        )

        logger.info("Logged in with superuser")

    def test_user_creation(self):
        url = "/admin/users/user/add/"

        data = {
            "username": "testuser",
            "password": "testuserpassword",
        }

        r = self.client.post(url, data=data)

        # admin user creation request returns 302
        self.assertEquals(r.status_code, 302)

        logger.info("Created test user")

        test_user = User.objects.get(username=data.get("username"))

        self.assertIsNotNone(test_user)

        self.assertEquals(test_user.username, data.get("username"))
        self.assertEquals(test_user.check_password(data.get("password")), True)
        self.assertIsNotNone(test_user.auth_token)

    def test_user_creation_no_password(self):
        url = "/admin/users/user/add/"

        data = {
            "username": "testuser",
        }

        r = self.client.post(url, data=data)

        # admin user creation request returns 302
        self.assertEquals(r.status_code, 302)

        logger.info("Created test user without password")

        test_user = User.objects.get(username=data.get("username"))

        self.assertIsNotNone(test_user)

        self.assertEquals(test_user.username, data.get("username"))
        self.assertEquals(test_user.check_password(data.get("password")), False)
        self.assertEquals(test_user.password, "")
        self.assertIsNotNone(test_user.auth_token)
