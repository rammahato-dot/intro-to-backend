# Intro to Backend and APIs Workshop

This repository is the companion project for a beginner-friendly session on backend fundamentals, APIs, REST thinking, FastAPI, and hands-on API testing with Postman.

The slides intentionally introduce Postman before the route-building section so every API endpoint can be verified immediately after it is created.

## What You Will Build

By the end of the workshop, you will have a small but complete backend that:

- serves a simple webpage from FastAPI,
- exposes a `/users` API,
- supports filtering users by age,
- fetches a single user by ID,
- accepts new user data through a `POST` request,
- and can be tested step by step in Postman.

The repository is intentionally simple so the focus stays on understanding the ideas, not fighting with setup.

## Prerequisites

Before the workshop, make sure you have these installed:

- Python 3.11 or newer
- Postman installed on your machine

Also make sure you can run `pip` from the terminal.

Verify Python:

```bash
python --version
```

If that does not work, try:

```bash
python3 --version
```

Postman should already be installed before you start the route-building part of the session. We use it right after the API concepts section so you can verify each endpoint as soon as it is introduced.

## Why Postman Comes Early

The slides introduce Postman before the FastAPI route examples on purpose.

That lets you practice the habit of testing an API as soon as you understand the request and response shape. Instead of only reading code, you will also see the endpoint behavior directly:

- request method,
- URL,
- query parameters,
- request body,
- response body,
- and status behavior.

This makes the session much more hands-on and easier to follow.

## Getting Started

### 1. Clone the repository, or download the zip file

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_NAME>
```

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
```

**Windows**

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows (Command Prompt)**

```cmd
.venv\Scripts\activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

You should now see `(.venv)` at the start of your terminal prompt.

### 4. Install the project dependencies

```bash
pip install -r requirements.txt
```

If `pip` is not available, use:

```bash
python -m pip install -r requirements.txt
```

### 5. Start the FastAPI development server

```bash
uvicorn app.main:app --reload
```

You should see output similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6. Open the app in your browser

Visit:

- http://127.0.0.1:8000

This loads the frontend from the `serve/` folder through FastAPI.

## API Reference

All API examples below use the local base URL:

```text
http://127.0.0.1:8000
```

### `GET /`

Returns the frontend page from `serve/index.html`.

This is the entry point for the app in a browser.

### `GET /users`

Returns the full list of users.

Optional query parameter:

- `ageLimit`

Examples:

```text
/users
/users?ageLimit=30
```

If `ageLimit` is provided, the response includes only users whose age is less than or equal to that value.

### `GET /users/{user_id}`

Returns one user by ID.

Example:

```text
/users/3
```

If the ID does not exist, the current implementation returns an empty object.

### `POST /users`

Creates a new user object in memory.

Expected JSON body:

```json
{
	"name": "Jane Doe",
	"age": 29,
	"address": "123 Main Street",
	"hobbies": ["Reading", "Traveling"]
}
```

The backend automatically assigns the new `id`.

Important note: the project keeps the data in memory, so newly added users are not permanently saved to disk.

## Route Implementation Walkthrough

The slides and the TODOs in [app/main.py](app/main.py) point to the same route logic. The goal of this section is to show the code you are meant to write and explain what each piece does.

### 1. Importing the tools FastAPI needs

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from typing import Optional, List

import json

from pydantic import BaseModel
```

These imports matter because each one supports a different part of the workshop:

- `FastAPI` creates the app object.
- `FileResponse` lets the root route return the HTML page.
- `StaticFiles` serves the frontend assets inside `serve/`.
- `Optional` is used for the query parameter that may or may not be provided.
- `List` describes a list of hobbies in the request body.
- `json` loads the sample user data from disk.
- `BaseModel` lets FastAPI validate incoming JSON automatically.

The `Optional[int]` type annotation is especially important. It tells FastAPI that `ageLimit` is not required. If the parameter is missing, the value becomes `None`, which makes the route logic much easier to read.

### 2. Defining the request body with a Pydantic model

```python
class User(BaseModel):
	name: str
	age: int
	address: str
	hobbies: List[str]
```

This model tells FastAPI what shape the incoming `POST` request should have.

Why this is helpful:

- FastAPI validates the data for you.
- The request body becomes self-documenting.
- The backend can reject malformed payloads before your route code even runs.

The `hobbies` field uses `List[str]`, which means the request must send an array of strings. That is why the `POST` example in Postman includes something like `"hobbies": ["Coding", "Reading"]`.

