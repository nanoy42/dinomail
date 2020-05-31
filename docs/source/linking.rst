Linking DinoMail to postfix and dovecot
=======================================

Now we are going to see how to link DinoMail data to postfix and dovecot in order to have a working email server. 

.. note:: This is an example implementation. Other implementations could work. This is mainly inspired by `<https://workaround.org/ispmail>`_.

We will use a postgresql database, but it could work with other types of database. We redirect to the documentations of postfix and dovecot. The user is ``dinomail`` with password ``secret``. The database is ``dinomail``.

.. warning:: Additional packages are needed for databases with postfix and dovecot (postfix-pgsql and dovecot-pgsql or postfix-mysql and dovecot-mysql for debian packages).

Postfix
#######

Create configuration files
**************************

First we create a pgsql.d directory in ``/etc/postfix`` :

.. code-block:: bash

    mkdir /etc/postfix/pgsql.d

Next we are going to populate the virtual domains :

.. code-block:: bash

    # /etc/postfix/pgsql.d/virtual-mailbox-domains.cf
    user = dinomail
    password = secret
    hosts = 127.0.0.1
    dbname = dinomail
    query = SELECT 1 FROM dinomail_virtualdomain WHERE name='%s'

.. note:: We select 1 because we must have a map with the key being the domain and the value is meaningless.

We do the same for virtual users and virtual aliases : 

.. code-block:: bash

    # /etc/postfix/pgsql.d/virtual-mailbox-maps.cf
    user = dinomail
    password = secret
    hosts = 127.0.0.1
    dbname = dinomail
    query = SELECT 1 FROM dinomail_virtualuser WHERE email='%s'

and 

.. code-block:: bash

    # /etc/postfix/pgsql.d/virtual-alias-maps.cf
    user = dinomail
    password = secret
    hosts = 127.0.0.1
    dbname = dinomail
    query = SELECT destination FROM dinomail_virtualalias WHERE source='%s'


We can also add an email2email.cf file which is a map where the key is an email and the value is the same email. It can be useful for wildcard matches for example :

.. code-block:: bash

    # /etc/postfix/pgsql.d/email2email.cf
    user = dinomail
    password = secret
    hosts = 127.0.0.1
    dbname = dinomail
    query = SELECT email FROM dinomail_virtualuser WHERE email='%s'

Test the configuration files
****************************

You can use the ``postmap`` utility. If you have the domain ``example.org``, a user ``test@example.org`` and an alias ``postmaster@example.org -> test@example.org``.

.. code-block:: bash

    postmap -q example.org pgsql:/etc/postfix/pgsql.d/virtual-mailbox-domains.cf
    postmap -q test@example.org pgsql:/etc/postfix/pgsql.d/virtual-mailbox-maps.cf
    postmap -q postmaster@example.org pgsql:/etc/postfix/pgsql.d/virtual-alias-maps.cf
    postmap -q test@example.org pgsql:/etc/postfix/pgsql.d/email2email.cf


It should return 1,1, test@example.org and test@example.org.

Make postfix use the configuration files
****************************************

Next, we have to specify postfix how these maps should be used. You can edit the ``main.cf`` file in ``/etc/postfix`` or use the ``postconf`` utility :

.. code-block:: bash

    postconf virtual_mailbox_domains=pgsql:/etc/postfix/pgsql.d/virtual-mailbox-domains.cf
    postconf virtual_mailbox_maps=pgsql:/etc/postfix/pgsql.d/virtual-mailbox-maps.cf
    postconf virtual_alias_maps=pgsql:/etc/postfix/pgsql.d/virtual-alias-maps.cf

Dovecot
#######

Next we want Dovecot to use the information in the database too. We edit ``/etc/dovecot/conf.d/auth-sql.conf.ext`` and set 

.. code-block:: bash

    userdb {
        driver = sql
        args = /etc/dovecot/dovecot-sql.conf.ext
    }

Then we edit ``/etc/dovecot/dovecot-sql.conf.ext`` and set 

.. code-block:: bash

    driver = pgsql
    connect = host=127.0.0.1 dbname=dinomail user=dinomail password=secret
    user_query = SELECT email as user, \
    concat('*:bytes=', quota) AS quota_rule, \
    '/var/vmail/%d/%n' AS home, \
    5000 AS uid, 5000 AS gid \
    FROM dinomail_virtualuser WHERE email='%u'
    password_query = SELECT password FROM dinomail_virtualuser WHERE email='%u'
    iterate_query = SELECT email AS user FROM dinomail_virtualuser