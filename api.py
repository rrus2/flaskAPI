from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bson, bcrypt

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'shop'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/shop'
mongo = PyMongo(app)

# PRODUCT API
@app.route('/products', methods=['GET'])
def products():
    collection = mongo.db.product.find()

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
    image = r['image']

    result = mongo.db.product.insert_one({'name': name, 'image': image, 'price': price})
    if result.acknowledged:
        output = mongo.db.product.find_one({'name': name})
        json = {'id' : str(output['_id']), 'name': output['name'], 'price': output['price'], 'image': output['image']}

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
    password = bcrypt.hashpw(r['password'].encode('utf-8'), bcrypt.gensalt())

    result = mongo.db.users.insert_one({'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'password': password})
    if result.acknowledged:
        output = mongo.db.users.find_one({'username': username})
        json = {'_id': str(output['_id']), 'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'password': password}
        return jsonify(json)

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


if __name__ == '__main__':
    app.run(debug=True)