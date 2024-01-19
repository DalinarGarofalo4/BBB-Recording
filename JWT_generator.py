from jose import jwt
from fastapi import Depends
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def write_to_JWT_file():
    payload = dict()
    encoded_jwt = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    with open('JWT.txt', 'w') as file:
        file.write(encoded_jwt)
write_to_JWT_file()
