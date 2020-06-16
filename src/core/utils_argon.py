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
Password utils using argon2 for DinoMail. It requires argon2-cffi.
"""

from argon2 import PasswordHasher, Type


def make_password_argon2i(password):
    """Password implementation for ARGON2I.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    ph = PasswordHasher(type=Type.I)
    hash = ph.hash(password)
    return "{{ARGON2I}}{}".format(hash)


def make_password_argon2id(password):
    """Password implementation for ARGON2ID

    Args:
        password (string): the plain password

    Returns:
        string: the hashed passord with prefix and salt
    """
    ph = PasswordHasher(type=Type.ID)
    hash = ph.hash(password)
    return "{{ARGON2ID}}{}".format(hash)
