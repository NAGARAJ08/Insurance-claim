import datetime
import jwt  # Use the PyJWT library

SECRET_KEY = "InsuranceApplication2023"


def generate_jwt_token(email):
    try:
        payload = {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        print(token)
        return token
    except Exception as e:
        print(f"Error generating JWT token: {str(e)}")
        return None


def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has Expired")
    except jwt.InvalidTokenError:
        print("Invalid Token")
