#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setupi import Base, Category, Item, User

import random
import string
import requests
import json
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

app = Flask(__name__)

# Connect to Database and create database session

engine = create_engine('sqlite:///itemcat.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

cats = session.query(Category).order_by(Category.id)

# Helper functions


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


def resPaj(text, num):
    response = make_response(json.dumps(text), num)
    response.headers['Content-Type'] = 'application/json'
    return response


def getUserID(email):
    try:
        print email
        user = session.query(User).filter_by(email=email).one()
        print user
        return user.id
    except:
        return None


def createUser(l_s):
    print l_s
    newUser = User(name=l_s.get('username'), email=l_s.get('email'),
                   picture=l_s.get('picture'), gID=l_s.get('gID'),
                   fbID=l_s.get('fbID'))
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=l_s.get('email')).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Login page with state token

@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Disconnect

@app.route('/discon')
def discon():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdiscon()
        elif login_session['provider'] == 'facebook':
            fbdiscon()
        login_session.clear()
        flash('You have successfully logged out.')
        return redirect(url_for('home'))
    else:
        flash('U were not logged in.')
        return redirect(url_for('home'))


# Google login

@app.route('/gcon', methods=['POST'])
def gcon():
    if request.args.get('state') != login_session['state']:
        return resPaj('Invalid state token. Is there someone in the middle?',
                      401)

    try:

        # get a credentials obj

        oauth_flow = flow_from_clientsecrets('g_client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
    except:

        # print "get through!"

        return resPaj('Failed to generate credentials', 401)

    # Check with google api

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    api_id_token = json.loads(h.request(url, 'GET')[1])

    # print 'Maybe this is the id_token: %s' % api_id_token

    if api_id_token.get('error') is not None:
        return resRaj(api_id_token['error'], 500)
    gID = credentials.id_token['sub']

    # print 'This is from flow: %s' % gID
    # print 'This is from api: %s' % api_id_token.get('sub')

    if api_id_token['sub'] != gID:
        return resPaj("Token's ID doesn't match given user ID.", 401)

    # If all tests pass, extract 'credentials' and 'gID' from
    # current loging_session, these will be None if not logged in already

    stored_credentials = login_session.get('credentials')
    stored_gID = login_session.get('gID')
    if stored_credentials is not None and gID == stored_gID:
        return resPaj('You are logged in already!', 200)

    # get user info from api

    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    userinfo = requests.get(url, params=params).json()

    # print 'Userinfo is %s' % userinfo

    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['access_token'] = access_token
    login_session['gID'] = gID
    login_session['username'] = userinfo['name']
    login_session['picture'] = userinfo['picture']
    login_session['email'] = userinfo['email']
    print login_session

    # check if user exists in database, if not create a new one

    userID = getUserID(userinfo['email'])
    print userID
    if userID is None:
        userID = createUser(login_session)
    login_session['user_id'] = userID

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 160px; height: 160px;'
    output += 'border-radius: 80px; -webkit-border-radius: 80px;'
    output += '-moz-border-radius: 80px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


# Google disconnect

@app.route('/gdiscon')
def gdiscon():
    credentials = login_session.get('credentials')
    access_token = login_session.get('access_token')
    if credentials is None:
        print 'Credentials obj is None!'
        return resPaj('Current user is not connected', 401)

    # Execute HTTP GET request to revoke current token.

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print login_session
    login_session.clear()
    print login_session

    if result['status'] == '200':
        return resPaj('Successfully logged out!!!', 200)
    else:
        return resPaj('Failed to revoke token for given user.', 400)


# FB login

@app.route('/fbcon', methods=['POST'])
def fbcon():

    # check state

    if request.args.get('state') != login_session['state']:
        return resPaj('Invalid state code!', 401)

    # kick start the flow

    access_token = request.data
    client = json.loads(open('f_client_secrets.json', 'r').read())['web']
    client_id = client['client_id']
    client_secret = client['client_secret']
    url = 'https://graph.facebook.com/v2.9/oauth/'
    url += 'access_token?grant_type=fb_exchange_token&client_id='
    url += '%s&client_secret=%s&' % (client_id, client_secret)
    url += 'fb_exchange_token=%s' % (access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print result

    # strip the expire tag

    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    # get user info from api

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' \
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print 'new result:'
    print result

    data = json.loads(result)
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data.get('email')
    if login_session['email'] is None:
        login_session['email'] = 'facebook@facebook.com'
    login_session['fbID'] = data['id']

    # Get user picture

    url = 'https://graph.facebook.com/v2.2/me/picture?'
    url += '%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print 'result with pic:'
    print result
    data = json.loads(result)
    print data

    login_session['picture'] = data['data']['url']

    # check if user exists

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 160px; height: 160px;'
    output += 'border-radius: 80px; -webkit-border-radius: 80px;'
    output += '-moz-border-radius: 80px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


# FB disconnect

@app.route('/fbdiscon')
def fbdiscon():
    fbID = login_session['fbID']
    url = 'https://graph.facebook.com/%s/permissions' % fbID
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    login_session.clear()
    return 'you have been logged out!'


# Home page

@app.route('/')
@app.route('/home/')
def home():
    items = session.query(Item, Category).join(Category)\
            .order_by(desc(Item.id)).limit(10).all()
    if 'username' not in login_session:
        return render_template('pubindex.html', cats=cats, items=items)
    return render_template('index.html', cats=cats, items=items)


# Show items in a category

@app.route('/catitems/<cat_name>/<int:cat_id>/items/')
def cat(cat_name, cat_id):
    items = session.query(Item).filter_by(category_id=cat_id).all()
    length = len(items)
    cat = session.query(Category).filter_by(id=cat_id).one()
    return render_template('items.html', cats=cats, items=items,
                           length=length, name=cat.name)


# Show an item

@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>')
def item(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    print item
    print item.user_id
    print login_session
    if login_session.get('user_id') == item.user_id:
        return render_template('item.html', item=item,
                               cat_name=cat_name)
    return render_template('pubitem.html', item=item, cat_name=cat_name)


# Add an item

@app.route('/catitems/add/', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=login_session.get('user_id'))
        session.add(newItem)
        session.commit()
        flash('%s has been added!!' % newItem.name)
        return redirect(url_for('home'))
    else:
        return render_template('addItem.html', cats=cats)


# Edit an item

@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def edit(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session.get('user_id') != item.user_id:
        text = "<script>function myFunction() "
        text += "{alert('You are not authorized to edit this item.');}"
        text += "</script><body onload='myFunction()'>"
        return text
    old_name = item.name
    print item.user_id
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = request.form['category_id']
        session.commit()
        new_name = item.name
        flash('{} has been edited to {}!!'.format(old_name, new_name))
        return render_template('editItem.html', cats=cats, item=item)
    else:
        return render_template('editItem.html', cats=cats, item=item)


# Delete an item

@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def delete(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session.get('user_id') != item.user_id:
        text = "<script>function myFunction() "
        text += "{alert('You are not authorized to delete this item.');}"
        text += "</script><body onload='myFunction()'>"
        return text
    name = item.name
    cat_id = item.category_id
    cat = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('%s has been deleted!!' % name)
        return redirect(url_for('cat', cat_name=cat.name,
                        cat_id=cat_id))
    else:

        return render_template('deleteItem.html', cat=cat, item=item)


# JSON APIs
# all categories

@app.route('/home/JSON')
def catsJSON():
    return jsonify(Categories=[c.serialize for c in cats])


# cat info

@app.route('/catitems/<cat_name>/<int:cat_id>/items/JSON')
def catJSON(cat_name, cat_id):
    items = session.query(Item).filter_by(category_id=cat_id).all()
    return jsonify(Items=[i.serialize for i in items])


# item info

@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>/JSON')
def itemJSON(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key2'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
