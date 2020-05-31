# DinoMail - Hungry dino managing emails
# Copyright (C) 2020 Yoann Pietri

# DinoMail is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DinoMail is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with DinoMail. If not, see <https://www.gnu.org/licenses/>.
"""
Test for api app.

TODO : write missing test (need to write auth headers for ApiKey). 
"""
import base64

from django.contrib.auth.models import User
from django.test import Client, TestCase
from tastypie.models import ApiKey

from core.models import VirtualDomain


class ApiKeyTestCase(TestCase):
    """
    Test case for API urls related to API keys.
    """

    def setUp(self):
        """Set up the test.
        """
        self.user = User.objects.create(username="testuser")
        self.user.set_password("thisisatestpassword")
        self.user.save()
        self.client = Client()
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuser:thisisatestpassword").decode("ascii"),
        }

    def test_key_creation(self):
        """
        Test an API key is created after a user's creation.
        """
        self.assertTrue(ApiKey.objects.filter(user=self.user).exists())

    def test_api_key(self):
        """Tets the url to get an API key.
        """
        response = self.client.get("/api/apikey/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.json()["objects"][0]["key"], "")
