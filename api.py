from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bson, bcrypt
from flask_cors import cross_origin, CORS
import json

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'shop'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/shop'
mongo = PyMongo(app)
CORS(app)

# PRODUCT API
@app.route('/products', methods=['GET'])
def products():
    collection = list(mongo.db.product.find())
    r = request.get_json('_id')
    name = None
    min_price = None
    max_price = None
    category = None
    if r:
        if 'name' in r:
            name = r['name']
        if 'min_price' in r:
            min_price = r['min_price']
        if 'max_price' in r:
            max_price = r['max_price']
        if 'category' in r:
            category = r['category']

    if name:
        collection = [x for x in collection if name in x.get('name')]

    if min_price:
        collection = [x for x in collection if min_price <= int(x.get('price'))]

    if max_price:
        collection = [x for x in collection if max_price >= int(x.get('price'))]
    
    if category:
        collection = [x for x in collection if category in x.get('category')]
    
    products = []

    for product in collection:
        products.append({'id': str(product['_id']), 'name': product['name'], 'price': product['price'], 'image': product['image']})

    return jsonify(products)

@app.route('/products/<id>', methods = ['GET'])
def product(id):
    item = mongo.db.product.find_one({'_id': bson.ObjectId(oid=str(id))})
    product = {'id': str(item['_id']),'name': item['name'], 'price': item['price'], 'image': item['image']}
    return jsonify(product)
    
@app.route('/products', methods = ['POST'])
def productpost():
    r = request.get_json('name')
    name = r['name']
    price = r['price']
    category = r['category']
    image = r['image']

    result = mongo.db.product.insert_one({'name': name, 'image': image, 'price': price, 'category': category})
    if result.acknowledged:
        output = mongo.db.product.find_one({'name': name})
        json = {'id' : str(output['_id']), 'name': output['name'], 'price': output['price'], 'image': output['image'], 'category': output['category']}

        return jsonify(json)

@app.route('/products/<id>', methods=['PUT'])
def productput(id):
    item = mongo.db.product.find_one({'_id': bson.ObjectId(oid=str(id))})
    r = request.get_json('_id')
    name = r['name']
    price = r['price']
    image = r['image']
    updated_item = {'$set': {'name': name, 'price': price, 'image': image}}
    mongo.db.product.update_one(item, updated_item)
    
    return jsonify(updated_item)

@app.route('/products/<string:name>', methods=['DELETE'])
def productdelete(name):
    item = mongo.db.product.find_one({'name': name})
    print(item)
    if item is not None:
        mongo.db.product.delete_one(item)

# USER API
@app.route('/users', methods=['GET'])
def users():
    collection = mongo.db.users.find()

    users = []

    for i in collection:
        users.append({'_id': str(i['_id']), 'firstname': i['firstname'], 'lastname': i['lastname'], 'username': i['username'], 'birthdate': i['birthdate'], 'email': i['email']})

    return jsonify(users)

@app.route('/users/<id>', methods=['GET'])
def user(id):
    item = mongo.db.users.find_one({'_id': bson.ObjectId(oid=id)})
    user = {'_id': str(item['_id']), 'firstname': item['firstname'], 'lastname': item['lastname'], 'username': item['username'], 'birthdate': item['birthdate'], 'email': item['email']}
    return jsonify(user)

@app.route('/users', methods=['POST'])
def userpost():
    r = request.get_json('_id')
    firstname = r['firstname']
    lastname = r['lastname']
    username = r['username']
    birthdate = r['birthdate']
    email = r['email']
    role = 'user'
    password1 = r['password']
    password2 = r['repeatpassword']
    check_username = mongo.db.users.find({'username': username})
    print(check_username)
    if password1 == password2 and firstname != "" and lastname != "" and username != "" and check_username.count() < 1:
        password = bcrypt.hashpw(r['password'].encode('utf-8'), bcrypt.gensalt())
        result = mongo.db.users.insert_one({'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'role': role, 'password': password})
        if result.acknowledged:
            #output = mongo.db.users.find_one({'username': username})
            #json = {'_id': output['_id'], 'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'role': role, 'password': password}
            return "user successfully added", 200
        else:
            return "fail inserting user", 404
    else:
        return "user already exists", 404

@app.route('/users/<id>', methods=['PUT'])
def userput(id):
    item = mongo.db.users.find_one({'_id': bson.ObjectId(oid=id)})
    r = request.get_json('_id')
    firstname = r['firstname']
    lastname = r['lastname']
    username = r['username']
    birthdate = r['birthdate']
    email = r['email']
    password = bcrypt.hashpw(r['password'].encode('utf-8'), bcrypt.gensalt())
    updated_item = {'$set': {'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'password': password}}

    mongo.db.users.update_one(item, updated_item)

    return jsonify(updated_item)

@app.route('/users/<id>', methods=['DELETE'])
def userdelete(id):
    item = mongo.db.users.find_one({'_id': bson.ObjectId(oid=id)})
    if item is not None:
        mongo.db.users.delete_one(item)

@app.route('/login', methods=['POST'])
def login():
    r = request.get_json('username')
    username = r['username']
    password = r['password']

    user = mongo.db.users.find_one({'username': username})
    if user is not None:
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            userobj = {
                '_id': str(user['_id']),
                'firstname': user['firstname'],
                'lastname': user['lastname'],
                'username': user['username'],
                'birthdate': user['birthdate'],
                'email': user['email'],
                'role': user['role'],
            }
            return jsonify(userobj)

    return "User/Password did not match", 301


# ORDERS API
@app.route('/orders', methods=['GET'])
def orders():
    collection = mongo.db.orders.find()

    orders = []

    for i in collection:
        orders.append({'_id': bson.ObjectId(oid=i['_id']), 'ProductID': i['ProductID'], 'UserID': i['UserID']})

    return jsonify(orders)

@app.route('/orders/<id>', methods=['GET'])
def order(id):
    item = mongo.db.orders.find_one({'_id': bson.ObjectId(oid=id)})
    order = {'_id': item['_id'], 'ProductID': item['ProductID'], 'UserID': item['UserID']}
    return jsonify(order)

@app.route('/orders', methods=['POST'])
def orderpost():
    r = request.get_json('_id')
    productid = r['ProductID']
    userid = r['UserID']

    result = mongo.db.orders.insert_one({'ProductID': productid, 'UserID': userid})
    if result.acknowledged and productid != None and userid != None:
        item = mongo.db.orders.find_one({'_id': bson.ObjectId(oid=r['_id'])})
        return jsonify(item)

@app.route('/users/<id>', methods=['PUT'])
def ordersput(id):
    item = mongo.db.orders.find_one({'_id': bson.ObjectId(oid=id)})
    r = request.get_json('_id')
    productid = r['ProductID']
    userid = r['UserID']
    updated_item = {'$set': {'ProductID': productid, 'UserID': userid}}
    mongo.db.orders.update_one(item, updated_item)

    return jsonify(updated_item)

@app.route('/users/<id>', methods=['DELETE'])
def ordersdelete(id):
    item = mongo.db.orders.find_one({'_id': bson.ObjectId(oid=id)})
    mongo.db.orders.delete_one(item)

if __name__ == '__main__':
    app.run(debug=True)