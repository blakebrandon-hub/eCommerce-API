from flask import Flask, request, jsonify, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import stripe
from functools import wraps
from os import environ
import uuid
import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE')
app.config['STRIPE_PUBLIC_KEY'] = environ.get('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = environ.get('STRIPE_SECRET_KEY')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = SQLAlchemy(app)

stripe.api_key = app.config['STRIPE_SECRET_KEY']


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String)
	username = db.Column(db.String)
	email = db.Column(db.String(80))
	password = db.Column(db.String)
	admin = db.Column(db.Boolean)


class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.String)
	user_id = db.Column(db.String)


def token_required(func):
	@wraps(func)
	def decorated(*args, **kwargs):
		token = None

		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({"message": "token is missing"}), 401

		try:
			decoded = jwt.decode(token, environ.get('SECRET_KEY'))
			current_user = User.query.filter_by(username=decoded['name']).first()
		except:
			return jsonify({'message': 'token is invalid'})

		return func(current_user, *args, **kwargs)

	return decorated

@app.route('/users')
@token_required
def get_users(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	users = User.query.all()

	output = []

	for user in users:
		user_data = {}
		user_data['username'] = user.username
		user_data['email'] = user.email
		user_data['admin'] = user.admin
		user_data['public_id'] = user.public_id
		user_data['password'] = user.password
		output.append(user_data)

	return jsonify({"users": output})

@app.route('/user/<name>')
@token_required
def get_one_user(current_user, name):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	user =  User.query.filter_by(username=name).first()

	user_data = {}
	user_data['username'] = user.username
	user_data['email'] = user.email
	user_data['admin'] = user.admin
	user_data['public_id'] = user.public_id
	user_data['password'] = user.password

	return jsonify({name: user_data})

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	data = request.get_json()

	hashed_password = generate_password_hash(data['password'], method='sha256')

	new_user = User(public_id=str(uuid.uuid4()), username=data['name'], password=hashed_password, 
			email=data['email'], admin=data['admin'])

	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message': 'user created'})

@app.route('/user/<name>', methods=['PUT'])
@token_required
def promote_user(current_user, name):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	user = User.query.filter_by(username=name).first()
	user.admin = True

	db.session.commit()

	return jsonify({'message': 'user has been promoted'})

@app.route('/user/<name>', methods=['DELETE'])
@token_required
def delete_user(current_user, name):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	user = User.query.filter_by(username=name).first()

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message': 'user has been deleted'})

@app.route('/login')
def login():
	auth = request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify authentication', 401, {'WWW-Authenticate': "Basic Realm='login required'"})

	user = User.query.filter_by(username=auth.username).first()

	if not user:
		return make_response('Could not verify user', 401, {'WWW-Authenticate': "Basic Realm='login required'"})

	if check_password_hash(user.password, auth.password):
		token = jwt.encode({"name": user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 
			environ.get('SECRET_KEY'))

		return jsonify({"token": token.decode('UTF-8')})

	return make_response('Could not verify', 401, {'WWW-Authenticate': "Basic Realm='login required'"})

@app.route('/product', methods=['POST'])
@token_required
def create_product(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	data = request.get_json()

	if 'description' not in data.keys():
		data['description'] = ''

	if 'images' not in data.keys():
		data['images'] = []

	if 'metadata' not in data.keys():
		data['metadata'] = {}

	if 'active' not in data.keys():
		data['active'] = True

	try:
		stripe.Product.create(name=data['name'], description=data['description'], 
				images=data['images'], active=data['active'], metadata=data['metadata'])

		return jsonify({"message": "product created"})

	except Exception as e:
			return str(e)

@app.route('/product/<product_id>')
@token_required
def get_one_product(current_user, product_id):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	return stripe.Product.retrieve(product_id)

@app.route('/product/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	data = request.get_json()

	if 'name' in data.keys():
		stripe.Product.modify(product_id, name=data['name'])

	if 'description' in data.keys():
		stripe.Product.modify(product_id, description=data['description'])

	if 'images' in data.keys():
		stripe.Product.modify(product_id, images=data['images'])

	if 'active' in data.keys():
		stripe.Product.modify(product_id, active=data['active'])

	if 'metadata' in data.keys():
		stripe.Product.modify(product_id, metadata=data['metadata'])

	return jsonify({"message": "product updated"})

@app.route('/product/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	try:
		stripe.Product.delete(product_id)
		return jsonify({"message": "product deleted"})

	except Exception as e:
		return str(e)

@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	try:
		products = stripe.Product.list()

		return jsonify({"products": products})

	except Exception as e:
		return str(e)

@app.route('/price', methods=['POST'])
@token_required
def create_price(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	data = request.get_json()

	try:
		stripe.Price.create(unit_amount=data['unit_amount'], currency=data['currency'], 
				product=data['product'])

		return jsonify({"message": "price created"})

	except Exception as e:
		return str(e)

@app.route('/price/<price_id>')
@token_required
def get_one_price(current_user, price_id):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	try:
		stripe.Price.retrieve(price_id)

	except Exception as e:
		return str(e) 

@app.route('/price/<price_id>', methods=['PUT'])
@token_required
def update_price(current_user, price_id):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	data = request.get_json()

	if 'active' in data.keys():
		stripe.Price.modify(price_id, active=data['active'])

	if 'nickname' in data.keys():
		stripe.Price.modify(price_id, nickname=data['nickname'])

	if 'metadata' in data.keys():
		stripe.Price.modify(price_id, metadata=data['metadata'])			

	return jsonify({"message": "price updated"})

@app.route('/prices', methods=['GET'])
@token_required
def get_prices(current_user):

	if not current_user.admin:
		return jsonify({"message": "cannot perform that function"})

	try:
		prices = stripe.Price.list()

		return jsonify({"prices": prices})

	except Exception as e:
		return str(e)

@app.route('/cart', methods=['GET'])
@token_required
def get_cart_items(current_user):

	cart_item = Product.query.filter_by(user_id=current_user.username).all()

	output = []

	for i in cart_item:
		d = {}
		d['product_id'] = i.product_id
		output.append(d)

	return jsonify({"cart": output})

@app.route('/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):

	data = request.get_json()

	new_item = Product(product_id=data['product_id'], user_id=current_user.username)

	db.session.add(new_item)
	db.session.commit()

	return jsonify({"message": "product added to cart"})

@app.route('/cart', methods=['DELETE'])
@token_required
def delete_from_cart(current_user):
	
	data = request.get_json()

	item = Product.query.filter_by(user_id=current_user.username, product_id=data['product_id']).first()

	db.session.delete(item)
	db.session.commit()

	return jsonify({"message": "product deleted from cart"})

@app.route('/checkout/<token>', methods=['GET', 'POST'])
def checkout(token):

	try:
		decoded = jwt.decode(token, environ.get('SECRET_KEY'))

		current_user = User.query.filter_by(username=decoded['name']).first()
		
		products = Product.query.filter_by(user_id=current_user.username).all()

		line_items = []

		for product in products:
			li_dict = {}
			li_dict['price'] = product.product_id
			li_dict['quantity'] = 1
			line_items.append(li_dict)

		try:
			checkout_session = stripe.checkout.Session.create(
				line_items = line_items,
				mode='payment',
			       success_url='https://ecomm-api-demo.herokuapp.com/success',
			       cancel_url='https://ecomm-api-demo.herokuapp.com/cancel',
			)

		except Exception as e:
			return str(e)

		return redirect(checkout_session.url, code=303)

	except:
		return jsonify({'message': 'token is invalid'})

@app.route('/success')
def success():
	return jsonify({"message": "payment successful"})

@app.route('/cancel')
def cancel():
	return jsonify({"message": "payment cancelled"})

@app.route('/account')
@token_required
def get_account_info(current_user):

	acc_dict = {}
	acc_dict['username'] = current_user.username
	acc_dict['email'] = current_user.email

	return jsonify({"account": acc_dict})
	
@app.route('/view/<product_id>')
@token_required
def view_one_product(current_user, product_id):

	return stripe.Product.retrieve(product_id)

@app.route('/view')
@token_required
def view_all_products(current_user, limit):
	
	products = stripe.Product.list(limit=limit)

	return jsonify({"products": products})

@app.route('/q')
@token_required
def query_products(current_user):

	query = request.args['search']

	products = stripe.Product.list()

	output = []

	for product in products:
		prod_dict = {}
		prod_dict['name'] = product.name
		prod_dict['product_id'] = product.id
		output.append(prod_dict)

	return jsonify({"products": output})

	
if __name__ == '__main__':
	app.run(debug=True)
