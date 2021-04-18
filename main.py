from fastapi import FastAPI, Response, status
import datetime
import hashlib

app = FastAPI()
app.id_counter = 0
app.patients = dict()

@app.get("/")
def root():
    return {"message": "Hello world!"}

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

@app.get("/auth", status_code = 401)
def get_auth(password: str, password_hash: str, response: Response):
    # password = authentication.get("password")
    # password_hash = authentication.get("password_hash")
    if hashlib.sha512(str(password).encode('utf-8')).hexdigest() == password_hash:
        response.status_code = 204

@app.post("/register", status_code=201)
def post_register(data: dict, response: Response):
    name = data.get("name")
    surname = data.get("surname")

    if name is None or surname is None:
        response.status_code = 422
        return

    app.id_counter += 1
    app.patients[app.id_counter] = {
            "id": app.id_counter,
            "name": name,
            "surname": surname,
            "register_date": (datetime.datetime.today()).strftime('%Y-%m-%d'),
            "vaccination_date": (datetime.datetime.today() + datetime.timedelta(days=len(name) + len(surname))).strftime('%Y-%m-%d')
            }
    return app.patients[app.id_counter]


@app.get("/patient/{patient_id}", status_code=200)
def get_patient(patient_id: int, response: Response):
    print("\n\n\n\nHaloooo\n\n\n" + str(app.patients))
    if patient_id < 1:
        response.status_code = 400
        return
    elif patient_id not in app.patients:
        response.status_code = 404
        return
    else:
        return app.patients[patient_id]
