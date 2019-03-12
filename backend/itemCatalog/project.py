from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# CLIENT_ID = json.loads(
#    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=false')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Render login template
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user id not match given user id"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's Client id does not match our app's"), 401)
        print "Token's Client id does not match our app's"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already connected
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'User is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    login_session['provider'] = 'google'

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/githubconnect')
def githubconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.args.get('code')
    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('github_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('github_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://github.com/login/oauth/access_token'
    payload = {
        'client_id': app_id,
        'client_secret': app_secret,
        'code': request.args.get('code')
    }
    headers = {'Accept': 'application/json'}
    r = requests.post(url, params=payload, headers=headers)

    response = r.json()
    # get access_token from response and store in session
    if 'access_token' not in response:
        response = make_response(json.dumps(
            'Github did not return an access token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = response['access_token']
    # get username from github api
    url = 'https://api.github.com/user?access_token=%s' % login_session['access_token']
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    # finish setting up login_session
    login_session['provider'] = 'github'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['client_id'] = app_id
    login_session['picture'] = data["avatar_url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
        
    # set user_id in login session
    
    # welcome user and redirect
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return redirect(url_for('showCategories'))


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'github':
            githubdisconnect()
            del login_session['client_id']

        # Finish cleaning out the login_session
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been successfully logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/githubdisconnect')
def githubdisconnect():
    client_id = login_session['client_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://api.github.com/applications/%s/tokens/%s' % (
        client_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect - Revoke a user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP Get Request to revoke current token
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(CatalogItem).all()
    return jsonify(categories=[c.serialize for c in categories], items=[i.serialize for i in items])
    
@app.route('/catalog/items/JSON')
def catalog_items_json():
    items = session.query(CatalogItem).all()
    print items
    return jsonify(items=[i.serialize for i in items])


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('public_categories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Show a category's items
@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(category_id=category_id).all()
    creator = getUserInfo(category.user_id)
    if 'username' in login_session and getUserID(login_session['email']) == category.user_id:
        return render_template('items.html', items=items, category=category,
                               creator=creator)
    else:
        return render_template('public_items.html', items=items,
                               category=category, creator=creator)


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('edit_category.html', category=editedCategory)


# Delete a Category
@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('delete_category.html', category=categoryToDelete)


# Add a new item to the catalog under the passed in category
@app.route('/catalog/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newCatalogItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()

    creator = getUserInfo(category.user_id)
    if getUserID(login_session['email']) != category.user_id:
        return redirect(url_for('showItems', category_id=category_id))

    if request.method == 'POST':
        newItem = CatalogItem(
            name=request.form['name'], description=request.form['description'], category_id=category_id)
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('new_catalog_item.html', category_id=category_id)


# Edit an item in the catalog
@app.route('/catalog/<int:category_id>/items/<int:items_id>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(category_id, items_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=items_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    if getUserID(login_session['email']) != category.user_id:
        return redirect(url_for('showItems', category_id=category_id))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('edit_catalog_item.html', category_id=category_id, items_id=items_id, item=editedItem)


# Delete a item in the catalog
@app.route('/catalog/<int:category_id>/items/<int:items_id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(category_id, items_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(CatalogItem).filter_by(id=items_id).one()
    creator = getUserInfo(category.user_id)
    if getUserID(login_session['email']) != category.user_id:
        return redirect(url_for('showItems', category_id=category_id))

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('delete_catalog_item.html', item=itemToDelete, category_id=category_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
