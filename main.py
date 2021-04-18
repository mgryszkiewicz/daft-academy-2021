from fastapi import FastAPI, Response, status
import hashlib

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/method")
def get_method():
    return {"method": "GET"}

@app.put("/method")
def put_method():
    return {"method": "PUT"}

@app.options("/method")
def options_method():
    return {"method": "OPTIONS"}

@app.delete("/method")
def delete_method():
    return {"method": "DELETE"}

@app.post("/method", status_code=201)
def post_method():
    return {"method": "POST"}

@app.get("/auth{password, password_hash}", status_code = 401)
def get_auth(authentication, response: Response):
    password = authentication.get("password")
    password_hash = authentication.get("password_hash")
    if hashlib.sha512(str(password).encode('utf-8').hexdigest()) == password_hash:
        response.status_code = 204

