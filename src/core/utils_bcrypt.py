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
Password utils using bcrypt for DinoMail. It requires bcrypt.
"""

import bcrypt


def make_password_blf_crypt(password):
    """Password implementation for BLF-CRYPT.

    Args:
        password (string): the plain password

    Returns:
        string: the hashed password with prefix and salt
    """
    password = password.encode("utf-8")
    blf_crypt = bcrypt.hashpw(password, bcrypt.gensalt())
    return "{{BLF-CRYPT}}{}".format(blf_crypt.decode("utf-8"))
