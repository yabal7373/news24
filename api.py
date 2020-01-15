from flask import Flask, jsonify, request


app = Flask(__name__)

stores = [
    {
        'name':'Codemart',
        'items': [
            {
                'name': 'shoe',
                'price': '5,555',
                'brand': 'caterpillar'
            }
        ]
    }
]


# POST /store data
@app.route('/stores', methods=['POST'])
def create_store():
    request_data = request.get_json()
    new_store = {
        "name": request_data["name"],
        "items": []
    }
    stores.append(new_store)
    return jsonify(new_store)

# GET /store/<string:name>
@app.route('/store/<string:name>', methods=['GET'])
def get_store(name):
    # iterate over the store
    for store in stores:
        if store['name'] == name:
            return jsonify(store)
    return jsonify({"message":"store not found"})

# GET /store
@app.route('/stores', methods=['GET'])
def get_stores():
    return jsonify({'stores': stores})


# GET /store/<string:name>/item {name:, price:, brand:}
@app.route('/stores/<string:name>/items', methods=['POST'])
def create_item_in_store(name):
    request_data = request.get_json()
    for store in stores:
        if store['name'] == name:
            new_item = {
                'name': request_data['name'],
                'price': request_data['price'],
                'brand': request_data['brand']
            }
            store['items'].append(new_item)
            return jsonify(new_item)
    return jsonify({"message":"store not found"})

# GET /store/<string:name>/item
@app.route('/stores/<string:name>/items', methods=['GET'])
def get_items_in_store(name):
    for store in stores:
        if store['name'] == name:
            return jsonify({'items': store['items']})
        # returning error message if item not found
    return jsonify({'message': 'item not found'})


# to get items by brand
# GET /store/<string:name>/item/<string:brand>
@app.route('/store/<string:name>/items/<string:brand>', methods=['GET'])
def get_items_by_brand_in_store(name, brand):
    for store in stores:
        search =[]
        if store['name'] == name:
            for items in store['items']:
                # print(items)
                if items['brand'] == brand:
                    search.append(items)
            if len(search) >= 1:
                return jsonify({'items': search})
            return jsonify({'message': 'item not found'})
    return jsonify({'message': 'store not found'})




if __name__ == '__main__':
    app.run(debug=True)



