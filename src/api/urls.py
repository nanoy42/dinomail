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
URL patters for api
"""
from django.urls import include, path
from tastypie.api import Api

from .api import (ApiKeyResource, ChangeUserPasswordResource,
                  VirtualAliasResource, VirtualDomainResource,
                  VirtualUserResource)

api = Api(api_name="api")
api.register(VirtualDomainResource())
api.register(VirtualUserResource())
api.register(VirtualAliasResource())
api.register(ChangeUserPasswordResource())
api.register(ApiKeyResource())

urlpatterns = [path("", include(api.urls))]
