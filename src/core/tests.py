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
Tests for core app.
"""
import crypt
from hmac import compare_digest as compare_hash

import bcrypt
from argon2 import PasswordHasher, Type
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import Client, TestCase, override_settings
from passlib.hash import lmhash
from tastypie.models import ApiKey

from .models import VirtualAlias, VirtualDomain, VirtualUser
from .utils import (
    make_password,
    make_password_clear,
    make_password_cleartext,
    make_password_crypt,
    make_password_des_crypt,
    make_password_ldap_md5,
    make_password_md5_crypt,
    make_password_plain,
    make_password_plain_md5,
    make_password_plain_trunc,
    make_password_sha,
    make_password_sha256,
    make_password_sha256_crypt,
    make_password_sha512,
    make_password_sha512_crypt,
    make_password_ssha,
    make_password_ssha256,
    make_password_ssha512,
    random_password,
)
from .utils_argon import make_password_argon2i, make_password_argon2id
from .utils_bcrypt import make_password_blf_crypt
from .utils_passlib import make_password_lanman


class VirtualDomainTestCase(TestCase):
    """Test case for virtual domains
    """

    def setUp(self):
        """Set up the tests.
        """
        self.examplecom = VirtualDomain.objects.create(name="example.com")
        self.examplefr = VirtualDomain.objects.create(name="example.fr", dkim_key="key")
        self.nanoyfr = VirtualDomain.objects.create(name="nanoy.fr")

    def test_uniqueness(self):
        """Test if we can create two virtual domains with same name (expecting no).
        """
        self.assertRaises(IntegrityError, VirtualDomain.objects.create, name="nanoy.fr")

    def test_str(self):
        """Test the __str__ method of a domain.
        """
        self.assertEqual(str(self.examplecom), "example.com")
        self.assertEqual(str(self.examplefr), "example.fr")

    def test_dkim(self):
        """Test the verify_dkim method

        All the possible cases are tested.
        For the ok case (all good), the dkim key of nanoy.fr (Yoann Pietri) is used.
        """
        self.assertEqual(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.NOTSET)
        self.nanoyfr.dkim_key_name = "false_key_name"
        self.nanoyfr.save()
        self.assertEqual(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.NOTSET)
        self.nanoyfr.dkim_key = "false_key"
        self.nanoyfr.save()
        self.assertEqual(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.NOTFOUND)
        self.nanoyfr.dkim_key_name = "falsekey"
        self.nanoyfr.save()
        self.assertEquals(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.NODNSKEY)
        self.nanoyfr.dkim_key_name = "2020050101"
        self.nanoyfr.save()
        self.assertEqual(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.NOMATCH)
        self.nanoyfr.dkim_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvpQbUZ8dCf3HDS/2QamqX670ip0Jbb/qxJCXwVzy7G+NyvkAtDjkKSwBpcoWZMX1LvZpY+q78Fxl1f6PjZpEDs16Yy8lI6P0a18eD5Sk5LAnnSoggIWfKwOhYhEXrwVIdqG0wm19QnvuiVkDkH3KEORmPRC74RYIz8NYb+A9wTwIDAQAB"
        self.assertEqual(self.nanoyfr.verify_dkim(), VirtualDomain.DkimStatus.OK)

        self.assertEqual(self.examplefr.verify_dkim(), VirtualDomain.DkimStatus.NOTSET)

    def test_update_dkim(self):
        """Test if the dkim_last_update field is well updated.
        """
        before = self.nanoyfr.dkim_last_update
        self.nanoyfr.update_dkim_status()
        self.assertGreater(self.nanoyfr.dkim_last_update, before)


class VirtualUserTestCase(TestCase):
    """Test case for virtual users.
    """

    def setUp(self):
        """Set up the test.
        """
        self.domain = VirtualDomain.objects.create(name="dino.mail")
        self.user = VirtualUser.objects.create(
            domain=self.domain, email="user@dino.mail", password="fake"
        )

    def test_uniqueness(self):
        """Test if we can create two virtual users with the same email (expecting no).
        """
        self.assertRaises(
            ValidationError,
            VirtualUser.objects.create,
            domain=self.domain,
            email="user@dino.mail",
            password="fake2",
        )

    def test_str(self):
        """Test the __str__ method for virtual users.
        """
        self.assertEqual(str(self.user), "user@dino.mail")

    def test_email_domain(self):
        """Test exectpions if we try to create an email with a wrong domain.
        """
        self.assertRaises(
            ValidationError,
            VirtualUser.objects.create,
            domain=self.domain,
            email="false@false.false",
            password="fake",
        )
        VirtualUser.objects.create(
            domain=self.domain, email="true@dino.mail", password="fake"
        )

    def test_quota(self):
        self.user.quota = 20
        self.user.save()
        self.assertEquals(self.user.readable_quota(), "20 B")
        self.user.quota = 35000
        self.user.save()
        self.assertEquals(self.user.readable_quota(), "35 kB")
        self.user.quota = 78000000
        self.user.save()
        self.assertEquals(self.user.readable_quota(), "78 MB")
        self.user.quota = 20000000000
        self.user.save()
        self.assertEquals(self.user.readable_quota(), "20 GB")

    def test_set_password(self):
        self.user.set_password("plopiplop")
        self.assertEquals(self.user.password[:9], "{SSHA512}")


class VirtualAliasTestCase(TestCase):
    """Test case for virtual aliases
    """

    def setUp(self):
        """Set up the test.
        """
        self.domain = VirtualDomain.objects.create(name="dino.mail")
        self.user = VirtualUser.objects.create(
            domain=self.domain, email="main@dino.mail", password="fake"
        )
        self.intern_alias = VirtualAlias.objects.create(
            domain=self.domain, source="abuse@dino.mail", destination="main@dino.mail"
        )
        self.broken_alias = VirtualAlias.objects.create(
            domain=self.domain,
            source="postmaster@dino.mail",
            destination="false@dino.mail",
        )
        self.extern_alias = VirtualAlias.objects.create(
            domain=self.domain, source="ext@dino.mail", destination="other@other.other"
        )

    def test_str(self):
        """Test __str__ method for virtual aliases.
        """
        self.assertEqual(str(self.intern_alias), "abuse@dino.mail -> main@dino.mail")

    def test_exterior(self):
        """Test the exterior method for virtual aliases.
        """
        self.assertTrue(self.extern_alias.exterior())
        self.assertFalse(self.intern_alias.exterior())

    def test_verify(self):
        """The the verify method for virtual aliases.
        """
        self.assertTrue(self.intern_alias.verify())
        self.assertTrue(self.extern_alias.verify())
        self.assertFalse(self.broken_alias.verify())

    def test_email_domain(self):
        """Test exceptions if we try to create an alias with the source domain different form the domain
        """
        self.assertRaises(
            ValidationError,
            VirtualAlias.objects.create,
            domain=self.domain,
            source="false@false.false",
            destination="main@dino.mail",
        )
        VirtualAlias.objects.create(
            domain=self.domain, source="true@dino.mail", destination="main@dino.mail"
        )


class PasswordTestCase(TestCase):
    """Test some password schemes.

    Expected values were generated using doveadm pw.
    """

    def setUp(self):
        """Define test password.
        """
        self.test_password = "plopiplop"

    def test_password_plain(self):
        """Test plain methods.
        """
        self.assertEquals(make_password_plain(self.test_password), "{PLAIN}plopiplop")
        self.assertEquals(
            make_password_plain_trunc(self.test_password), "{PLAIN-TRUNC}plopiplop"
        )
        self.assertEquals(make_password_clear(self.test_password), "{CLEAR}plopiplop")
        self.assertEquals(
            make_password_cleartext(self.test_password), "{CLEARTEXT}plopiplop"
        )

    def test_passsword_md5(self):
        """Test password methods for md5 related.
        """
        self.assertEquals(
            make_password_plain_md5(self.test_password),
            "{PLAIN-MD5}93bd5de10674d5619acb229111e38d0d",
        )
        self.assertEquals(
            make_password_ldap_md5(self.test_password),
            "{LDAP-MD5}k71d4QZ01WGayyKREeONDQ==",
        )
        self.assertEquals(
            make_password_md5_crypt(self.test_password)[:11], "{MD5-CRYPT}"
        )

    def test_password_sha(self):
        """Test password methods for SHA*.
        """
        self.assertEquals(
            make_password_sha(self.test_password), "{SHA}h6LOSkDf2MedKPoixyR/U1o7V2E="
        )
        self.assertEquals(make_password_ssha(self.test_password)[:6], "{SSHA}")
        self.assertEquals(
            make_password_sha256(self.test_password),
            "{SHA256}lxvwhomWBVVYwV0BAKTO3L75pfNtG9k9utfXa0G2NTU=",
        )
        self.assertEquals(make_password_ssha256(self.test_password)[:9], "{SSHA256}")
        self.assertEquals(
            make_password_sha512(self.test_password),
            "{SHA512}R0mrqf4kSN9gL90YdYZJHkHtL2qeEZN//m9PkkLjX9uZhfIOsDg43Xgnz5W9Pa7hLIdV2Vgn1uOlmoJlM6BngA==",
        )
        self.assertEquals(make_password_ssha512(self.test_password)[:9], "{SSHA512}")
        self.assertEquals(
            make_password_sha256_crypt(self.test_password)[:14], "{SHA256-CRYPT}"
        )
        self.assertEquals(
            make_password_sha512_crypt(self.test_password)[:14], "{SHA512-CRYPT}"
        )

    def test_password_argon(self):
        """Test password methods for utils_argon.
        """
        self.phi = PasswordHasher(type=Type.I)
        self.phid = PasswordHasher(type=Type.ID)
        self.assertEquals(make_password_argon2i(self.test_password)[:9], "{ARGON2I}")
        self.assertEquals(make_password_argon2id(self.test_password)[:10], "{ARGON2ID}")
        self.assertTrue(
            self.phi.verify(
                make_password_argon2i(self.test_password)[9:], self.test_password
            )
        )
        self.assertTrue(
            self.phid.verify(
                make_password_argon2id(self.test_password)[10:], self.test_password
            )
        )

    def test_password_bcrypt(self):
        """Test password for utils_bcrypt.
        """
        self.assertEquals(
            make_password_blf_crypt(self.test_password)[:11], "{BLF-CRYPT}"
        )
        self.assertTrue(
            bcrypt.checkpw(
                self.test_password.encode("utf-8"),
                make_password_blf_crypt(self.test_password)[11:].encode("utf-8"),
            )
        )

    def test_password_passlib(self):
        """Test password for utils_passlib
        """
        self.assertEquals(make_password_lanman(self.test_password)[:8], "{LANMAN}")
        self.assertTrue(
            lmhash.verify(
                self.test_password, make_password_lanman(self.test_password)[8:]
            )
        )

    def test_password(self):
        """Tets make password and random password.
        """
        self.assertEquals(
            make_password_des_crypt(self.test_password)[:11], "{DES-CRYPT}"
        )
        self.assertEquals(make_password_crypt(self.test_password)[:7], "{CRYPT}")
        self.assertEquals(make_password(self.test_password)[:9], "{SSHA512}")
        self.assertEquals(random_password()[:9], "{SSHA512}")


class ViewsTestCase(TestCase):
    """Test for views.
    """

    def setUp(self):
        """Set up the tests.
        """
        self.c = Client()
        self.login_required_urls = [
            "/",
            "/virtual-domains/",
            "/virtual-domains/new",
            "/virtual-domains/1/edit",
            "/virtual-domains/1/delete",
            "/virtual-domains/1/update-dkim-status",
            "/virtual-domains/1/dkim-scan",
            "/virtual-domains/1/autoconfig",
            "/virtual-users/",
            "/virtual-users/new",
            "/virtual-users/1/edit",
            "/virtual-users/1/edit-password",
            "/virtual-users/1/delete",
            "/virtual-aliases/",
            "/virtual-aliases/new",
            "/virtual-aliases/1/edit",
            "/virtual-aliases/1/delete",
            "/search",
            "/regen-api-key",
        ]
        self.no_login_required_urls = ["/login", "/legals"]
        self.password = "password"
        self.superuser = User.objects.create_superuser(
            "superuser", "test@example.com", self.password
        )

    def test_unauthorized(self):
        """Test views witout login required.
        """
        for url in self.login_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url, "/login?next={}".format(url),
            )

    def test_authorized(self):
        """Test views with login required.
        """
        for url in self.no_login_required_urls:
            response = self.c.get(url)
            self.assertEquals(response.status_code, 200)

    def test_login(self):
        """Test login view.
        """
        response = self.c.post(
            "/login", {"username": self.superuser.username, "password": self.password}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_home(self):
        """Test home view.
        """
        self.c.login(username=self.superuser.username, password=self.password)
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_regen_api_key(self):
        """Test regen api key view.
        """
        self.c.login(username=self.superuser.username, password=self.password)
        apikey = ApiKey.objects.get(user=self.superuser).key
        response = self.c.get("/regen-api-key")
        self.assertEquals(response.status_code, 302)
        apikey2 = ApiKey.objects.get(user=self.superuser).key
        self.assertNotEquals(apikey, apikey2)

        ApiKey.objects.get(user=self.superuser).delete()
        response = self.c.get("/regen-api-key")
        self.assertEquals(response.status_code, 302)
        self.assertTrue(ApiKey.objects.filter(user=self.superuser).exists())

    def test_virtual_domains(self):
        """Test virtual domains views.
        """
        self.c.login(username=self.superuser.username, password=self.password)

        response = self.c.get("/virtual-domains/")
        self.assertEquals(response.status_code, 200)
        response = self.c.get("/virtual-domains/1/edit")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("/virtual-domains/1/delete")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("virtual-domains/1/update-dkim-status")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("/virtual-domains/1/dkim-scan")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("/virtual-domains/1/autoconfig")
        self.assertEquals(response.status_code, 404)

        response = self.c.get("/virtual-domains/new")
        self.assertEquals(response.status_code, 200)
        response = self.c.post("/virtual-domains/new", {"name": "example.com"})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-domains/")
        self.assertTrue(VirtualDomain.objects.filter(name="example.com").exists())

        response = self.c.get("/virtual-domains/1/edit")
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-domains/1/edit",
            {
                "name": "nanoy.fr",
                "dkim_key_name": "2020050101",
                "dkim_key": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvpQbUZ8dCf3HDS/2QamqX670ip0Jbb/qxJCXwVzy7G+NyvkAtDjkKSwBpcoWZMX1LvZpY+q78Fxl1f6PjZpEDs16Yy8lI6P0a18eD5Sk5LAnnSoggIWfKwOhYhEXrwVIdqG0wm19QnvuiVkDkH3KEORmPRC74RYIz8NYb+A9wTwIDAQAB",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-domains/")
        self.assertTrue(VirtualDomain.objects.filter(name="nanoy.fr").exists())

        vd = VirtualDomain.objects.get(name="nanoy.fr")
        last_update = vd.dkim_last_update

        response = self.c.get("/virtual-domains/1/update-dkim-status")
        vd = VirtualDomain.objects.get(name="nanoy.fr")
        self.assertGreater(vd.dkim_last_update, last_update)
        self.assertEquals(vd.dkim_status, VirtualDomain.DkimStatus.OK)

        response = self.c.get("/virtual-domains/1/dkim-scan")
        self.assertEquals(response.status_code, 200)

        response = self.c.get("/virtual-domains/1/autoconfig")
        self.assertEquals(response.status_code, 200)

        response = self.c.get("/virtual-domains/1/delete")
        self.assertEquals(response.status_code, 200)

        response = self.c.post("/virtual-domains/1/delete", {"verifier": "false"})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-domains/")
        self.assertTrue(VirtualDomain.objects.filter(name="nanoy.fr").exists())

        response = self.c.post("/virtual-domains/1/delete", {"verifier": "nanoy.fr"})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-domains/")
        self.assertFalse(VirtualDomain.objects.filter(name="nanoy.fr").exists())

    def test_virtual_users(self):
        """Test virtual users views.
        """
        self.c.login(username=self.superuser.username, password=self.password)

        response = self.c.get("/virtual-users/")
        self.assertEquals(response.status_code, 200)
        response = self.c.get("/virtual-users/1/edit")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("/virtual-users/1/delete")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("virtual-users/1/edit-password")

        self.domain = VirtualDomain.objects.create(name="nanoy.fr")
        response = self.c.get("/virtual-users/new")
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-users/new",
            {"domain": self.domain.pk, "email": "falseemail@email.email", "quota": 0},
        )
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-users/new",
            {"domain": self.domain.pk, "email": "me@nanoy.fr", "quota": 0},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-users/")
        self.assertTrue(VirtualUser.objects.filter(email="me@nanoy.fr").exists())

        response = self.c.post("/virtual-users/1/edit",)
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-users/1/edit",
            {"domain": self.domain.pk, "email": "me@nanoy.fr", "quota": 20},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-users/")
        self.assertTrue(
            VirtualUser.objects.filter(email="me@nanoy.fr", quota=20).exists()
        )

        self.user = VirtualUser.objects.get(email="me@nanoy.fr")
        password = self.user.password
        response = self.c.get("/virtual-users/1/edit-password")
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-users/1/edit-password", {"password": "plopiplop"}
        )
        self.user = VirtualUser.objects.get(email="me@nanoy.fr")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-users/")
        self.assertNotEquals(password, self.user.password)

        response = self.c.get("/virtual-users/1/delete")
        self.assertEquals(response.status_code, 200)

        response = self.c.post("/virtual-users/1/delete", {"verifier": "false"})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-users/")
        self.assertTrue(VirtualUser.objects.filter(email="me@nanoy.fr").exists())

        response = self.c.post("/virtual-users/1/delete", {"verifier": "me@nanoy.fr"})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-users/")
        self.assertFalse(VirtualUser.objects.filter(email="me@nanoy.fr").exists())

    def test_virtual_aliases(self):
        """Test virtual alias views.
        """
        self.c.login(username=self.superuser.username, password=self.password)

        response = self.c.get("/virtual-aliases/")
        self.assertEquals(response.status_code, 200)
        response = self.c.get("/virtual-aliases/1/edit")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("/virtual-aliases/1/delete")
        self.assertEquals(response.status_code, 404)
        response = self.c.get("virtual-aliases/1/edit-password")

        self.domain = VirtualDomain.objects.create(name="nanoy.fr")
        response = self.c.get("/virtual-aliases/new")
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-aliases/new",
            {
                "domain": self.domain.pk,
                "source": "test@plop.fr",
                "destination": "me@nanoy.fr",
            },
        )
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-aliases/new",
            {
                "domain": self.domain.pk,
                "source": "test@nanoy.fr",
                "destination": "me@nanoy.fr",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-aliases/")
        self.assertTrue(VirtualAlias.objects.filter(destination="me@nanoy.fr").exists())

        response = self.c.post("/virtual-aliases/1/edit",)
        self.assertEquals(response.status_code, 200)
        response = self.c.post(
            "/virtual-aliases/1/edit",
            {
                "domain": self.domain.pk,
                "source": "test@nanoy.fr",
                "destination": "me@plop.fr",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-aliases/")
        self.assertTrue(VirtualAlias.objects.filter(destination="me@plop.fr").exists())

        response = self.c.get("/virtual-aliases/1/delete")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/virtual-aliases/")
        self.assertFalse(VirtualAlias.objects.filter(destination="me@plop.fr").exists())

    def test_search(self):
        """Test the search view.
        """
        self.c.login(username=self.superuser.username, password=self.password)

        response = self.c.get("/search")
        self.assertEquals(response.status_code, 200)

        response = self.c.get("/search", {"q": "plop"})
        self.assertEquals(response.status_code, 200)
