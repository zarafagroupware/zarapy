Zarapy
======

Zarapy is a GUI web application which can be used to "look into" Zarafa.
It's similiar to OutlookSpy and MFCMAPI but it's Zarafa specific. (This program isn't actively supported by Zarafa)

![Zarapy](https://raw.githubusercontent.com/zarafagroupware/zarapy/master/zarapy/static/image/zarapy.png "Zarapy example")


Features
========

Zarapy supports:

* List all  user on a Zarafa Server
* Viewing the store of the user
* List the folders of the users
* list all the item per folder
* list the softdelete
* list properties per item
* Export an email as eml
* View mail and attachments
* Download attachments
* Delete an item
* Change properties on an item
* Remove properties on an item
* Add properties on an item


Dependencies
============

Zarapy depends on a few Python libraries:

* [python-zarafa](https://github.com/zarafagroupware/python-zarafa.git)
* [python-mapi](https://download.zarafa.com/community/final/)
* Flask

Usage
=====

    python run.py (requires root permissions to connect to the socket for an system session)

Connect to a remote server
=======================

    python run.py  -s https://serverip:237/zarafa -k /etc/zarafa/ssl/server.pem -p password


Using user sessions
===================

    python run.py  -s https://serverip:237/zarafa -U user -P password
