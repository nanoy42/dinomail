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
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tastypie.models import create_api_key

from .utils import make_password, random_password

# Automatically create api key for user
signals.post_save.connect(create_api_key, sender=User)


class VirtualDomain(models.Model):
    """Model to store virtual domains.

    A virtual domain is a domain that will be managed by the mail server.

    Args:
        name (string): name of the domain (example.org by instance). This is the only required field.
        dkim_key_name (string): name of the dkim key (as in the dns record name).
        dkim_key (string): the value of the dkim public key.
        dkim_status (int): stored value of the dkim status (picked form DkimStatus).
        dkim_last_update (date): last time the dkim_status attribute was updated.
        display_name (string): display name for te xml autconfiguration file.
        short_display_name (string): short display name for the xml autoconfiguration file.
        imap_address (string): imap address for the xml autoconfiguration file. If not set, imap.(name of domain) is used.
        pop_address (string): pop address for the xml autoconfiguration file. If not set, the pop section is ignored.
        smtp_address (string): smtp address for the xml autoconfiguration file. If not set, smtp.(name of domain) is used.
        """

    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    class DkimStatus(models.IntegerChoices):
        """Choices for DKIM status
        """

        NOTSET = 0, _("not set")
        NOTFOUND = 1, _("dns record not found")
        NODNSKEY = 2, _("no dns key found in record")
        NOMATCH = 3, _("key and dns record don't match")
        OK = 4, _("ok")

    name = models.CharField(max_length=50, unique=True, verbose_name=_("name"))
    dkim_key_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("dkim key name")
    )
    dkim_key = models.TextField(blank=True, verbose_name=_("dkim key"))
    dkim_status = models.IntegerField(
        choices=DkimStatus.choices,
        verbose_name=_("dkim status"),
        default=DkimStatus.NOTSET,
    )
    dkim_last_update = models.DateTimeField(
        auto_now_add=True, verbose_name=_("dkim status last update")
    )
    display_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("display name")
    )
    short_display_name = models.CharField(
        max_length=50, blank=True, verbose_name=_("short display name")
    )
    imap_address = models.URLField(blank=True, verbose_name=_("imap address"))
    pop_address = models.URLField(blank=True, verbose_name=_("pop address"))
    smtp_address = models.URLField(blank=True, verbose_name=_("smtp address"))

    def verify_dkim(self):
        """Verify the DKIM key.

        1. Verify if dkim_key_name and dkim_key are set
        2. Try to get the TXT record corresponding to the key
        3. Try to extract a key from the record
        4. Check the extracted key against the saved key

        1. If dkim_key_name or dkim_key is not set, it returns DkimStatus.NOTSET
        2. If no DNS record is found, it returns DkimStatus.NOTFOUND
        3. If no key can be extracted from the record, it returns DkimStatus.NODNSKEY
        4. If the keys don't match, it returns DkimStatus.NOMATCH
        5. If everything is good, it returns DkimStatus.OK

        Returns:
            int: dkim status
        """
        if self.dkim_key_name and self.dkim_key:
            try:
                dns_answer = dns.resolver.query(
                    "{key_name}._domainkey.{domain}".format(
                        key_name=self.dkim_key_name, domain=self.name
                    ),
                    "TXT",
                )
            except:
                return self.DkimStatus.NOTFOUND
            text = dns_answer[0].to_text()
            match = re.match('^"(.*;\s?)*p=([^;"]*).*$', text)
            if not match:
                return self.DkimStatus.NODNSKEY
            if match.groups()[-1] != self.dkim_key:
                return self.DkimStatus.NOMATCH
            return self.DkimStatus.OK
        return self.DkimStatus.NOTSET

    def update_dkim_status(self):
        """Update the dkim status and update the date.

        TODO : Auto update after model save.
        """
        self.dkim_status = self.verify_dkim()
        self.dkim_last_update = timezone.now()
        self.save()

    def __str__(self):
        """str method for virtual domains.

        Returns:
            string: name of the virtual domain
        """
        return self.name


