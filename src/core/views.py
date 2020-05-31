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

import re

import dns.resolver
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tastypie.models import ApiKey, create_api_key

from .forms import (DeleteForm, UpdatePasswordVirtualUserForm,
                    VirtualAliasForm, VirtualDomainForm, VirtualUserForm)
from .models import VirtualAlias, VirtualDomain, VirtualUser
from .utils import make_password


@login_required
def home(request):
    """Home view.

    This query the total number of virtual domains, users and aliases to display on home page.

    Args:
        request (HttpRequest): django request object

    Returns:
        HttpResponse: django response object
    """
    virtual_domains = VirtualDomain.objects.all().count()
    virtual_users = VirtualUser.objects.all().count()
    virtual_aliases = VirtualAlias.objects.all().count()
    return render(
        request,
        "home.html",
        {
            "virtual_domains": virtual_domains,
            "virtual_aliases": virtual_aliases,
            "virtual_users": virtual_users,
            "active": "home",
        },
    )


@login_required
@permission_required("core.view_virtualdomain")
def virtual_domains_index(request):
    """List all virtual domains.

    Args:
        request (HttpRequets): django request object

    Returns:
        HttpResponse: django response object
    """
    virtual_domains = VirtualDomain.objects.all()
    return render(
        request,
        "virtual_domains_index.html",
        {"virtual_domains": virtual_domains, "active": "virtual-domains"},
    )


@login_required
@permission_required("core.add_virtualdomain")
def add_virtual_domain(request):
    """View to add a virtual domain.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    form = VirtualDomainForm(request.POST or None)
    if form.is_valid():
        virtual_domain = form.save()
        messages.success(
            request, _("Domain {} was created.").format(virtual_domain.name)
        )
        return redirect(reverse("virtual-domains-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Add domain"),
            "form_button": _("Add"),
            "active": "virtual-domains",
        },
    )


@login_required
@permission_required("core.change_virtualdomain")
def edit_virtual_domain(request, pk):
    """View to edit a virtual domain.

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the virtual domain to edit/

    Returns:
        HttpResponse: django response object.
    """
    virtual_domain = get_object_or_404(VirtualDomain, pk=pk)
    form = VirtualDomainForm(request.POST or None, instance=virtual_domain)
    if form.is_valid():
        virtual_domain = form.save()
        messages.success(
            request, _("Domain {} was changed.").format(virtual_domain.name)
        )
        return redirect(reverse("virtual-domains-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Change domain {}").format(virtual_domain.name),
            "form_button": _("Change"),
            "active": "virtual-domains",
        },
    )


@login_required
@permission_required("core.delete_virtualdomain")
def delete_virtual_domain(request, pk):
    """View to delete a virtual domain.

    The view first displays a form in which the user have to enter the domain name to confirm the deletion.

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the virtual domain to detete.

    Returns:
        HttpResponse: django response object.
    """
    virtual_domain = get_object_or_404(VirtualDomain, pk=pk)
    form = DeleteForm(
        request.POST or None, label=_("Enter domain name to confirm deletion")
    )
    if form.is_valid():
        if form.cleaned_data["verifier"] == virtual_domain.name:
            message = _("Domain {} was deleted").format(virtual_domain.name)
            virtual_domain.delete()
            messages.warning(request, message)
        else:
            messages.error(request, _("Names don't match. Operation cancelled."))
        return redirect(reverse("virtual-domains-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Delete domain {}").format(virtual_domain.name),
            "form_button": _("Delete"),
            "active": "virtual-domains",
        },
    )


@login_required
@permission_required("core.view_virtualdomain")
def update_dkim_virtual_domain(request, pk):
    """View to update the DKIM status.

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the virtual domain to update dkim status.

    Returns:
        HttpResponse: django response object.
    """
    virtual_domain = get_object_or_404(VirtualDomain, pk=pk)
    virtual_domain.update_dkim_status()
    return redirect(reverse("virtual-domains-index"))


@login_required
@permission_required("core.view_virtualdomain")
def dkim_scan_virtual_domain(request, pk):
    """View to display DKIM scan information.

    Args:
        request (HttpRequest): django request object
        pk (int): primary key of the virtual domain.

    Returns:
        HttpResponse: django response object.
    """
    virtual_domain = get_object_or_404(VirtualDomain, pk=pk)
    virtual_domain.update_dkim_status()
    url = "{key_name}._domainkey.{domain}".format(
        key_name=virtual_domain.dkim_key_name, domain=virtual_domain.name
    )
    try:
        dns_answer = dns.resolver.query(url, "TXT")[0].to_text()
    except:
        dns_answer = None
    if dns_answer:
        match = re.match('^"(.*;\s?)*p=([^;"]*).*$', dns_answer)
        if not match:
            key = None
        else:
            key = match.groups()[-1]
    else:
        key = None
    return render(
        request,
        "virtual_domains_dkim_scan.html",
        {
            "domain": virtual_domain,
            "url": url,
            "dns_answer": dns_answer,
            "key": key,
            "active": "virtual-domains",
        },
    )


@login_required
@permission_required("core.view_virtualdomain")
def autoconfig_virtual_domain(request, pk):
    """View to generate autoconfig xml file

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the virtual domain.

    Returns:
        HttpResponse: django response object.
    """
    virtual_domain = get_object_or_404(VirtualDomain, pk=pk)
    t = loader.get_template("autoconfig.xml")
    response = HttpResponse(
        t.render({"domain": virtual_domain}), content_type="application/xml"
    )
    response["Content-Disposition"] = "attachment; filename=autoconfig.xml"
    return response


@login_required
@permission_required("core.view_virtualuser")
def virtual_users_index(request):
    """List all virtual users.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    virtual_users = VirtualUser.objects.all()
    return render(
        request,
        "virtual_users_index.html",
        {"virtual_users": virtual_users, "active": "virtual-users"},
    )


