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
import hashlib
import os
import random
import string


def make_password(password):
    """Hash a password using SHA512. Compatible with dovecot.

    The password is hashsed ans stored as a dovecot-complient way, i.e.
    {algorithm}passwordsalt

    TODO : implement other hasing algorithms and have a setting

    Args:
        password (string): the non-hashed password

    Returns:
        string: the hashed password
    """
    salt = os.urandom(16)
    sha = hashlib.sha512()
    password = password.encode("utf-8")
    sha.update(password)
    sha.update(salt)
    ssha512 = base64.b64encode(sha.digest() + salt)
    return "{{SSHA512}}{}".format(ssha512.decode("utf-8"))


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