class VirtualUser(models.Model):
    """Model to store virtual users.

    A virtual user is an actual email account.

    Args:
        domain (VirtualDomain): virtual domain corresponding to the user.
        email (string): email of the user.
        password (string): hashed password of the user.
        quota (int): quota, in bytes, of the user. 
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    domain = models.ForeignKey(
        VirtualDomain, on_delete=models.CASCADE, verbose_name=_("domain")
    )
    email = models.EmailField(verbose_name=_("email"), unique=True)
    password = models.CharField(
        max_length=300, default=random_password, verbose_name=_("password")
    )
    quota = models.BigIntegerField(verbose_name=_("quota"), null=True, default=0)

    def __str__(self):
        """str method for virtual users.

        Returns:
            string: email of the user
        """
        return self.email

    def set_password(self, password):
        """Set password for the user.

        The password is hashed and saved.

        Args:
            password (string): plain password
        """
        self.password = make_password(password)
        self.save()

    def readable_quota(self):
        """Return a readable value for the quota.

        The quota is stored in bytes. This method return a human (readable) value (B, kB, MB, GB).

        Returns:
            string: readable value for the quota
        """
        value = self.quota
        if value < 1000:
            return "{} B".format(value)
        elif value < 1000000:
            return "{} kB".format(int(value / 1000))
        elif value < 1000000000:
            return "{} MB".format(int(value / 1000000))
        else:
            return "{} GB".format(int(value / 1000000000))

    def clean(self):
        """Clean method for the model.

        It should not be possible to create a user with an email that does not correspond to one of the managed domains.

        Raises:
            ValidationError: if the email domain and domain don't match.
        """
        match = re.match("^[^@]*@(.*)$", self.email)
        domain = None
        if match:
            domain = match.groups()[0]
        if domain != self.domain.name:
            raise ValidationError(
                _(
                    "The domain of {email} ({email_domain}) is not the same as the domain {domain}"
                ).format(email=self.email, email_domain=domain, domain=self.domain.name)
            )

    def save(self, *args, **kwargs):
        """Override save method to call full clean before saving.

        Note that full clean itself calls clean.
        """
        self.full_clean()
        return super(VirtualUser, self).save(*args, **kwargs)


class VirtualAlias(models.Model):
    """Model to store aliases.

    Args:
        domain (VirtualDomain): domain of the source.
        source (string): source email.
        destination (string): destination email.
    """

    class Meta:
        verbose_name = _("alias")
        verbose_name_plural = _("aliases")

    domain = models.ForeignKey(
        VirtualDomain, on_delete=models.CASCADE, verbose_name=_("domain")
    )
    source = models.EmailField(verbose_name=_("source"))
    destination = models.EmailField(verbose_name=_("destination"))

    def __str__(self):
        return "{} -> {}".format(self.source, self.destination)

    def exterior(self):
        """Tets if an alias is considered as exterior.

        An alias is considered as exterior if the domain of the destination is not one of the managed domains.

        Returns:
            bool: True if the destination domain is not managed by the system and False otherwise
        """
        match = re.match("^[^@]*@(.*)$", self.destination)
        if match:
            destination_domain = match.group(1)
            domains = VirtualDomain.objects.filter(name=destination_domain)
            if domains:
                return False
        return True

    def verify(self):
        """Verify the destination.

        In case the mail is not exterior, it checks that the destination email is either the source of another alias or an actual user.

        Returns:
            bool: True if the destination email exists or is an exterior alias
        """
        if not self.exterior():
            emails = VirtualUser.objects.filter(email=self.destination)
            aliases = VirtualAlias.objects.filter(source=self.destination)
            if not emails and not aliases:
                return False
        return True

    def clean(self):
        """Clean method for the model.

        It should not be possible to create an alias with a source email that does not correspond to one of the managed domains.

        Raises:
            ValidationError: if the source domain and domain don't match.
        """
        match = re.match("^[^@]*@(.*)$", self.source)
        domain = match.groups()[0]
        if domain != self.domain.name:
            raise ValidationError(
                _(
                    "The domain of {email} ({email_domain}) is not the same as the domain {domain}"
                ).format(
                    email=self.source, email_domain=domain, domain=self.domain.name
                )
            )

    def save(self, *args, **kwargs):
        """Override save method to call full clean before saving.

        Note that full clean itself calls clean.
        """
        self.full_clean()
        return super(VirtualAlias, self).save(*args, **kwargs)
