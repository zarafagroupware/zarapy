from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from flask import render_template
from app import app

from collections import OrderedDict
import zarafa

@app.route('/')
@app.route('/index')
def index():
    users = {}
    for user in zarafa.Server().users():
        users[user.name] = {'name': user.name,
                            'company': user.company.name,
                            'guid': user.store.guid,
                            'server': user.server.name}
        users = OrderedDict(sorted(users.items(), key=lambda t: (t[1], t[0])))


    return render_template('index.html',
            title = 'Users',
            users = users)


@app.route('/viewuser/<company>/<user>')
def viewuser(company=None, user=None):
    props = {}

    for prop in zarafa.Server().company(company).user(user).props():
        props[prop.idname] = {'name': prop.idname,
                            'type': prop.typename,
                            'value': prop.strval()}


    return render_template('viewuser.html',
            title = 'User %s' % user,
            props = props,
            user = user,
            company = company)


@app.route('/listfolders/<company>/<user>/<foldername>')
@app.route('/listfolders/<company>/<user>')
def listfolders(company=None, user=None, foldername=None):
    folderitems = {}
    subfolders = {}

    if foldername:
        for folder in zarafa.Server().company(company).user(user).store.folders():
            if folder.entryid == foldername:
                for item in folder.items():
                    folderitems[item.entryid] = {'folderid': folder.entryid,
                                                'itemid': item.entryid,
                                                'itemsubject': item.subject}
    else:
        for folder in zarafa.Server().company(company).user(user).store.folders():
                    subfolders[folder.entryid] = {'folderid': folder.entryid,
                                                'foldername': folder.name}


    return render_template('listfolders.html',
            title = 'Folders for %s' % user,
            folderitems = folderitems,
            subfolders = subfolders,
            user = user,
            company = company)


@app.route('/listitem/<company>/<user>/<itemname>')
def listitem(company=None, user=None, foldername=None, itemname=None):
    props = {}

    if itemname:
        item = zarafa.Server().company(company).user(user).store.item(itemname)
        for prop in item.props():
            props[prop.idname] = {'name': prop.idname,
                                'type': prop.typename,
                                'value': prop.strval().decode('utf-8')}
    

    return render_template('listitem.html',
            title = 'Item for user %s' % user,
            props = props,
            itemname = itemname,
            user = user,
            company = company)

