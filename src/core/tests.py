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
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from passlib.hash import lmhash

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
