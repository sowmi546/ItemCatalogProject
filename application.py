
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, CatalogItem, User
from flask import session as login_session

# New imports for this step
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#in creating a new user
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)
#retrieve clientID
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "CatalogItem"

#connect to database to retrieve
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#main route
@app.route('/')
@app.route('/mainpage')
def MainPage():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' in login_session:
         return render_template('mainpage.html', categories=categories,username=login_session['username'])
    else:
        return render_template('publicmainpage.html', categories=categories)

#show catalogItems in a category
@app.route('/catalog/<category_name>/items')
@app.route('/catalog/<category_name>/')
def CategoryItems(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    # category = session.query(Category).filter_by(name=category_name).one()
    cat_items = session.query(CatalogItem).filter_by(category_name=category_name).all()

    return render_template('categorydetails.html',categoryname=category_name,items=cat_items,categories=categories)

#Catalog item details
@app.route('/catalog/<category_name>/<item_name>')
def CatalogItemDetails(category_name,item_name):
    cat_item = session.query(CatalogItem).filter_by(name=item_name).one()
    return render_template('itemdetails.html',itemname=item_name,description=cat_item.description,category_name=category_name)


#add new catalog item
@app.route('/catalog/additem', methods=['GET', 'POST'])
def NewCatalogItem():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = CatalogItem(name=request.form['name'], description=request.form['description'],category_name=request.form['category'],user_name=login_session['username'])
        category_name=request.form['category']
        categoryCheck = session.query(Category).filter_by(name=category_name).one()
        if categoryCheck.user_name != login_session['username']:
            return "<script>function myFunction() {alert('You are not authorized to Create this item. Please create your own catalog item in your own category.');}</script><body onload='myFunction()''>"
        session.add(newItem)
        session.commit()
        flash('New CatalogItem %s Item Successfully Created' % (newItem.name))
        # return redirect(url_for('MainPage', restaurant_id=restaurant_id))
        return "successfully added !!!!!!!!!!!"
    else:
        return render_template('newcatalogitem.html', categories=categories)
    # return "Hello adding new catalog item"

#edit catalog item
@app.route('/catalog/<category_name>/<item_name>/edit', methods=['GET', 'POST'])
def EditCatalogItem(category_name,item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    if editedItem.user_name != login_session['username']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own catalog item in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('MainPage'))
    else:
        return render_template('editcatalogitem.html',categories=categories)

#delete catalog item
@app.route('/catalog/<category_name>/<item_name>/delete', methods=['GET', 'POST'])
def DeleteCatalogItem(category_name,item_name):

    itemToDelete = session.query(CatalogItem).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_name != login_session['username']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('MainPage'))
    else:
        return render_template('deletecatalogitem.html', item=itemToDelete)

#creating a new user
@auth.verify_password
@app.route('/checklogin', methods=['POST'])
def isValidUser():
    print("Method type**" +request.method)
    if request.method == 'POST':
        print "before user name"
        username = request.form['uname']
        print "after user name"
        print("Username is" +username)
        password = request.form['psw']

        # user = User(username)
        # fromdbuser = session.query(User).filter_by(uname = username).first()
        user = session.query(User).filter_by(uname = username).first()
        # pass_hash = user.password
        # print (user.hash_password(password))
        # print "password" +user.password_hash
        # if not user or not user.verify_password(password):
        if not user:
            print(user.verify_password(password))
            return "Unable to verify password"
        else:
            login_session['username']=user.uname
            categories = session.query(Category).order_by(asc(Category.name))
            # return render_template('mainpage.html',categories=categories,username=login_session['username'])
            #return render_template('mainpage.html', categories=categories, username=login_session['username'])
            return redirect('/mainpage')

# @app.route('/user/create',methods=['GET','POST'])
# def CreateNewUser():
#     return render_template('createuser.html')

#creating new user in signup page
@app.route('/user/create', methods = ['GET','POST'])
def CreateNewUser():
    if request.method == 'POST':
        username = request.form['uname']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        password = json.dumps(password)

        if username is None or password is None:
            abort(400) # missing arguments
        user = User(uname = username,name=name,email=email)

    # if session.query(User).filter_by(username = username).first() is not None:
    #     abort(400) # existing user
        if user:

            user.hash_password(password)
            session.add(user)
            flash('New User %s Successfully Created' % user.name)
            session.commit()
            return render_template('login.html')
    else:
        return render_template('createuser.html')


@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

#Login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)
    # return "The current session state is %s" %login_session['state']

#gconnect login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("Hello" +request.args.get('state'))
    print("Hello2**" +login_session['state'])
#     #check if user exists in database
#     print "Hello***" + login_session['state']
# #ADDED CODE
#     # user_id = getUserID(login_session['email'])
#     # if not user_id:
#     #     user_id = createUser(login_session)
#     # login_session['user_id'] = user_id
# #END OF ADDED CODE
#     # if getUserInfo(login_session['user_id']):
#     #     return
#     # else:
#     #     createUser(login_session)
# #from here
#
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['access_token']=credentials.access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    #ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
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

    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    print "done*******!" + login_session['access_token']
    return output

#disconnect
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    # access_token = login_session['credentials']
    # print('Hello***' +credentials)
    access_token = login_session.get('credentials')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)
    print('Hello****' +result['status'])
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('MainPage'))
    else:
        flash("You were not logged in")
        del login_session['username']
        return redirect(url_for('MainPage'))


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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

#disconnect
@app.route('/disconnect')
def mydisconnect():
    if login_session['username']:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('MainPage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('MainPage'))

        
if __name__ == '__main__':
     app.secret_key = 'super_secret_key'
     app.debug = True
     app.run(host = '0.0.0.0', port=8000)
