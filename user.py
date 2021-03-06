from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_restful import Resource, reqparse
from math import ceil

from db import db

page_size = 20

def jwt_exists(token): # for get requests
    data = UserModel.query.filter_by(jwt=token).all()
    if len(data) > 0:
        return True
    else:
        return False

def jwt_match(google_tok, jwt): # for post, put, and delete requests
    user = UserModel.find_by_google_tok(google_tok)
    if user.jwt == jwt:
        return True
    else:
        return False

class UserModel(db.Model):
    """The UserModel object stores information about the user, as well as
    the listing objects that are associated with it.
Attributes:
    google_tok (string): The google token for the user.
    imageURL (string): The URL referencing the user's image.
    email (string): The user's email.
    name (string): The user's first name.
    givenName (string): The user's given name.
    familyName (string): The user's last name.
    listings (ListingModel[]): All listings posted by the user,
    jwt (string): The jwt token passed from frontend used for authentification
"""

# Creates a table named 'users'
    __tablename__ = 'users'

    google_tok = db.Column(db.String, primary_key=True)
    imageURL = db.Column(db.String)
    email = db.Column(db.String)
    name = db.Column(db.String)
    givenName = db.Column(db.String)
    familyName = db.Column(db.String)
    listings = db.relationship("ListingModel")
    jwt = db.Column(db.String)

    def __init__(self, google_tok, imageURL, email, name, givenName, familyName, jwt):
        self.google_tok = google_tok
        self.imageURL = imageURL
        self.email = email
        self.name = name
        self.givenName = givenName
        self.familyName = familyName
        self.jwt = jwt


    def get_listings(self):
        """Get a list of book listing jsons posted by the user.

        Args:
                none.

        Returns:
                json[]: A list of jsonified listings.
        """
        listing_ids = []
        for listing in self.listings:
            listing_ids.append(listing.listing_json_w_book())
        return listing_ids

    # Returns a json object representing the book
    def user_json_wo_listings(self):  # listings already displayed
        """Returns a jsonified user item.

        Args:
                none.

        Returns:
                json: A json item representing the user.
        """
        return {'google_tok': self.google_tok, 'imageURL': self.imageURL, 'email': self.email, 'name': self.name, 'givenName': self.givenName, 'familyName': self.familyName}

    def user_json_w_listings(self):  # listings not already displayed
        """Returns a jsonified user item, with a list of jsonified listings.

        Args:
                none.

        Returns:
                json: A json item representing the user.
        """
        return {'google_tok': self.google_tok, 'imageURL': self.imageURL, 'email': self.email, 'name': self.name, 'givenName': self.givenName, 'familyName': self.familyName, 'listings': self.get_listings()}

    def bare_json(self):
        """Returns a jsonified user item, with a list of listing ids.

        Args:
                none.

        Returns:
                json: A json item representing the user.
        """
        return {'google_tok': self.google_tok, 'imageURL': self.imageURL, 'email': self.email, 'name': self.name, 'givenName': self.givenName, 'familyName': self.familyName, 'listing_ids': [listing.listing_id for listing in self.listings]}

    @classmethod
    # emails are unique between students, used to see if user exists or not
    def find_by_email(cls, email):
        """Finds a user by email.

        Args:
                email (str): The email of the user we're searching for.

        Returns:
                UserModel: The user who matches the email.
        """
        return UserModel.query.filter_by(email=email).first()

    @classmethod
    def find_by_google_tok(cls, google_tok):
        """Finds a user by google token.

        Args:
                google_tok (str): The google token of the user we're looking for.

        Returns:
                UserModel: The user who matches the google token..
        """
        return UserModel.query.filter_by(google_tok=google_tok).first()

    def save_to_db(self):
        """Saves the user to the database.

        Args:
                none.

        Returns:
                json: A json item representing the user.
        """
        db.session.add(self)
        db.session.commit()
        return self.user_json_wo_listings()

    def delete_from_db(self):
        """Deletes the user from the database.

        Args:
                none.

        Returns:
                none.
        """
        db.session.delete(self)
        db.session.commit()
        for listing in self.listings:
            listing.delete_from_db()

    def __repr__(self):
        """Defines how the user class will appear when printed.

        Args:
                none.

        Returns:
                none.
        """
        return "<User(name='%s', email='%s')>" % (
            self.name, self.email)


