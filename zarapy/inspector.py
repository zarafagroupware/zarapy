#!/usr/bin/env python
from flask import Flask, render_template,  request, session,jsonify,Blueprint

import time, sys, difflib
from MAPI.Tags import SYNC_NEW_MESSAGE
import zarafa



inspect_page = Blueprint('inspect_page', __name__, template_folder='templates')

def opt_args():
    parser = zarafa.parser('skpcfUP')
    return parser.parse_args()

ITEM_MAPPING = {}

def proplist(item):
    biggest = max((len(prop.strid or 'None') for prop in item.props()))
    props = []
    for prop in item.props():
        offset = biggest - len(prop.strid or 'None')
        props.append('%s %s%s\n' % (prop.strid, ' ' * offset,  prop.strval))
    return props

def diffitems(item, old_item=[], delete=False):
    if delete:
        oldprops = proplist(item)
        newprops = []
        new_name = ''
        old_name = item.subject
    else:
        oldprops = proplist(old_item) if old_item else []
        newprops = proplist(item)
        new_name = item.subject
        old_name = item.subject if old_item else ''

    for line in difflib.unified_diff(oldprops, newprops, tofile=new_name, fromfile=old_name):
        sys.stdout.write(line)

class Importer:
    def update(self, item, flags):
        print '\033[1;41mUpdate: subject: %s folder: %s sender: %s (%s)\033[1;m' % (item.subject, item.folder, item.sender.email, time.strftime('%a %b %d %H:%M:%S %Y'))
        if not flags & SYNC_NEW_MESSAGE:
            old_item = ITEM_MAPPING[item.sourcekey]
        else:
            ITEM_MAPPING[item.sourcekey] = item
            old_item = False

        diffitems(item, old_item)
        print '\033[1;41mEnd Update\033[1;m\n'


    def delete(self, item, flags): # only item.sourcekey is available here!
        rm_item = ITEM_MAPPING[item.sourcekey]
        if rm_item:
            print '\033[1;41mBegin Delete: subject: %s folder: %s sender: %s (%s)\033[1;m' % (rm_item.subject, rm_item.folder, rm_item.sender.email, time.strftime('%a %b %d %H:%M:%S %Y'))
            diffitems(rm_item, delete=True)
            print '\033[1;41mEnd Delete\033[1;m\n'
            del ITEM_MAPPING[rm_item.sourcekey]





@inspect_page.route('/test')
def test():
    return render_template('trace.html')

@inspect_page.route('/_trace')
def trace():
    options, args = opt_args()
    user = session['user']
    folder = session['folder']
    user = zarafa.Server(options).user(user)
    #folder = 'Inbox'
    folder = user.store.folder(folder)
    for item in folder.items():
        ITEM_MAPPING[item.sourcekey] = item
        print 'Mapping of items and sourcekey complete'

        folder_state = folder.state
        new_state = folder.sync(Importer(), folder_state) # from last known state
        while True:
            new_state = folder.sync(Importer(), folder_state) # from last known state
            if new_state != folder_state:
                folder_state = new_state
            time.sleep(1)

    return jsonify(result=new_state)
