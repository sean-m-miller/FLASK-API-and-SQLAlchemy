from user import User

def authenticate(username, password):
    user = User.find_by_username(username) # user == None if no match
    if user and user.password == password:
        return user

def identity(payload):
    user_id = payload["identity"]
    return User.find_by_id(user_id)
