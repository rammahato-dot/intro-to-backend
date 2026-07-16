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

## Next Steps

This project is a good starting point, but it is still running in a very local setup. The next layer of learning is to understand how applications move from your own machine to a real network and eventually to the public internet. That shift is where backend development starts to feel practical instead of just theoretical, because the same app can behave very differently depending on where it is running and who is allowed to reach it.

### 1. From loopback to the internet

Right now, the app runs on the loopback address, which means it is only reachable from the same machine. That is why `http://127.0.0.1:8000` works for local development. The loopback address is a special address that always points back to your own computer, so it is perfect for testing and debugging, but it is intentionally isolated from the rest of the network.

To make the app reachable from other devices on your network, start Uvicorn with `0.0.0.0` as the host:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

`0.0.0.0` means "listen on every network interface." That is the key difference between an app that only works on your own machine and an app that another device on the same Wi-Fi can reach.

After starting the server this way, find the machine’s private IP address.

On macOS or Linux, run:

```bash
ifconfig
```

On Windows, run:

```bash
ipconfig
```

Look for the active adapter’s IPv4 address, usually something like `192.168.x.x` or `10.x.x.x`.

Now, from another device on the same network, open:

```text
http://192.168.x.x:8000
```

That is local network hosting. The app is still running on your machine, but the private IP lets other devices on the same network reach it.

If you want to expose the app to the internet without deploying it to a VPS yet, use ngrok.

The basic flow is:

1. Install ngrok.
2. Sign in and add your ngrok auth token if it asks for one.
3. Start the FastAPI app on port `8000`.
4. Open a tunnel to that port.

```bash
ngrok http 8000
```

ngrok will give you a public URL such as `https://xxxx.ngrok-free.app`. Anyone who opens that URL is forwarded to your local FastAPI app. This is useful for demos, sharing with classmates, testing webhooks, or showing a project without setting up a full server.

This is the path from local development to real deployment:

- `127.0.0.1` for only your own machine,
- private IP for devices on the same network,
- ngrok for a public tunnel to your local machine,
- public IP or domain name for a real hosted server.

Once you understand that progression, deployment becomes much less mysterious.

### 2. How the internet works

To understand backend development deeply, it helps to learn the basics of networking. The internet is built on connected devices exchanging data through protocols, and HTTP is the protocol most web apps use. A browser does not magically know where your app lives; it resolves a name or IP address, opens a network connection, and then speaks a protocol that both sides understand.

TCP is the transport layer that carries HTTP traffic. In brief, TCP makes sure data moves reliably between two machines. It establishes a connection, keeps track of what was sent, retransmits lost packets, and delivers data in order. You normally do not write TCP code in a beginner FastAPI app, but HTTP depends on it.

In a typical HTTP flow:

- the browser or frontend sends a request,
- the server receives it and processes it,
- the server sends back a response,
- and the client renders or uses that response.

This request-response cycle is the crux of web development. Once you understand URLs, IP addresses, ports, TCP connections, and HTTP methods like `GET` and `POST`, a lot of backend behavior starts making sense.

The important pieces fit together like this:

- The URL tells the client where to go and what resource to ask for.
- The IP address identifies the server machine on the network.
- The port identifies which application on that machine should receive the request.
- TCP provides a reliable connection so the data arrives in the correct order.
- HTTP defines the language of the conversation, including methods, headers, status codes, and body data.

HTTP is where backend developers spend most of their time, so it helps to know what is actually inside a request and response.

An HTTP request usually contains:

- a method, such as `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`,
- a path, such as `/users` or `/users/3`,
- optional query parameters, such as `?ageLimit=30`,
- headers, which carry metadata like `Content-Type` or authentication tokens,
- and an optional body, which is commonly JSON for `POST` and `PUT` requests.

An HTTP response usually contains:

- a status code,
- headers,
- and a body.

The status code is the first thing you should check when a request fails. Some common ones are:

- `200` for success,
- `201` when something is created,
- `400` when the client sends invalid data,
- `404` when the route or resource is not found,
- and `500` when the server hits an unexpected error.

Headers matter because they tell the client how to interpret the response. For example, `Content-Type: application/json` tells the client that the body is JSON. That is why the frontend can call `response.json()` and why tools like Postman can format the result properly.

