from user import User

users = [
    User(1, "bob", "hello")
]

username_mapping = {u.username: u for u in users} # search through users to create mapping
userid_mapping = {u.id: u for u in users}

def authenticate(username, password):
    user = username_mapping.get(username, None) # user == None if no match
    if user and user.password == password:
        return users

def identity(payload):
    user_id = payload["identity"]
    return userid_mapping.get(user_id, None)