### 3. Loading the initial data

```python
with open("./data.json", "r") as file:
	users = json.load(file)
```

This line reads the starter user data into memory.

That means the server begins with a ready-made collection of users, and every request works against that in-memory list.

Important detail: this is a teaching project, so the data is not stored in a database. When the process restarts, the data goes back to whatever is inside `data.json`.

### 4. Creating the FastAPI app and serving static files

```python
app = FastAPI()
app.mount("/static", StaticFiles(directory="serve"), name="static")
```

The first line creates the application.

The second line makes files from `serve/` available under `/static`. This is why the frontend can load images and other static assets from the browser.

This is also a good place to remember the difference between an API route and a static asset route:

- API routes return data or app behavior.
- Static routes return files like images, CSS, or JavaScript.

### 5. Root route for the frontend page

```python
@app.get("/")
async def root():
	return FileResponse("serve/index.html")
```

This route makes the app usable from a browser.

When you visit `http://127.0.0.1:8000`, FastAPI sends the frontend page back to the browser.

The route is marked `async` because FastAPI supports asynchronous request handling, even though this specific route is simple enough that it does not need any async work inside the function.

### 6. `GET /users` with an optional query parameter

```python
@app.get("/users")
def get_users(ageLimit: Optional[int] = None):

	if ageLimit is None:
		return users

	return [user for user in users if user["age"] <= ageLimit]
```

This is one of the most important learning steps in the workshop.

The function accepts `ageLimit` as an optional query parameter. That means the URL can look like either of these:

- `/users`
- `/users?ageLimit=30`

How it works:

- If `ageLimit` is not present, the function returns every user.
- If `ageLimit` is present, the function filters the list.

This is the first place where type annotations become really useful in FastAPI. The annotation `Optional[int]` tells FastAPI to expect either an integer or nothing at all, and FastAPI handles the conversion from the incoming query string automatically.

### 7. `GET /users/{user_id}` with a path parameter

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
	for user in users:
		if user["id"] == user_id:
			return user

	return {}
```

This route reads the user ID directly from the URL path.

For example, `/users/1` sends `1` into the `user_id` parameter.

Why the `int` annotation matters here:

- FastAPI converts the path value to an integer.
- If the path value is not a number, the request will not match the expected type.
- This reduces manual parsing and makes the route safer to work with.

The loop searches the in-memory list and returns the matching user. If nothing is found, the current implementation returns an empty object. That is fine for a beginner workshop because it keeps the behavior easy to understand.

### 8. `POST /users` with JSON request data

```python
@app.post("/users")
def add_user(user: User):

	new_user_id = len(users) + 1

	new_user = {
		"id": new_user_id,
		**user.dict()
	}

	users.append(new_user)

	return {
		"id": new_user_id
	}
