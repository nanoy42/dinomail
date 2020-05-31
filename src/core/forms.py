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
Forms for core app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import VirtualAlias, VirtualDomain, VirtualUser


class VirtualDomainForm(forms.ModelForm):
    """Form to create and change virtual domains.
    """

    class Meta:
        model = VirtualDomain
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


class VirtualUserForm(forms.ModelForm):
    """Form to create and change virtual users.
    """

    class Meta:
        model = VirtualUser
        fields = ("domain", "email", "quota")


class UpdatePasswordVirtualUserForm(forms.Form):
    """Form to edit a user's password 
    """

    password = forms.CharField(max_length=150)


class VirtualAliasForm(forms.ModelForm):
    """Form to cretae and change a virtual alias.
    """

    class Meta:
        model = VirtualAlias
        fields = ("domain", "source", "destination")


class DeleteForm(forms.Form):
    """Generic form to delete an object.

    Args:
        string label: label for the verifier field
    """

    verifier = forms.CharField(label=_("Verification chain"), max_length=200)

    def __init__(self, *args, **kwargs):
        if "label" in kwargs:
            label = kwargs.pop("label")
            super(DeleteForm, self).__init__(*args, **kwargs)
            self.fields["verifier"].label = label
