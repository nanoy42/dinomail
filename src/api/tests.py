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
"""
import base64

from django.contrib.auth.models import User
from django.test import Client, TestCase
from tastypie.models import ApiKey

from core.models import VirtualAlias, VirtualDomain, VirtualUser


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


class ApiTestCase(TestCase):
    """Test other views.
    """

    def setUp(self):
        """Set up the test.
        """
        self.user = User.objects.create_superuser(
            "testuser", "test@example.com", "thisisatestpassword"
        )
        self.client = Client()
        apikey = ApiKey.objects.get(user=self.user).key
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "ApiKey " + "testuser" + ":" + apikey
        }

    def test_virtualdomains(self):
        """Test virtual domains urls.
        """
        VirtualDomain.objects.create(name="nanoy.fr")
        response = self.client.get("/api/virtualdomain/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        expected = {
            "display_name": "",
            "dkim_key": "",
            "dkim_key_name": "",
            "dkim_status": 0,
            "id": 1,
            "imap_address": "",
            "name": "nanoy.fr",
            "pop_address": "",
            "resource_uri": "/api/virtualdomain/1/",
            "short_display_name": "",
            "smtp_address": "",
        }
        self.assertTrue(expected.items() <= response.json()["objects"][0].items())

        response = self.client.post(
            "/api/virtualdomain/",
            {"name": "example.com"},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(VirtualDomain.objects.filter(name="example.com").exists())

        response = self.client.get("/api/virtualdomain/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        response = self.client.patch(
            "/api/virtualdomain/2/",
            {"display_name": "display name"},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEquals(response.status_code, 202)
        self.assertTrue(
            VirtualDomain.objects.filter(
                name="example.com", display_name="display name"
            ).exists()
        )

        response = self.client.patch(
            "/api/virtualdomain/2/",
            {"name": "example.fr"},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEquals(response.status_code, 202)
        self.assertTrue(VirtualDomain.objects.filter(name="example.fr").exists())

        response = self.client.delete("/api/virtualdomain/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 204)
        self.assertFalse(VirtualDomain.objects.filter(name="example.fr").exists())

    def test_virtualusers(self):
        """Test virtual users urls.
        """
        domain = VirtualDomain.objects.create(name="nanoy.fr")
        VirtualUser.objects.create(domain=domain, email="me@nanoy.fr")
        response = self.client.get("/api/virtualuser/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        expected = {
            "domain": "/api/virtualdomain/1/",
            "email": "me@nanoy.fr",
            "id": 1,
            "quota": 0,
            "resource_uri": "/api/virtualuser/1/",
        }
        self.assertTrue(expected.items() <= response.json()["objects"][0].items())

        response = self.client.post(
            "/api/virtualuser/",
            {"domain": "/api/virtualdomain/1/", "email": "test@plop.fr", "quota": 0},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEquals(
            response.json()["error"],
            "['The domain of test@plop.fr (plop.fr) is not the same as the domain nanoy.fr']",
        )
        self.assertFalse(VirtualUser.objects.filter(email="test@plop.fr").exists())

        response = self.client.post(
            "/api/virtualuser/",
            {"domain": "/api/virtualdomain/1/", "email": "test@nanoy.fr", "quota": 0},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(VirtualUser.objects.filter(email="test@nanoy.fr").exists())

        response = self.client.get("/api/virtualuser/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        response = self.client.patch(
            "/api/virtualuser/2/",
            {"quota": 20},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEquals(response.status_code, 202)
        self.assertTrue(
            VirtualUser.objects.filter(email="test@nanoy.fr", quota=20).exists()
        )

        password = VirtualUser.objects.get(email="test@nanoy.fr").password
        response = self.client.patch(
            "/api/changeuserpassword/2/",
            {"paswword": "plopiplop"},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEquals(response.status_code, 202)
        password2 = VirtualUser.objects.get(email="test@nanoy.fr").password
        self.assertNotEquals(password, password2)

        response = self.client.delete("/api/virtualuser/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 204)
        self.assertFalse(VirtualUser.objects.filter(email="test@nanoy.fr").exists())

    def test_virtualaliases(self):
        """Test virtual aliases urls.
        """
        domain = VirtualDomain.objects.create(name="nanoy.fr")
        VirtualAlias.objects.create(
            domain=domain, source="test@nanoy.fr", destination="me@nanoy.fr"
        )
        response = self.client.get("/api/virtualalias/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        expected = {
            "destination": "me@nanoy.fr",
            "domain": "/api/virtualdomain/1/",
            "id": 1,
            "resource_uri": "/api/virtualalias/1/",
            "source": "test@nanoy.fr",
        }
        self.assertTrue(expected.items() <= response.json()["objects"][0].items())

        response = self.client.post(
            "/api/virtualalias/",
            {
                "domain": "/api/virtualdomain/1/",
                "source": "test@plop.fr",
                "destination": "test@plop.fr",
            },
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEquals(
            response.json()["error"],
            "['The domain of test@plop.fr (plop.fr) is not the same as the domain nanoy.fr']",
        )
        self.assertFalse(
            VirtualAlias.objects.filter(
                source="test@plop.fr", destination="test@plop.fr"
            ).exists()
        )

        response = self.client.post(
            "/api/virtualalias/",
            {
                "domain": "/api/virtualdomain/1/",
                "source": "test@nanoy.fr",
                "destination": "test@plop.fr",
            },
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            VirtualAlias.objects.filter(
                source="test@nanoy.fr", destination="test@plop.fr"
            ).exists()
        )

        response = self.client.get("/api/virtualalias/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 200)
        response = self.client.patch(
            "/api/virtualalias/2/",
            {"destination": "me@plop.fr"},
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEquals(response.status_code, 202)
        self.assertTrue(
            VirtualAlias.objects.filter(
                source="test@nanoy.fr", destination="me@plop.fr"
            ).exists()
        )

        response = self.client.delete("/api/virtualalias/2/", **self.auth_headers)
        self.assertEquals(response.status_code, 204)
        self.assertFalse(
            VirtualAlias.objects.filter(
                source="test@plop.fr", destination="me@plop.fr"
            ).exists()
        )
