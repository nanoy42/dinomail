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
URL patterns for core app.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

# Url patterns for virtual domains

urlpatterns_virtual_domains = [
    path("", views.virtual_domains_index, name="virtual-domains-index"),
    path("new", views.add_virtual_domain, name="virtual-domains-add"),
    path("<int:pk>/edit", views.edit_virtual_domain, name="virtual-domains-edit"),
    path("<int:pk>/delete", views.delete_virtual_domain, name="virtual-domains-delete"),
    path(
        "<int:pk>/update-status",
        views.update_virtual_domain,
        name="virtual-domains-update-status",
    ),
    path(
        "<int:pk>/update-dkim-status",
        views.update_dkim_virtual_domain,
        name="virtual-domains-update-dkim-status",
    ),
    path(
        "<int:pk>/update-dmarc-status",
        views.update_dmarc_virtual_domain,
        name="virtual-domains-update-dmarc-status",
    ),
    path(
        "<int:pk>/dkim-scan",
        views.dkim_scan_virtual_domain,
        name="virtual-domains-dkim-scan",
    ),
    path(
        "<int:pk>/dmarc-scan",
        views.dmarc_scan_virtual_domain,
        name="virtual-domains-dmarc-scan",
    ),
    path(
        "<int:pk>/autoconfig",
        views.autoconfig_virtual_domain,
        name="virtual-domains-autoconfig",
    ),
]

# Url patterns for virtual users

urlpatterns_virtual_users = [
    path("", views.virtual_users_index, name="virtual-users-index"),
    path("new", views.add_virtual_user, name="virtual-users-add"),
    path("<int:pk>/edit", views.edit_virtual_user, name="virtual-users-edit"),
    path(
        "<int:pk>/edit-password",
        views.edit_password_virtual_user,
        name="virtual-users-edit-password",
    ),
    path("<int:pk>/delete", views.delete_virtual_user, name="virtual-users-delete"),
]

# Url patterns for virtual aliases

urlpatterns_virtual_aliases = [
    path("", views.virtual_aliases_index, name="virtual-aliases-index"),
    path("new", views.add_virtual_alias, name="virtual-aliases-add"),
    path("<int:pk>/edit", views.edit_virtual_alias, name="virtual-aliases-edit"),
    path("<int:pk>/delete", views.delete_virtual_alias, name="virtual-aliases-delete"),
]

# Url patterns of core app

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("search", views.search, name="search"),
    path("legals", views.legals, name="legals"),
    path("regen-api-key", views.regen_api_key, name="regen-api-key"),
    path("virtual-domains/", include(urlpatterns_virtual_domains)),
    path("virtual-users/", include(urlpatterns_virtual_users)),
    path("virtual-aliases/", include(urlpatterns_virtual_aliases)),
]
