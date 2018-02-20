import sqlite3
from flask_restful import Resource, reqparse

class User:
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db') # database "plumbing"
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username=?" # ? will be username
        result = cursor.execute(query, (username,)) # arguments must be a tuple, use comma even if only one arg
        row = result.fetchone() # fetch a row where username matches
        if row is not None:
            user = cls(row[0], row[1], row[2]) # passing (id, username, password) into User constructor
        else:
            user = None

        connection.close()
        return user # return either a user object, or None

    @classmethod
    def find_by_id(cls, _id):
        connection = sqlite3.connect('data.db') # database "plumbing"
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE id=?" # ? will be id
        result = cursor.execute(query, (_id,)) # arguments must be a tuple, use comma even if only one arg
        row = result.fetchone() # fetch a row where username matches
        if row is not None:
            user = cls(row[0], row[1], row[2]) # (id, username, id), constructor
        else:
            user = None

        connection.close()
        return user # return either a user object, or None

class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        if User.find_by_username(data['username']):
            return {"message": "that username already exists"}, 400 #prevents duplicate users.

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'INSERT INTO users VALUES (NULL, ?, ?)'
        cursor.execute(query, (data['username'], data['password']))

        connection.commit()
        connection.close()

        return {"message": "User created successfully."}, 201
