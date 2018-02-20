from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from security import authenticate, identity
from user import UserRegister
from item import Item, ItemList

app = Flask(__name__)
app.secret_key = "Sean"
api = Api(app)

jwt = JWT(app, authenticate, identity) # calls authenticate and identity in security.py

api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, '/register')

if __name__ == '__main__': # prevents app from running when being imported from elsewhere
    app.run(port=5000, debug=True)
