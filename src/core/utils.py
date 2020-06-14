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
Password utils functions for DinoMail.
"""
import base64
import crypt
import hashlib
import importlib
import os
import random
import string

from django.conf import settings


def make_password(password):
    """Hash a password using SHA512. Compatible with dovecot.

    The password is hashsed ans stored as a dovecot-complient way, i.e.
    {algorithm}passwordsalt

    Args:
        password (string): the non-hashed password

    Returns:
        string: the hashed password
    """
    function_string = getattr(
        settings, "DINOMAIL_PASSWORD_SCHEME", "core.utils.make_password_ssha512"
    )
    mod_name, func_name = function_string.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return func(password)


def make_password_plain(password):
    """Password implementation for PLAIN.

    PLAIN is just the plain password.

    Args:
        password (string): the plain password

    Returns:
        string: the plain password with prefix
    """
    return "{{PLAIN}}{}".format(password)


def make_password_plain_trunc(password):
    """Password implementation for PLAIN-TRUNC.

    PLAIN-TRUNC is also the plain password.

    Args:
        password (string): the plain password

    Returns:
        string: the plain password with prefix
    """
    return "{{PLAIN-TRUNC}}{}".format(password)


def make_password_cleartext(password):
    """Password implementation for CLEARTEXT

    CLEARTEXT is juste the plain password.

    Args:
        password (string): the plain password

    Returns:
        string: the plain password with prefix
    """
    return "{{CLEARTEXT}}{}".format(password)


def make_password_clear(password):
    """Password implementation for CLEAR.

    CLEAR is juste the plain password.

    Args:
        password (string): the plain password

    Returns:
        string: the plain password with prefix
    """
    return "{{CLEAR}}{}".format(password)


def make_password_ssha512(password):
    """Password implementation for SSHA512.

    SSHA512 is salted SHA512.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt.
    """
    salt = os.urandom(16)
    sha = hashlib.sha512()
    password = password.encode("utf-8")
    sha.update(password)
    sha.update(salt)
    ssha512 = base64.b64encode(sha.digest() + salt)
    return "{{SSHA512}}{}".format(ssha512.decode("utf-8"))


def make_password_sha512(password):
    """Password implementation for SHA512.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix
    """
    sha = hashlib.sha512()
    password = password.encode("utf-8")
    sha.update(password)
    sha512 = base64.b64encode(sha.digest())
    return "{{SHA512}}{}".format(sha512.decode("utf-8"))


def make_password_ssha256(password):
    """Password implementation for SSHA256.

    SSHA256 is salted SHA256.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    salt = os.urandom(16)
    sha = hashlib.sha256()
    password = password.encode("utf-8")
    sha.update(password)
    sha.update(salt)
    ssha256 = base64.b64encode(sha.digest() + salt)
    return "{{SSHA256}}{}".format(ssha256.decode("utf-8"))


def make_password_sha256(password):
    """Password implementation for SHA256.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix
    """
    sha = hashlib.sha256()
    password = password.encode("utf-8")
    sha.update(password)
    sha256 = base64.b64encode(sha.digest())
    return "{{SHA256}}{}".format(sha256.decode("utf-8"))


def make_password_sha(password):
    """Password implementation for SHA.

    SHA is SHA1.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix
    """
    sha = hashlib.sha1()
    password = password.encode("utf-8")
    sha.update(password)
    sha1 = base64.b64encode(sha.digest())
    return "{{SHA}}{}".format(sha1.decode("utf-8"))


def make_password_ssha(password):
    """Password implementation for SSHA.

    SSHA is salted SHA1.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    salt = os.urandom(16)
    sha = hashlib.sha1()
    password = password.encode("utf-8")
    sha.update(password)
    sha.update(salt)
    sha1 = base64.b64encode(sha.digest())
    return "{{SSHA}}{}".format(sha1.decode("utf-8"))


def make_password_plain_md5(password):
    """Password implementation for PLAIN-MD5.

    PLAIN-MD5 is the MD5 sum stored in HEX.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password and prefix
    """
    md = hashlib.md5()
    password = password.encode("utf-8")
    md.update(password)
    return "{{PLAIN-MD5}}{}".format(md.hexdigest())


def make_password_ldap_md5(password):
    """Password implementation for LDAP-MD5.

    LDAP-MD5 is the MD5 sum stored in Base64.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password and prefix
    """
    md = hashlib.md5()
    password = password.encode("utf-8")
    md.update(password)
    md5 = base64.b64encode(md.digest())
    return "{{LDAP-MD5}}{}".format(md5.decode("utf-8"))


def make_password_crypt(password):
    """Password implementation for CRYPT.

    CRYPT is usual DES-CRYPT.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    return "{{CRYPT}}{}".format(
        crypt(password, crypt.mksalt(method=crypt.METHOD_CRYPT))
    )


def make_password_des_crypt(password):
    """Password implementation for DES-CRYPT.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    return "{{DES-CRYPT}}{}".format(
        crypt(password, crypt.mksalt(method=crypt.METHOD_CRYPT))
    )


def make_password_md5_crypt(password):
    """Password implementation for MD5-CRYPT.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    return "{{MD5-CRYPT}}{}".format(
        crypt(password, crypt.mksalt(method=crypt.METHOD_MD5))
    )


def make_password_sha256_crypt(password):
    """Password implementation for SHA256-CRYPT.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    return "{{SHA256-CRYPT}}{}".format(
        crypt(password, crypt.mksalt(method=crypt.METHOD_SHA256))
    )


def make_password_sha512_crypt(password):
    """Password implementation for SHA512-CRYPT

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    return "{{SHA512-CRYPT}}{}".format(
        crypt(password, crypt.mksalt(method=crypt.METHOD_SHA512))
    )


def random_password():
    """Create a random hashed password for user creation.

    The password is 16-digit long.

    Returns:
        string: random hashed password.
    """
    random_password = "".join(
        [random.choice(string.ascii_letters + string.digits) for n in range(16)]
    )
    return make_password(random_password)