@login_required
@permission_required("core.add_virtualuser")
def add_virtual_user(request):
    """View to add a virtual user.

    Note that a random password is chosen for the user at its creation.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    form = VirtualUserForm(request.POST or None)
    if form.is_valid():
        virtual_user = form.save()
        messages.success(request, _("User {} was created.").format(virtual_user.email))
        return redirect(reverse("virtual-users-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Add user"),
            "form_button": _("Add"),
            "active": "virtual-users",
        },
    )


@login_required
@permission_required("core.change_virtualuser")
def edit_virtual_user(request, pk):
    """View to edit a virtual user.

    Note that this view don't update the user's password.

    Args:
        request (HttpRequest): django request object.
        pk (pk): primary key of the virtual user to edit.

    Returns:
        HttpResponse: django response object.
    """
    virtual_user = get_object_or_404(VirtualUser, pk=pk)
    form = VirtualUserForm(request.POST or None, instance=virtual_user)
    if form.is_valid():
        virtual_user = form.save()
        messages.success(request, _("user {} was changed.").format(virtual_user.email))
        return redirect(reverse("virtual-users-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Change user {}").format(virtual_user.email),
            "form_button": _("Change"),
            "active": "virtual-users",
        },
    )


@login_required
@permission_required("core.change_virtualuser")
def edit_password_virtual_user(request, pk):
    """View to edit a user's password.

    Args:
        request (HttpRequest): django request object.
        pk (int): primary jey of the virtual user.

    Returns:
        HttpResponse: django response object.
    """
    virtual_user = get_object_or_404(VirtualUser, pk=pk)
    form = UpdatePasswordVirtualUserForm(request.POST or None)
    if form.is_valid():
        virtual_user.set_password(form.cleaned_data["password"])
        messages.success(
            request, _("{}'s password was changed").format(virtual_user.email)
        )
        return redirect(reverse("virtual-users-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Change {}'s password").format(virtual_user.email),
            "form_button": _("Change"),
            "active": "virtual-users",
        },
    )


@login_required
@permission_required("core.delete_virtualuser")
def delete_virtual_user(request, pk):
    """View to delete a virtual user.

    The user has to enter the virtual user's email to confirm deletion.

    Args:
        request (HttpRequest): django request object.
        pk (int): primary key of the virtual user to delete.

    Returns:
        HttpResponse: django response object.
    """
    virtual_user = get_object_or_404(VirtualUser, pk=pk)
    form = DeleteForm(
        request.POST or None, label=_("Enter user's email to confirm deletion")
    )
    if form.is_valid():
        if form.cleaned_data["verifier"] == virtual_user.email:
            message = _("User {} was deleted").format(virtual_user.email)
            virtual_user.delete()
            messages.warning(request, message)
        else:
            messages.error(request, _("Emails don't match. Operation cancelled"))
        return redirect(reverse("virtual-users-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Delete user {}").format(virtual_user.email),
            "form_button": _("Delete"),
            "active": "virtual-users",
        },
    )


@login_required
@permission_required("core.view_virtualalias")
def virtual_aliases_index(request):
    """List all virtual aliases.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    virtual_aliases = VirtualAlias.objects.all()
    return render(
        request,
        "virtual_aliases_index.html",
        {"virtual_aliases": virtual_aliases, "active": "virtual-aliases"},
    )


