API
===

DinoMail exposes an API. The API allows to :

 * get a token
 * list, detail, create, modify and delete a virtual domain
 * list, detail, create, modify, modify password of and delete a virtual user
 * list, detail, create, modify and delete a virtual alias

Authentication
##############

For the most part of the API, you will need to authenticate with an ApiKey : ``Authorization: ApiKey username:apikey``.

To get an api key, you can query the url ``/api/apikey/`` with a basic authentication : ``Authorization: Basic username:password``.

Virtual domains, users and aliases urls
#######################################

The basis URLS are 

 * ``/api/virtualdomain``
 * ``/api/virtualuser``
 * ``/api/virtualalias``

You can then, for each of those basis urls, query

 * ``/`` (``GET``) : list of all objects.
 * ``/`` (``POST``) : add an object.
 * ``/<pk>/`` (``GET``) : get detail for object with primary key ``<pk>``.
 * ``/<pk>/`` (``POST``) : update all fields of object with primary key ``<pk>``.
 * ``/<pk>/`` (``PATCH``) : update specified fields of object with primayr key ``<pk>``.
 * ``/<pk>/`` (``DELETE``) : delete object with primary key ``<pk>``.

.. note:: A ``POST`` on ``/api/virtualuser/<pk>`` will not reset the password.

There is also a special URL to change a user's password : ``/api/changeuserpassword/<pk>``, (``POST`` or ``PATCH`` are available). You have to transmit the plain text password.