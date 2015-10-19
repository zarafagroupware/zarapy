#!/usr/bin/env python

from __future__ import unicode_literals
from flask import Flask, render_template, current_app, request, make_response, redirect, url_for, session,jsonify,Blueprint
from flask.sessions import SessionInterface
from flask.ext.paginate import Pagination
import click
import zarafa
import binascii
import os
from datetime import datetime
import cPickle as pickle
from MAPI.Util import *

from inspector import inspect_page
startdir = os.path.dirname(os.path.realpath(__file__))


def opt_args():
    parser = zarafa.parser('skpcfUP')
    return parser.parse_args()

def reverstag(proptag, type):
    return int(proptag, 16) - type >> 16

def printprop(typename, item):
    if typename == 'PT_MV_BINARY':
        listItem = []
        for i in item:
            listItem.append(str(binascii.hexlify(i)).upper())
        return listItem
    if typename == 'PT_OBJECT':
        return None
    if typename == 'PT_BINARY':
        return str(binascii.hexlify(item)).upper()
    if typename == 'PT_UNICODE':
        try:
            return item.encode('utf-8')
        except:
            return item
    else:
        return item


def getprop(item, myprop):
    try:
        return item.prop(myprop).value
    except:
        return None

def checktype(type):

    if type == 'PT_I4' or type == 'PT_LONG':
        type = 3
    if type == 'PT_BINARY':
        type = 258
    if type == 'PT_BOOLEAN':
        type = 11
    if type == 'PT_TSTRING' or type == 'PT_STRING8':
        type = 30
    if type == 'PT_UNICODE':
        type = 31
    if type == 'PT_SYSTIME' :
        type = 64

    return type

def checkTags(proptag=None, propname=None, value=None):

    with open('%s/static/Tags' % startdir, 'rb') as handle:
        tags = pickle.load(handle)
    type = None
    for tag in tags:
        if propname == tag['PR']:
            proptag = tag['HEX']
            type= tag['PT']
            propname = tag['PR']

    name = PROP_TAG(checktype(type), int(proptag, 16))
    if type:
        if type == 'PT_I4' or type == 'PT_LONG':
            try:
                value = int(value)
            except ValueError as e:
                value = 0
        if type == 'PT_BINARY':
            value = binascii.hexlify(value)
        if type == 'PT_BOOLEAN':
            if value.lower() == 'true':
                value = True
            else:
                value = False

    return value, name

def change(prop, value,special=None):
    if special:
        prop.set_value(value)
    elif prop.typename == u'PT_SYSTIME':
        print value
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        prop.set_value(value)
    elif prop.typename == u'PT_BINARY':
        try:
            prop.set_value(binascii.unhexlify(value))
        except Exception as e:
            print repr(e)
    elif prop.typename == u'PT_I4':
        prop.set_value(int(value))
    else:
        prop.set_value(value)

    return None



# stuff for rendering page
def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_page_items():
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = current_app.config.get('PER_PAGE', 100)
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    return page, per_page, offset


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )
