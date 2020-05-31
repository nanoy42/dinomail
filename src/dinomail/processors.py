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
Cutsom processor for DinoMail.
"""
from django.conf import settings


def conf_processor(request):
    """Setting processors.

    This processor let the templates have access to some chosen variables of the settings.

    Args:
        request (HttpRquest): django request object.

    Returns:
        dict: context with the chosen values.
    """
    return {
        "DINOMAIL_NAME": settings.DINOMAIL_NAME,
        "DINOMAIL_CATCH_LINE": settings.DINOMAIL_CATCH_LINE,
        "DINOMAIL_LEGALS": settings.DINOMAIL_LEGALS,
    }
