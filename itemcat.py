from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setupi import Base, Category, Item, User

import random, string, requests, json, httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcat.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

cats = session.query(Category).order_by(Category.id)

# Extract client secrets obj from 'g_client_secrets.json'
# and 'f_client_secrets.json'
G_CLIENT = json.loads(
    open('g_client_secrets.json', 'r').read())['web']
F_CLIENT = json.loads(
    open('f_client_secrets.json', 'r').read())['web']

##login_session.clear()

# Helper functions
def resPaj(text, num):
    response = make_response(json.dumps(text), num)
    response.headers['Content-Type'] = 'application/json'
    return response


# Login page with state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
	                for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Google login
@app.route('/gcon', methods=['POST'])
def gcon():
    if request.args.get('state') != login_session['state']:
       return resPaj('Invalid state token. Is there someone in the middle?',401)

    try:
        # get a credentials obj
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
##        print "get through!"
    except:
        return resRaj('Failed to generate credentials',401)

    # Check with google api
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    api_id_token = json.loads(h.request(url, 'GET')[1])
    print 'Maybe this is the id_token: %s' % api_id_token

    if api_id_token.get('error') is not None:
        return resRaj(api_id_token['error'], 500)
    gID = credentials.id_token['sub']
    print 'This is from flow: %s' % gID
    print 'This is from api: %s' % api_id_token.get('sub')

##    output = ''
##    output += '<h1>Welcome, '
##    output += login_session['username']
##    output += '!</h1>'
##    output += '<img src="'
##    output += login_session['picture']
##    output += ' " style = "width: 160px; height: 160px;'
##    output += 'border-radius: 80px; -webkit-border-radius: 80px;'
##    output += '-moz-border-radius: 80px;"> '
##    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return "<h1> WTF </h1>"

       
# Home page
@app.route('/')
@app.route('/home/')
def home():
    items = session.query(Item, Category).join(Category).\
           order_by(desc(Item.id)).all()
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
    return render_template('item.html', item=item, cat_name=cat_name)

# Add an item
@app.route('/catitems/add/', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=1)
        session.add(newItem)
        session.commit()
        flash('%s has been added!!' % newItem.name)
        return render_template('addItem.html', cats=cats)
    else:
        return render_template('addItem.html', cats=cats)

# Edit an item
@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>/edit', methods=['GET','POST'])
def edit(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    old_name = item.name
    print item.user_id
    if request.method == 'POST':
        item.name=request.form['name']
        item.description=request.form['description']
        item.category_id=request.form['category_id']
        session.commit()
        new_name = item.name
        flash('{} has been edited to {}!!'.format(old_name, new_name))
        return render_template('editItem.html', cats=cats, item=item)
    else:
        return render_template('editItem.html', cats=cats, item=item)

# Delete an item
@app.route('/catitems/<cat_name>/<item_name>/<int:item_id>/delete', methods=['GET','POST'])
def delete(cat_name, item_name, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    name = item.name
    cat_id = item.category_id
    cat = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('%s has been deleted!!' % name)
        return redirect(url_for('cat', cat_name=cat.name, cat_id=cat_id))

    else:
        return render_template('deleteItem.html', cat=cat, item=item)

# JSON APIs
# all categories
@app.route('/catitems/JSON')
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