@login_required
@permission_required("core.add_virtualalias")
def add_virtual_alias(request):
    """View to add a virtual alias.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    form = VirtualAliasForm(request.POST or None)
    if form.is_valid():
        virtual_alias = form.save()
        messages.success(
            request, "L'utilisateur {} a bien été créé".format(virtual_alias)
        )
        return redirect(reverse("virtual-aliases-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Add alias"),
            "form_button": _("Add"),
            "active": "virtual-aliases",
        },
    )


@login_required
@permission_required("core.change_virtualalias")
def edit_virtual_alias(request, pk):
    """View to edit a virtual alias.

    Args:
        request (HttRequest): django request object.
        pk (int): primary key of the virtual alias to edit.

    Returns:
        HttpResponse: django response onject.
    """
    virtual_alias = get_object_or_404(VirtualAlias, pk=pk)
    form = VirtualAliasForm(request.POST or None, instance=virtual_alias)
    if form.is_valid():
        virtual_alias = form.save()
        messages.success(request, _("Alias {} was changed").format(virtual_alias))
        return redirect(reverse("virtual-aliases-index"))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": _("Change alias {}").format(virtual_alias),
            "form_button": _("Change"),
            "active": "virtual-aliases",
        },
    )


@login_required
@permission_required("core.delete_virtualalias")
def delete_virtual_alias(request, pk):
    """View to delete a virtual alias.

    No verification is done.

    Args:
        request (HttRequest): django request object.
        pk (int): primary key of the virtual alias to dleete.

    Returns:
        HttpResponse: django response object.
    """
    virtual_alias = get_object_or_404(VirtualAlias, pk=pk)
    message = _("Alias {} was deleted").format(virtual_alias)
    virtual_alias.delete()
    messages.warning(request, message)
    return redirect(reverse("virtual-aliases-index"))


@login_required
def search(request):
    """Search view.

    The search parameter is used to find :
        * domains with the domain name containing the parameter.
        * users with the email containing the parameter.
        * aliases with the source or destination email containing the parameter.

    Args:
        request (HttpRequest): django request obejct.

    Returns:
        HttpResponse: django response object.
    """
    search = request.GET.get("q")
    if search:
        virtual_domains = VirtualDomain.objects.filter(name__icontains=search)
        virtual_users = VirtualUser.objects.filter(email__icontains=search)
        virtual_aliases = VirtualAlias.objects.filter(
            Q(source__icontains=search) | Q(destination__icontains=search)
        )
    else:
        virtual_domains = VirtualDomain.objects.none()
        virtual_users = VirtualUser.objects.none()
        virtual_aliases = VirtualAlias.objects.none()
    return render(
        request,
        "search.html",
        {
            "search": search,
            "virtual_domains": virtual_domains,
            "virtual_users": virtual_users,
            "virtual_aliases": virtual_aliases,
        },
    )


def legals(request):
    """Legal view.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    return render(request, "legals.html", {"active": "legals"})


@login_required
def regen_api_key(request):
    """View to regen or create the ApiKey for the logged user.

    Note the the ApiKey sould have been created when the user was created.

    Args:
        request (HttpRequest): django request object.

    Returns:
        HttpResponse: django response object.
    """
    req = ApiKey.objects.filter(user=request.user)
    if req:
        api_key = req[0]
        api_key.key = api_key.generate_key()
        api_key.save()
        messages.success(request, _("Api key was regenerated."))
    else:
        ApiKey.objects.create(user=request.user)
        messages.success(request, _("Api key was created."))
    return redirect(reverse("home"))