class User(Resource):
    parser = reqparse.RequestParser()  # Book class parser
    parser.add_argument('google_tok',
                        type=str,
                        required=False,
                        help="goog_tok required."
                        )
    parser.add_argument('imageURL',
                        type=str,
                        required=False,
                        help="check format"
                        )
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('givenName',
                        type=str,
                        required=True,
                        help="must provide givenName"
                        )
    parser.add_argument('familyName',
                        type=str,
                        required=True,
                        help="must provide familyName"
                        )
    parser.add_argument('jwt',
                        type=str,
                        required=True,
                        help="jwt token required")

    def get(self, tokens):
        """Get request, looking for all users with google token.

        Args:
                tokens (str): The google token and jwt token.

        Returns:
                json[]: A list of jsonified users.
        """
        #strings = find.split("+")
        #google_tok = int(strings[0])
        #page = int(strings[1])
        tokens = tokens.split("+")
        if len(tokens) <= 1:
            return {"message": "oops! you forgot your jwt or google token"}
        if not jwt_exists(tokens[1]):
            return {"message": "Be gone hacker! your jwt token does not exist in database"}
        google_tok = tokens[0]
        user = UserModel.find_by_google_tok(google_tok)
        listing_IDs = []
        if user:
            for listing in user.listings:
                listing_IDs.append(listing.listing_id)
            return {'google_tok': user.google_tok, 'imageURL': user.imageURL, "email": user.email, "name": user.name, "givenName": user.givenName, 'familyName': user.familyName, "listings": listing_IDs}
            # user.user_json_w_listings()
            #of = ceil(len(all_listings)/page_size)
            # return{"user": [all_listings[i].user_json_w_listings() for i in range(page*page_size, min(((page+1)*page_size),len(all_listings)))], "page": page, "of": of}
        return {"message": "user not found"}, 404

    def post(self, tokens):
        """Posts a user to the database.

        Args:
                google_tok (str): The google token of the user being posted.

        Returns:
                message: What happened with the post call.
        """
        data = User.parser.parse_args()
        if UserModel.find_by_google_tok(tokens):
            return {'message': 'A user with that google_token already exists'}, 400
        user = UserModel(tokens, data['imageURL'], data['email'],
                         data['name'], data['givenName'], data['familyName'], data["jwt"])
        user.save_to_db()
        return {"message": "User created successfully."}, 201

    def delete(self, tokens):
        """Deletes a user from the database.

        Args:
                tokens (str): The google token and jwt token.

        Returns:
                message: What happened with the delete call.
        """
        data = User.parser.parse_args()
        if not jwt_match(tokens, data["jwt"]):
            return {"message": "begone hacker! your jwt does not match your google token"}
        user = UserModel.find_by_google_tok(tokens)
        if user:
            user.delete_from_db()
            return {"message": "User deleted"}
        return {"message": "User with user_id (" + tokens + ") does not exist."}

    def put(self, tokens): # pass in google_token, with new jwt in the body
        # this poses security threats...
        # Could anyone send a post request to chenge a user's jwt to be anything they wanted
        # But how could we jave jwt be required for this function... frontend would have to save
        # previous jwt token of this user from last login
        try:
            data = User.parser.parse_args()
            user = UserModel.find_by_google_tok(tokens)
            user.jwt = data["jwt"]
            user.save_to_db()
            return user.bare_json()
        except:
            return {"message": "error. Unable to update jwt - line 285 user.py"}

class UserList(Resource):
    """The UserList object handles the entire list of users in the database.

Attributes:
    none.
"""

    def get(self, tokens):
        """Gets a list of all users in database that match any token from a list
        of tokens..

        Args:
                tokens (str[]): A list of tokens to query with.

        Returns:
                json[]: A list of jsonified users that match the tokens.
        """

        tokens = tokens.split("+")
        if not jwt_exists(tokens[1]):
            return {"message": "begone hacker! your jwt is invalid"}
        print(tokens[0])
        all_users = UserModel.query.filter(
            UserModel.google_tok.in_(tokens[:1])).all() # for some reason, the string contained at tokens[0] doesn't support _in, but the LIST at index tokens[0] does
        print(len(all_users))
        #of = ceil(len(all_listings)/page_size)
        # return {"users": [all_listings[i].user_json_w_listings() for i in range(page*page_size, min(((page+1)*page_size),len(all_listings)))], "page": page, "of": of}

        return {"users": [user.bare_json() for user in all_users]}

    #	return {"users": [user.user_json_w_listings() for user in UserModel.query.all()]}

    # search_ = strings[1]
    # for i in search_:
    # 	if i == "_":
    # 		search_by.append(" ")
    # 	else:
    # 		search_by.append(i)
    # search_by = ''.join(search_by)
    # if len(strings[2]) > 0: # price was provided
    # 	price = float(strings[2])
    # 	if len(strings[3]) > 0: #condition was provided
    # 		condition = strings[3] # "bad", "ehh", "good", or "new"
    # 		print(search_by)
    # 		all_listings = ListingModel.query.filter(ListingModel.book.book_json_wo_listings()["author"] == search_by or ListingModel.book.book_json_wo_listings()["title"] == search_by).filter(ListingModel.price <= price).filter(ListingModel.condition >= condition).all()
    # 		return{"listings": [all_listings[i].listing_json_w_book_and_user() for i in range(page*page_size, min(((page+1)*page_size),len(all_listings)))], "page": page, "of": of}
