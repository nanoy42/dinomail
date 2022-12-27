# CHANGELOG

## Version 1.1.1 (2022-12-27)

#### Others

* :arrow_up: Upgrade dependencies
* Change from pipfile to poetry

## Version 1.1.0 (2021-12-26)

#### Fixes

* :bug: Fix [#43](https://github.com/nanoy42/dinomail/issues/43)
* :bug: Fix [#33](https://github.com/nanoy42/dinomail/issues/33)
* :bug: Fix django warnings on auto fields
#### Docs

* :bug: Fix [#32](https://github.com/nanoy42/dinomail/issues/32)
#### Others

* :arrow_up: Upgrade dependencies

## Version 1.0.0
### Context
**Codename: Denver**

Denver is the last dinosaur.

### Changes

* Add favicon to the login page
* Add domain filters
* Add docker environment for dev
* Change TIME_ZONE setting to local settings
* Update dependencies
* Improve translations
* Add contributing.md file

### Update information
Recompile translations : `django-admin compilemessages`.

## Version 0.2
### Context
**Codename: Dilophosaurus**

Herrerasaurus were looking like Dilophosaurus in Jurrasic Park.

### Changes

* Add password schemes : 
    * PLAIN
    * PLAIN-TRUNC
    * CLEARTEXT
    * CLEAR
    * SHA
    * SSHA 
    * SHA256
    * SSHA256
    * SHA512
    * SSHA512
    * PLAIN-MD5
    * LDAP-MD5
    * CRYPT
    * DES-CRYPT
    * MD5-CRYPT
    * SHA256-CRYPT
    * SHA512-CRYPT
* Add DMARC and SPF support
* Add unit tests
* Add CI and coverage
* Documentation
* Minor fixes

### Update information
You should apply migrations : `python3 manage.py migrate` and recompile translations messages : `django-admin compilemessages`.

## Version 0.1.1
### Context
**Codename : Herrerasaurus**

Herrerasaurus was one of the earliest dinosaurs. It seems adapted for an early release.

### Changes

* Hotfix : add id field for virtual users api.

### Update information
No update information.

## Version 0.1
### Context
**Codename : Herrerasaurus**

Herrerasaurus was one of the earliest dinosaurs. It seems adapted for an early release.

### Features

The version 0.1 of DinoMail includes the following features :

* Create, modify, and delete virtual domains.
* Create, modify, and delete virtual users.
* Create, modify, and delete virtual aliases.
* Store a user's password in a dovecot-compliant way (using salted-SSHA512 hashing algorithm).
* Expose an API for the above points.
* Verify DKIM signature.
* Generate xml autoconfig file for a domain.

### Update information
There is no update information as there is no previous versions.