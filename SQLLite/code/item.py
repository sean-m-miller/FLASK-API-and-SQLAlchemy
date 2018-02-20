import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

class Item(Resource):
    parser = reqparse.RequestParser() #Item class parser
    parser.add_argument("price", #requests must be in format { "price": float}
        type=float,
        required=True,
        help="FORMAT ERROR: This request must have be string : float where string == price "
    )

    @jwt_required() # jwt authentification required
    def get(self, name): # get request, looking for item called "name",
        item = self.find_by_name(name)
        if item:
            return item
        return {"message": "Item not found"}, 404

    @classmethod
    def find_by_name(cls, name): # abstracted and redifined from get
        # Does NOT require jwt_auth, so it can be used by both get and post
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()
        if row:
            return {"item": {"name": row[0], "price": row[1]}}


    def post(self, name):
        if self.find_by_name(name):
            return {'message': 'An item with name ' + name + 'already exists.'}, 400
        data = Item.parser.parse_args() # what the user will send to the post request (in good format)
        # In our case, the user sends the price as JSON, but the item name gets passed into the function
        item = {"name": name, "price": data["price"]}
        try:
            self.insert(item)
        except:
            return{"message": "An error occurred while inserting"}, 500 # internal server error

        return item, 201 #post was successful

    @classmethod
    def insert(cls, item):
        # write to database
        # abstracted just like find_by_name so that it can be used by both post and put
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()

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

        item = self.find_by_name(name) # find item
        updated_item = {'name': name, 'price': data['price']}

        if item is None: # no item found, add item name with JSON price
            try:
                self.insert(updated_item)
            except:
                return {"message": "Error inserting item"}, 500
        else:
            try:
                self.update(updated_item) # item found, updated with JSON price
            except:
                return {"message": "Error inserting item"}, 500
        return item

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()


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
