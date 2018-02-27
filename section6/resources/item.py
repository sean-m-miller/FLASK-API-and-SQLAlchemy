import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser() #Item class parser
    parser.add_argument("price", #requests must be in format { "price": float}
        type=float,
        required=True,
        help="FORMAT ERROR: This request must have be string : float where string == price "
    )

    @jwt_required() # jwt authentification required
    def get(self, name): # get request, looking for item called "name",
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found"}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'An item with name ' + name + 'already exists.'}, 400
        data = Item.parser.parse_args() # what the user will send to the post request (in good format)
        # In our case, the user sends the price as JSON, but the item name gets passed into the function
        item = ItemModel(name, data["price"])
        try:
            item.insert()
        except:
            return{"message": "An error occurred while inserting"}, 500 # internal server error

        return item.json(), 201 #post was successful

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {"message": "Item Deleted"}

    def put(self, name):
        data = Item.parser.parse_args() # only add valid JSON requests into data

        item = ItemModel.find_by_name(name) # find item
        updated_item = ItemModel(name, data['price'])

        if item is None: # no item found, add item name with JSON price
            try:
                updated_item.insert()
            except:
                return {"message": "Error inserting item"}, 500
        else:
            try:
                updated_item.update() # item found, updated with JSON price
            except:
                return {"message": "Error inserting item"}, 500
        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items" #select all name matches
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'name':row[0], 'price':row[1]})

        connection.close()

        return {'items': items}
