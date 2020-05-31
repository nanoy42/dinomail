# DinoMail

DinoMail is a simple webapp to manage virtual domains, users and aliases.

It has been firstly developped to work with postfix and dovecot, following the tutorial here : https://workaround.org/ispmail

## What DinoMail can do ?

DinoMail allows you to :

 * create virtual domains
 * verify the DKIM signature for a domain
 * create virtual users (password being stored with the good prefix for dovecot)
 * assignate quotas to a user
 * create internal and external aliases (with some verification functionnality)
 * generate autoconfig xml files

## What DinoMail can't do ?

DinoMail

 * is not a webmail
 * will not configure the mail stack for you
 * will not be reponsible for any lost emails (see license part)

## Screenshots

![home](https://github.com/nanoy42/DinoMail/raw/master/res/screenshots/home.png "Home page")
![domains](https://github.com/nanoy42/DinoMail/raw/master/res/screenshots/domains.png "Domains page")
![users](https://github.com/nanoy42/DinoMail/raw/master/res/screenshots/users.png "Users page")
![aliases](https://github.com/nanoy42/DinoMail/raw/master/res/screenshots/aliases.png "Aliases page")
![search](https://github.com/nanoy42/DinoMail/raw/master/res/screenshots/search.png "Search page")

## License

DinoMail is distributed under th GPLv3 license :

DinoMail is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

DinoMail is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DinoMail.  If not, see <https://www.gnu.org/licenses/>.

In particular, DinoMail will not take any responsability for any lost email, missed appointement or thermonuclear war. You have the source code and you should verify it before installing it.
