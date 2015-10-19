#!/usr/bin/env python
from zarapy import app
from option import *
startdir = os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def index():
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    session['foldername'] = None
    session['subject'] = None
    users = []
    total = 0
    if options.auth_user and options.auth_pass:
        lusers= []
        lusers.append(zarafa.Server(options).user(options.auth_user))
    else:
        lusers = zarafa.Server(options).users(parse=True, remote=True)
    for user in lusers:
        if user.store:
            users.append([user.name, user.company.name, user.userid, user.home_server])
            total += 1
        else:
            users.append([user.name, user.company.name, 'User has no store', user.home_server])


    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='users',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('index.html', users=users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/listusers', methods=['GET', 'POST'])
def listusers():
    options, args = opt_args()
    props = []
    total = 0
    if request.method == 'POST':
        postUser = request.form['user']
    else:
        postUser = session['user']
    for prop in zarafa.Server(options).user(postUser).props():
        props.append([prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])
        total += 1

    return render_template('index.html', listusers=props,
                           userid=postUser,
                           )


@app.route('/createStore', methods=['GET', 'POST'])
def createStore():
    # options, args = opt_args()
    user = request.form['user']
    # Dirty way
    os.system("zarafa-admin  --create-store '%s' " % user)
    # xxx  wait for the python-zarafa way is fixed

    return redirect(url_for('index'))

@app.route('/folders', methods=['GET', 'POST'], )
def folders():
    options, args = opt_args()
    menu = []
    session.clear()
    if request.method == 'POST':
        user = request.form['user']
    if request.method == 'GET':
        user = request.args.get('user')
    for folder in zarafa.Server(options).user(user).folders():
        menu.append([folder.name, folder.entryid])
    session['menu'] = menu
    session['user'] = user

    return redirect(url_for('propsStore'))


@app.route('/propsfolder', methods=['GET', 'POST'])
def propsfolder():
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    props = []
    total = 0
    user = session['user']
    if request.method == 'GET':
        folder = request.args.get('folder')
    else:
        folder = session['folder']
    for prop in zarafa.Server(options).user(user).folder(folder).props():
        props.append([prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])
        total += 1
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='props',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('folder.html', propsfolder=props,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/propsStore')
def propsStore():
    options, args = opt_args()
    props = []
    user = session['user']
    user = zarafa.Server(options).user(user)
    for prop in user.store.root.props():
        props.append(
            [prop.id_, prop.idname, hex(prop.proptag).upper(), prop.typename, printprop(prop.typename, prop.value)])

    return render_template('store.html', propsStore=props,
                           user=user.name,
                           )


@app.route('/items', methods=['GET', 'POST'])
def items(user=None, folder=None):
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    items = []
    session['subject'] = None

    user = session['user']
    if request.method == 'POST':
        folder = request.form['folder']
        folder = zarafa.Server(options).user(user).folder(folder)
        total = folder.count
        session['total'] = total
        session['foldername'] = folder.name
        session['folder'] = folder.entryid
        listitems = []
        for item in folder.items():
            listitems.append(item.entryid)
        pickle.dump(listitems, open('%s/tmp/listitems' % startdir, "wb"))
    else:
        listitems = pickle.load(open('%s/tmp/listitems' % startdir, 'rb'))
        total = session['total']

    itemsstart = per_page * (page - 1)
    itemsend = per_page * page
    user = zarafa.Server(options).user(user)
    for itemid in listitems[itemsstart:itemsend]:
        item = user.item(itemid)
        if item.subject == '':
            subject = '<No subject>'
        else:
            subject = item.subject
            items.append([subject, item.entryid])

    if total == 0:
        items.append(['No Items in %s' % folder.name, '0000'])

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='items',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('items.php', items=items,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/propsitem', methods=['GET', 'POST'])
def propsitem():
    options, args = opt_args()
    user = session['user']
    props = []
    if request.method == 'POST':
        item = request.form['item']
        session['item'] = item
    else:
        item = session['item']
    item = zarafa.Server(options).user(user).item(item)
    session['subject'] = item.subject
    for prop in item.props():
        if hex(prop.proptag) == "0x10130102L":
            props.append([prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value), prop.value])
        else:
            props.append([prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])

    with open('%s/static/Tags' % startdir, 'rb') as handle:
        tags = pickle.load(handle)

    return render_template('items.php', propsitem=props, tags=tags)


@app.route('/showItem')
def showItem():
    options, args = opt_args()
    user = session['user']
    item = session['item']
    item = zarafa.Server(options).user(user).item(item)
    attachment = []
    for at in item.attachments():
        attachment.append([at.filename, binascii.hexlify(at.data)])

    iteminfo = (
        getprop(item, 0x42001fL), getprop(item, 0xe04001fL), getprop(item, 0xe03001fL), getprop(item, 0xe02001fL),
        getprop(item, 0x37001fL), getprop(item, 0x10130102L), getprop(item, 0x1000001fL))

    return render_template('items.php', showmail=iteminfo,
                           attachments=attachment
                           )


@app.route('/download', methods=['POST'])
def download():
    response = make_response(binascii.unhexlify(request.form['dowData']))
    response.headers["Content-Disposition"] = "attachment; filename=%s" % request.form['dowName']
    return response


@app.route('/deleteItem')
def deleteItem():
    options, args = opt_args()
    user = session['user']
    folder = session['folder']
    item = session['item']
    folder = zarafa.Server(options).user(user).folder(folder)
    item = folder.item(item)
    folder.delete(item)
    return redirect(url_for('items'))


@app.route('/eml')
def eml():
    options, args = opt_args()
    user = session['user']
    folder = session['folder']
    item = session['item']
    item = zarafa.Server(options).user(user).folder(folder).item(item)
    response = make_response(item.eml())
    response.headers["Content-Disposition"] = "attachment; filename=%s.eml" % item.subject

    return response


@app.route('/uploademl', methods=['POST'])
def uploademl():
    options, args = opt_args()
    user = session['user']
    folder = session['folder']
    uploadfile = request.files['fileToUpload']
    try:
        itemprop = request.form['itemprop']
    except:
        itemprop = False
    if str(uploadfile.filename).endswith('.eml'):
        item = zarafa.Server(options).user(user).folder(folder).create_item(eml=uploadfile.read())
        if itemprop == "True":
            props = []
            for prop in zarafa.Server(options).user(user).item(item.entryid).props():
                props.append(
                    [prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])
            return render_template('items.php', propsitem=props,
                                   item=item.entryid
                                   )
        elif request.form['item']:

            return redirect(url_for('items'))

        else:
            return redirect(url_for('folders'))
    else:
         return redirect(url_for('items'))


@app.route('/diffItem', methods=['POST'])
def diffItem():
    options, args = opt_args()
    folder = zarafa.Server(options).user(request.form['user']).folder(request.form['folder'])
    items = request.form.getlist('dfItems[]')
    props = []
    for itemID in items:
        for prop in folder.item(itemID).props():
            props.append([itemID, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])

    return render_template('diff.html', props=props)


@app.route('/searchitem', methods=['POST'])
def searchitem():
    user = session['user']
    search = request.form['search']
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    items = []
    total = 0
    user = zarafa.Server(options).user(user)
    try:
        item = user.store.item(search)
        items.append([item.subject, item.entryid])

    except:
        for folder in user.folders():

            for item in folder.items():
                if search in item.subject or search in item.entryid or search in printprop('PT_BINARY',
                                                                                           getprop(item, 0x65e00102L)):
                    items.append([item.subject, item.entryid])
                    total += 1

    if total == 1:
        props = []
        for prop in item.props():
            props.append(
                [prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])
        return render_template('items.php', propsitem=props,
                               item=item,
                               )
    else:
        pagination = get_pagination(page=page,
                                    per_page=per_page,
                                    total=total,
                                    record_name='items',
                                    format_total=True,
                                    format_number=True,
                                    )
        return render_template('items.php', items=items,
                               page=page,
                               per_page=per_page,
                               pagination=pagination,
                               )


@app.route('/changeitem', methods=['POST'])
def changeitem():
    options, args = opt_args()
    proptag = request.form['proptag']
    user = session['user']
    item = session['item']
    value = request.form['value']
    user = zarafa.Server(options).user(user)
    item = user.item(item)
    for prop in item.props():
        if hex(prop.proptag).upper() == proptag.upper():
            oldvalue = prop.value
            if oldvalue != value:
                if proptag == '0x10130102L':
                    change(prop, value, special=True)
                else:
                    change(prop, value)

    return redirect(url_for('propsitem'))


@app.route('/changestore', methods=['POST'])
def changestore():
    options, args = opt_args()
    username = request.form['user']
    proptag = request.form['proptag']
    value = request.form['value']
    user = zarafa.Server(options).user(username)
    print proptag
    for prop in user.store.root.props():
        if hex(prop.proptag).upper() == proptag.upper():
            oldvalue = prop.value
            if oldvalue != value:
                change(prop, value)

    return redirect(url_for('propsStore', user=username))

@app.route('/addprop', methods=['POST'])
def addprop():
    options, args = opt_args()
    user = session['user']
    item = session['item']
    propname = request.form['propname']
    value = request.form['value']
    fixvalue , name = checkTags(propname=propname, value=value)
    item = zarafa.Server(options).user(user).store.item(item)
    item.mapiobj.SetProps([SPropValue(name, fixvalue)])
    item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

    return redirect(url_for('propsitem'))


@app.route('/removeprop', methods=['POST'])
def removeprop():
    options, args = opt_args()
    user = session['user']
    item = session['item']
    proptag = request.form['proptag']

    item = zarafa.Server(options).user(user).store.item(item)
    for prop in item.props():
        if hex(prop.proptag).upper() == proptag.upper():
            item.delete(item.prop(prop.proptag))
    return redirect(url_for('propsitem'))


@app.route('/softdelete', methods=['GET'])
def softdelete():
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    items = []
    session['subject'] = None
    user = session['user']
    if request.method == 'GET':
        folder = request.args.get('folder')
        folder = zarafa.Server(options).user(user).folder(folder)
        session['foldername'] = folder.name
        listitems = []
#get softdelete
        table= folder.mapiobj.GetContentsTable(SHOW_SOFT_DELETES)
        table.SetColumns([PR_SUBJECT, PR_ENTRYID], 0)
        rows = table.QueryRows(-1, 0)
        for item in rows:
            listitems.append([item[0].Value,item[1].Value])
        total = len(listitems)
        pickle.dump(listitems, open('%s/tmp/softdelete' % startdir, "wb"))
    else:
        listitems = pickle.load(open('%s/tmp/softdelete' % startdir, 'rb'))
        total = session['total']


    itemsstart = per_page * (page - 1)
    itemsend = per_page * page
    user = zarafa.Server(options).user(user)
    for itemid in listitems[itemsstart:itemsend]:
        items.append([itemid[0],binascii.hexlify(itemid[1])])
    if total == 0:
        items.append(['No Soft-Delete items in  %s' % folder.name, '0000'])

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='items',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('items.php', items=items,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )

# company stuff
@app.route('/company')
def company():
    options, args = opt_args()
    page, per_page, offset = get_page_items()
    companies = []
    total = 0
    for company in zarafa.Server(options).companies(remote=True, parse=True):
        companies.append([company.name, user.company.name, user.userid, user.home_server])
        total += 1
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='users',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('base.html', companies=companies,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,

                        )

