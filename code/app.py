from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
app.secret_key = "Sean"
api = Api(app)

items = [] # The "database"

class Item(Resource):
    def get(self, name): # get request, looking for item called "name",
        for item in items: #loop through our "database" (local dictionary)
            if name == item["name"]:
                return {"item": item}, 200 #status OK, item found
        return {"item" : None}, 404 #not found

    def post(self, name):
        for item in items:
            if name == item["name"]:
                return {"message": "an item with name " + name + " already exists."}, 400 #bad request
        data = request.get_json() # what the user will send to the post request
        # In our case, the user sends the price as JSON, but the item name gets passed into the function
        item = {"name": name, "price": data["price"]}
        items.append(item) # push to database
        return item, 201 #post was successful

class ItemList(Resource):
    def get(self):
        return { "items" : items}


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")

app.run(port=5000, debug=True)
