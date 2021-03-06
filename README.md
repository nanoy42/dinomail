# DinoMail

[![Documentation Status](https://readthedocs.org/projects/dinomail/badge/?version=latest)](https://dinomail.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/nanoy42/dinomail/badge.svg?branch=master)](https://coveralls.io/github/nanoy42/dinomail?branch=master)
[![github-actions](https://github.com/nanoy42/dinomail/workflows/Django%20CI/badge.svg)](https://github.com/nanoy42/dinomail/workflows/Django%20CI)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style black](https://img.shields.io/badge/code%20style-black-000000.svg)]("https://github.com/psf/black)
[![GitHub release](https://img.shields.io/github/release/nanoy42/dinomail.svg)](https://github.com/nanoy42/dinomail/releases/)


![logo](https://github.com/nanoy42/dinomail/raw/master/res/dinomail.jpg "Logo")

DinoMail is a simple webapp to manage virtual domains, users and aliases.

It has been firstly developped to work with postfix and dovecot, following the tutorial here : https://workaround.org/ispmail.

There is an Android App for DinoMail : https://play.google.com/store/apps/details?id=fr.nanoy.dinomail_app&hl=fr and https://github.com/nanoy42/dinomail_app.

Credits to Zaiken for the logo.

## What DinoMail can do ?

DinoMail allows you to :

 * create virtual domains
 * verify DKIM , DMARC and SPF for a domain
 * create virtual users (password being stored with the good prefix for dovecot, several schemes are available)
 * assign quotas to a user
 * create internal and external aliases (with some verification functionality)
 * generate auto-config xml files

## What DinoMail can't do ?

DinoMail

 * is not a web-mail
 * will not configure the mail stack for you
 * will not be responsible for any lost emails (see license part)


## Supported languages

The following languages are supported:

  * English
  * French

## Contributing

See the following 

## Documentation

DinoMail documentation can be found at https://dinomail.readthedocs.io/en/latest/.

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

In particular, DinoMail will not take any responsibility for any lost email, missed appointment or thermonuclear war. You have the source code and you should verify it before installing it.

## Development information

### Tests

Tests are launched automatically when merging or making a pull request on master or dev.

You can launch the tests manually with 
```
cd src
python3 manage.py test
```

### Docker

You can use docker, **for development purposes only** with the following commands:

```
docker build .
docker-compose up
```

You can create a superuser with the following command:

```
docker exec <container> bash -c "python manage.py createsuperuser"
```

Docker will automatically start a container for a postgresql database and the web container. There is no need to reload the container when modifying code. Please note that the `local_settings.py` file will be overwritten by the `local_settings.docker.py` file.