When you send a `GET` request, you are usually asking for data. When you send a `POST` request, you are usually asking the server to create or process something. The response then tells you whether the request worked, failed, or needs more information. That is the core pattern behind almost every web app.

### 3. Why databases matter

This project stores data in a file and loads it into memory, which is fine for learning. But file-based storage has limits:

- it is harder to query efficiently,
- concurrent writes can become messy,
- data can be lost when the process restarts,
- and it does not scale well for real applications.

That is why applications usually use databases instead. A file works when the data is tiny and the app is simple, but it becomes fragile once more users, more updates, and more relationships appear. Two requests updating the same file at the same time can conflict, and reading or filtering data often becomes slow because the entire file has to be loaded and searched manually.

With a database, the storage layer is built for these problems. The application server talks to a database server over the network, sends queries, and reads results back. This separation makes storage more reliable, more structured, and much easier to grow with the application. The app server handles your business logic, while the database server specializes in storing, indexing, filtering, and protecting the data.

To make this concrete, you can migrate this project from a JSON file to SQLite, which is a lightweight database that stores everything in one local database file but still gives you real SQL queries and persistence.

The current user objects already map cleanly to a database table:

```json
{
  "id": 1,
  "name": "Alice Johnson",
  "age": 28,
  "address": "123 Maple Street, Seattle",
  "hobbies": ["Reading", "Hiking", "Photography"]
}
```

A simple SQLite table for the same data could look like this:

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  age INTEGER NOT NULL,
  address TEXT NOT NULL,
  hobbies TEXT NOT NULL
);
```

Here, `hobbies` is stored as text. The normal approach is to serialize the Python list into JSON before inserting it into SQLite, then deserialize it back into a list when reading it out.

That gives you a simple migration plan:

1. Load the existing `data.json` file once.
2. Create the SQLite table if it does not already exist.
3. Insert each JSON user into the table.
4. Replace the in-memory `users` list with SQL queries.
5. Update `GET /users` to read from SQLite.
6. Update `GET /users/{user_id}` to fetch one row by ID.
7. Update `POST /users` to insert a new row.
8. Keep the API response shape the same, even though the storage backend changed.

Here is a minimal Python example using the built-in `sqlite3` module:

```python
import json
import sqlite3

connection = sqlite3.connect("users.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	address TEXT NOT NULL,
	hobbies TEXT NOT NULL
)
""")

with open("data.json", "r") as file:
	users = json.load(file)

for user in users:
	cursor.execute(
		"INSERT OR IGNORE INTO users (id, name, age, address, hobbies) VALUES (?, ?, ?, ?, ?)",
		(
			user["id"],
			user["name"],
			user["age"],
			user["address"],
			json.dumps(user["hobbies"]),
		),
	)

connection.commit()
```

Once the data is stored in SQLite, the backend can query only what it needs. For example, filtering by age becomes a SQL query such as `SELECT * FROM users WHERE age <= ?` instead of a Python list comprehension.

The same `User` model from this project still applies:

```python
class User(BaseModel):
	name: str
	age: int
	address: str
	hobbies: List[str]
```

The difference is in storage, not in the API contract. The frontend can keep sending the same JSON, and the backend can keep returning the same kind of response, while SQLite handles persistence.

If you want to make the migration cleaner, add a small helper to convert a database row back into the API format:

```python
def row_to_user(row):
	return {
		"id": row[0],
		"name": row[1],
		"age": row[2],
		"address": row[3],
		"hobbies": json.loads(row[4]),
	}
```

That way, the route logic stays simple even after the storage layer changes.

In a real backend, this usually means:

- the application server receives the HTTP request,
- it validates and prepares the data,
- it sends a SQL or database query to the database server,
- the database server returns the result,
- and the application server formats the final HTTP response.

That separation is one of the biggest ideas in backend architecture.

### 4. Learn backend in depth

If you want a deeper backend path after this workshop, check out ProCodrr’s backend course on [procodrr.com](https://procodrr.com). The site currently highlights their [Backend with Node.js](https://app.procodrr.com/web/checkout/66c86939c0a286ccc32c0d8b) course, which is a good next step for learning backend concepts beyond this starter FastAPI project.

That kind of course is useful once you are comfortable with the basics in this repo, because it can take you from simple request handling into topics like routing structure, API design, database integration, authentication, and production-style backend patterns.

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
