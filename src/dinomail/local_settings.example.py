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

import os

from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = ""
DEBUG = False
ALLOWED_HOSTS = []

# DATABASES

DATABASES = {}

# I18N

LANGUAGE_CODE = "en"

# Static

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# API (see tastypie documentation)

API_LIMIT_PER_PAGE = 0

# DINOMAIL settings

DINOMAIL_NAME = "DinoMail"
DINOMAIL_CATCH_LINE = _("Peaceful emails !")
DINOMAIL_LEGALS = """
"""
DINOMAIL_PASSWORD_SCHEME = "core.utils.make_password_ssha512"
