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
Admin for core app.
"""
from django.contrib import admin

from .models import VirtualAlias, VirtualDomain, VirtualUser


class VirtualDomainAdmin(admin.ModelAdmin):
    """Admin class for virtual domains
    """

    list_display = ("name", "dkim_status", "dkim_last_update", "display_name")
    ordering = ("name",)
    search_fields = ("name",)
    list_filter = ("dkim_status",)
    fields = (
        "name",
        "dkim_key_name",
        "dkim_key",
        "display_name",
        "short_display_name",
        "imap_address",
        "pop_address",
        "smtp_address",
    )


class VirtualUserAdmin(admin.ModelAdmin):
    """Admin class for virtual users.
    """

    list_display = ("email", "domain", "readable_quota")
    ordering = ("email", "quota")
    search_fields = ("email", "domain")
    list_filter = ("domain",)
    fields = ("domain", "email", "quota")


class VirtualAliasAdmin(admin.ModelAdmin):
    """Admin class for virtual aliases.
    """

    list_display = ("__str__", "source", "destination", "domain")
    ordering = ("source", "destination")
    search_fileds = ("source", "destination", "domain")
    list_filter = ("domain",)
    fields = ("domain", "source", "destination")


admin.site.register(VirtualAlias, VirtualAliasAdmin)
admin.site.register(VirtualUser, VirtualUserAdmin)
admin.site.register(VirtualDomain, VirtualDomainAdmin)
