import pymongo

connection_string = ""

# Create a MongoClient using the connection string
client = pymongo.MongoClient(connection_string,connect=False)

# Access a specific database
db = client['NK']

user_collection = db["users"]
claims_collection = db["claims"]


def add_user(email, hashed_password):
    user = {"email": email, "password": hashed_password}
    result = user_collection.insert_one(user)
    user_id = result.inserted_id
    return user_id


def get_user_by_email(email):
    user = user_collection.find_one({"email": email})
    return user


def get_user_by_id(user_id):
    user = user_collection.find_one({"_id": user_id})
    return user


def add_claim(claim):
    result = claims_collection.insert_one(claim)
    return result.inserted_id