```

This route is where the request body becomes really important.

The `user: User` parameter tells FastAPI to parse the incoming JSON body into the `User` model.

What happens step by step:

- FastAPI validates the JSON body.
- The code creates a new numeric ID.
- The new ID is merged with the validated user data.
- The new object is added to the in-memory list.
- Only the new `id` is returned to the client.

This is a good teaching pattern because it shows the difference between the full stored object and the smaller response returned to the client.

## Frontend Implementation Walkthrough

The frontend file in [serve/script.js](serve/script.js) is the browser-side companion to the FastAPI routes. It shows how a JavaScript app talks to the backend with `fetch`.

### 1. Loading the user list

```javascript
async function loadUsers(ageLimit){

	let url="/users";

	if(ageLimit){
		url+=`?ageLimit=${ageLimit}`;
	}

	const response=await fetch(url);

	const users=await response.json();

	userList.innerHTML="";

	users.forEach(user=>{

		const card=document.createElement("div");

		card.className="user-card";

		card.innerHTML=`
			<img src="/static/avatar.svg" class="avatar">
			<h3>${user.name}</h3>
		`;

		card.onclick=()=>showUser(user.id);

		userList.appendChild(card);

	});

}
```

This function does three things:

- builds the request URL,
- fetches the user list from the backend,
- and renders the returned users into the page.

The `if(ageLimit)` block adds the query parameter only when the user wants to filter results. That mirrors the `GET /users` route in the backend.

The `response.json()` call is important because the backend returns JSON, and the frontend needs to convert it into a JavaScript object before it can render anything.

### 2. Loading one user into the modal

```javascript
async function showUser(id){

	const response=await fetch(`/users/${id}`);

	const user=await response.json();

	document.getElementById("modalName").innerText=user.name;

	document.getElementById("modalAge").innerText=user.age;

	document.getElementById("modalAddress").innerText=user.address;

	const hobbies=document.getElementById("modalHobbies");

	hobbies.innerHTML="";

	user.hobbies.forEach(hobby=>{

		const li=document.createElement("li");

		li.innerText=hobby;

		hobbies.appendChild(li);

	});

	modal.classList.remove("hidden");

}
```

This function demonstrates the path-parameter route in action.

It calls `/users/{id}`, reads the returned JSON, and uses the data to fill the modal.

This is a good example of why backend APIs matter: the frontend does not need to know where the data comes from, only what shape the response has.

### 3. Creating a new user with `POST`

```javascript
document.getElementById("saveUser").onclick=async()=>{

	const body={

		name:document.getElementById("name").value,

		age:Number(document.getElementById("age").value),

		address:document.getElementById("address").value,

		hobbies:document
			.getElementById("hobbies")
			.value
			.split(",")
			.map(h=>h.trim())
	};

	await fetch("/users",{

		method:"POST",

		headers:{
			"Content-Type":"application/json"
		},

		body:JSON.stringify(body)

	});

	addModal.classList.add("hidden");

	loadUsers();

};
```

This is the frontend version of the `POST /users` route.

The most important part here is the request header:

```javascript
"Content-Type":"application/json"
```

That header tells the server that the request body is JSON. Without it, the backend may not interpret the payload the way you expect.

The code then converts the JavaScript object into a JSON string with `JSON.stringify(body)` before sending it to the server.

After the request finishes, the UI closes the modal and reloads the user list so the new user appears immediately.

### 4. Why the frontend code is structured this way

The frontend code is intentionally simple and direct because the lesson is about understanding the request/response cycle.

The key ideas are:

- `fetch` sends the HTTP request,
- `await response.json()` reads the JSON response,
- query parameters are added in the URL,
- `POST` requests send a JSON body,
- headers tell the server what format the body uses.

That is the exact bridge between the slides, the backend, and the browser.

## Postman Verification Guide

Use Postman after the server is running and before moving on to the frontend behavior.

### Step 1: Verify `GET /users`

Create a new `GET` request in Postman:

- Method: `GET`
- URL: `http://127.0.0.1:8000/users`

What to check:

- The response should be a JSON array.
- You should see all users from `data.json`.
- The response should be easy to read in Postman’s formatted JSON view.

### Step 2: Verify `GET /users` with `ageLimit`

Use the same endpoint, but add a query parameter:

- Method: `GET`
- URL: `http://127.0.0.1:8000/users?ageLimit=30`

What to check:

- Only users aged 30 or below should appear.
- This confirms that the query parameter is being read and used correctly.

### Step 3: Verify `GET /users/{user_id}`

Create another `GET` request:

- Method: `GET`
- URL: `http://127.0.0.1:8000/users/1`

What to check:

- You should receive the user with ID `1`.
- Try a few other IDs as well, such as `2` or `10`.
- If you use an ID that does not exist, the current code returns an empty object.

### Step 4: Verify `POST /users`

Create a `POST` request:

- Method: `POST`
- URL: `http://127.0.0.1:8000/users`
- Headers: `Content-Type: application/json`

Use this body:

```json
{
	"name": "New Student",
	"age": 24,
	"address": "221B Baker Street",
	"hobbies": ["Coding", "Reading"]
}
```

What to check:

- The response should return a new `id`.
- After the request, send `GET /users` again and confirm the new user appears in the list for the current server session.

## Project Structure

```text
.
├── app/
│   └── main.py
├── serve/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── data.json
├── requirements.txt
├── slides.pptx
└── README.md
```

## Troubleshooting

### `python` is not recognized

Try:

```bash
python3 --version
```

and use `python3` instead of `python` on macOS or Linux.

### `pip` is not recognized

Run:

```bash
python -m pip install -r requirements.txt
```

or:

```bash
python3 -m pip install -r requirements.txt
```

### The server will not start

Double-check that your virtual environment is active and that the dependencies finished installing successfully.

### Postman requests are failing

Make sure the FastAPI server is running at `http://127.0.0.1:8000` and that your request URLs match that base address exactly.

### The app looks empty in the browser

Confirm that you are visiting the root route at `http://127.0.0.1:8000` and not opening `serve/index.html` directly from the filesystem.
