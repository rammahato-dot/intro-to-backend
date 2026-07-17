# Import the various objects from the FastAPI library
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Utility library for type information
from typing import Optional, List

# Import the json standard library
import json

# Import the BaseModel class for JSON support
from pydantic import BaseModel


# This class User will tell us the structure in which the POST request data will be accepted
class User(BaseModel):
    name: str
    age: int
    address: str
    hobbies: List[str]


# Open the file in read mode, and store the contents in the variable users
with open("./data.json", "r") as file:
    users = json.load(file)

# Create an instance of the FastAPI app
app = FastAPI()

# Mount the app with the configuration to serve the static assets from the serve directory
app.mount("/static", StaticFiles(directory="serve"), name="static")


# The / route specifies the root address of the URL
# The GET method means that this request can also be analysed by entering the address on the browser address bar
@app.get("/")
async def root():
    return FileResponse("serve/index.html")


# TODO: Add the GET endpoint for /users that also expects an optional ageLimit parameter. When the ageLimit parameter is not present, it returns a list of all the users. When the parameter is present, it only returns the users whose age is less than or equal to the ageLimit

@app.get("/users")
async def get_users(ageLimit: Optional[int] = None):
    if ageLimit is None:
        return users
    else:
        return [user for user in users if user.age <= ageLimit]

# TODO: Add the GET endpoint for /users/{user_id} that returns the user for that id by doing a lookup in the users list according to the id provided.

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    return {"error": "User not found"}

# TODO: Add the POST endpoint for /users that accepts the User object, adds the required id to the object, and finally appends the newly created user object to the users list

@app.post("/users")
async def create_user(user: User):
    new_id = max(user.id for user in users) + 1 if users else 1
    new_user = user.dict()
    new_user["id"] = new_id
    users.append(new_user)
    return new_user