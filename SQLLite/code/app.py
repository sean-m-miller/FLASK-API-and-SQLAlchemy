from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "Sean"
api = Api(app)

jwt = JWT(app, authenticate, identity) # calls authenticate and identity in security.py

items = [] # The "database"

class Item(Resource):
    parser = reqparse.RequestParser() #Item class parser
    parser.add_argument("price", #requests must be in format { "price": float}
        type = float,
        required = True,
        help="FORMAT ERROR: This request must have be string : float where string == price "
    )

    @jwt_required() # jwt authentification required
    def get(self, name): # get request, looking for item called "name",
        for item in items: #loop through our "database" (local dictionary)
            if name == item["name"]:
                return {"item": item}, 200 #status OK, item found
        return {"item" : None}, 404 #not found

    def post(self, name):
        for item in items:
            if name == item["name"]:
                return {"message": "an item with name " + name + " already exists."}, 400 #bad request
        data = Item.parser.parse_args() # what the user will send to the post request (in good format)
        # In our case, the user sends the price as JSON, but the item name gets passed into the function
        item = {"name": name, "price": data["price"]}
        items.append(item) # push to database
        return item, 201 #post was successful

    def delete(self, name):
        cnt = 0
        for item in items: #remove all items called "name"
            if name == item["name"]:
                items.remove(item)
                cnt+=1
        return {"message": str(cnt) + " Item(s) Deleted"}

    def put(self, name):
        data = Item.parser.parse_args() # only add valid JSON requests into data
        item = next(filter(lambda x: x["name"] == name, items), None) # find item
        message = ""
        status = 200
        if item is None: # no item found, add item name with JSON price
            item = {"name": name, "price": data["price"]}
            items.append(item)
            message += str(name) + " added"
            status = 201
        else:
            item.update(data) # item found, updated with JSON price
            message += str(name) + " updated"
        return {"message": message}, status

class ItemList(Resource):
    def get(self):
        return { "items" : items}


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")

app.run(port=5000, debug=True)
