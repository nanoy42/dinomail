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
Api resources.
"""
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.fields import CharField, ForeignKey
from tastypie.models import ApiKey
from tastypie.resources import ModelResource, Resource

from core.models import VirtualAlias, VirtualDomain, VirtualUser
from core.utils import make_password


class ApiKeyAuthorization(Authorization):
    """
    Special authorization which select only the object related for the logged user.

    Used for the ApiKey resource.
    """

    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)


class VirtualDomainResource(ModelResource):
    """Api resource for virtual domains.
    """

    class Meta:
        queryset = VirtualDomain.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()


class VirtualUserResource(ModelResource):
    """Api resource for virtual users.

    The password field is voluntarily excluded as a special resource is set for this field.
    """

    domain = ForeignKey(VirtualDomainResource, "domain")

    class Meta:
        queryset = VirtualUser.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        fields = ("email", "quota")


class VirtualAliasResource(ModelResource):
    """Api resource for virtual aliases.
    """

    domain = ForeignKey(VirtualDomainResource, "domain")

    class Meta:
        queryset = VirtualAlias.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()


class ChangeUserPasswordResource(ModelResource):
    """Api resource to change a user's password.
    """

    class Meta:
        queryset = VirtualUser.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        fields = ["password"]
        list_allowed_methods = []
        detail_allowed_methods = ["put", "patch"]

    def hydrate(self, bundle):
        """Reimplement the hydrate method to change the password by its hash.
        """
        bundle.data["password"] = make_password(bundle.data["password"])
        return bundle


class ApiKeyResource(ModelResource):
    """Api resource for api keys.
    """

    class Meta:
        queryset = ApiKey.objects.all()
        list_allowed_methods = ["get"]
        detail_allowed_methods = ["get"]
        authorization = ApiKeyAuthorization()
        authentication = BasicAuthentication()
