from fastapi import FastAPI, Response, status, HTTPException
from typing import NoReturn, Optional
from pydantic import BaseModel
import sqlite3
import sys

app = FastAPI()

class Category(BaseModel):
    name: str


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/")
async def main():
    return {"sqlite3_library_version": sqlite3.version, "sqlite_version": sqlite3.sqlite_version}

@app.get("/categories")
async def categories():
    categories = app.db_connection.execute('''SELECT CategoryID AS id, CategoryName AS name
                                              FROM Categories
                                              ORDER BY id
                                              ''')
    return {"categories": [{"id": row[0], "name": row[1]} for row in categories]}


@app.get("/customers")
async def customers():
    customers = app.db_connection.execute('''Select CustomerID AS id, CompanyName AS name, COALESCE(Address,''), COALESCE(PostalCode,''), COALESCE(City,''), COALESCE(Country,'')
                                             FROM Customers
                                             ORDER BY id COLLATE NOCASE
                                             ''')
    return {"customers": [{"id": row[0], "name": row[1], "full_address": "{} {} {} {}".format(row[2], row[3], row[4], row[5])} for row in customers]}


@app.get("/products/{id}")
async def products(id: int):
    product = app.db_connection.execute('''SELECT ProductID, ProductName
                                           FROM Products
                                           WHERE ProductID = :id
                                           ''', {'id': id}).fetchone()
    if product is None:
        raise HTTPException(status_code=404)
    return {"id": product[0], "name": product[1]}


@app.get("/employees")
async def employees(limit: Optional[int]=None, offset: Optional[int]=None, order: Optional[str]=None):
    if order not in ("first_name", "last_name", "city", None):
        raise HTTPException(status_code=400)
    if limit is None:
        limit = sys.maxsize
    if offset is None:
        offset = 0
    if order is None:
        order = "id"
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=400)

    employees = app.db_connection.execute('''SELECT EmployeeID AS id, LastName AS last_name, FirstName AS first_name, City AS city
                                             FROM Employees
                                             ORDER BY {}
                                             LIMIT :limit OFFSET :offset
                                             '''.format(order), {'limit': limit, 'offset': offset})

    return {"employees": [{"id": row[0], "last_name": row[1], "first_name": row[2], "city": row[3]} for row in employees]}


@app.get("/products_extended")
async def products_extended():
    products_extended = app.db_connection.execute('''SELECT p.ProductID AS id, p.ProductName AS name, c.CategoryName AS category, s.CompanyName AS supplier
                                                     FROM Products AS p
                                                     JOIN Categories AS c
                                                     ON p.CategoryID = c.CategoryID
                                                     JOIN Suppliers AS s
                                                     ON p.SupplierID = s.SupplierID''')

    return {"products_extended": [{"id": row[0], "name": row[1], "category": row[2], "supplier": row[3]} for row in products_extended]}


@app.get("/products/{id}/orders")
async def products_orders(id: int):
    products_orders = app.db_connection.execute('''SELECT o.OrderID AS id, c.CompanyName AS customer, od.Quantity, ROUND((od.UnitPrice * od.Quantity) - (od.Discount * (od.UnitPrice * od.Quantity)), 2) AS total_price
                                                   FROM Orders AS o
                                                   JOIN Customers AS c
                                                   ON o.CustomerID = c.CustomerID
                                                   JOIN "Order Details" as od
                                                   ON o.OrderID = od.OrderID
                                                   WHERE od.ProductID = :id                                                                                                
                                                   ''', {"id": id}).fetchall()

    if products_orders is None or len(products_orders) == 0:
        raise HTTPException(status_code=404)

    return {"orders": [{"id": row[0], "customer": row[1], "quantity": row[2], "total_price": row[3]} for row in products_orders]}


@app.post("/categories", status_code=201)
async def post_categories(category: Category):
    inserted_record = app.db_connection.execute('''
                                                   INSERT INTO Categories (CategoryName)
                                                   VALUES (:name)
                                                   RETURNING *
                                                ''', {"name": category.name}).fetchone()
    return {"id": inserted_record[0], "name": inserted_record[1]}



# @app.get("/")
# def root():
#     return {"message": "Hello world!"}


# @app.get("/method")
# def get_method():
#     return {"method": "GET"}


# @app.put("/method")
# def put_method():
#     return {"method": "PUT"}


# @app.options("/method")
# def options_method():
#     return {"method": "OPTIONS"}


# @app.delete("/method")
# def delete_method():
#     return {"method": "DELETE"}


# @app.post("/method", status_code=201)
# def post_method():
#     return {"method": "POST"}


# @app.get("/auth", status_code=401)
# def get_auth(response: Response, password: Optional[str] = "", password_hash: Optional[str] = ""):
#     if password == "" or password_hash == "":
#         return
#     if hashlib.sha512(str(password).encode('utf-8')).hexdigest() == password_hash:
#         response.status_code = 204


# @app.post("/register", status_code=201)
# def post_register(data: dict, response: Response):
#     name = data.get("name")
#     surname = data.get("surname")

#     if name is None or surname is None:
#         response.status_code = 422
#         return

#     name_shift = sum(map(str.isalpha, str(name)))
#     surname_shift = sum(map(str.isalpha, str(surname)))
#     shift = surname_shift + name_shift
#     app.id_counter += 1

#     app.patients[app.id_counter] = {
#         "id": app.id_counter,
#         "name": str(name),
#         "surname": str(surname),
#         "register_date": datetime.datetime.today().strftime('%Y-%m-%d'),
#         "vaccination_date": (datetime.datetime.today() + datetime.timedelta(days=shift)).strftime('%Y-%m-%d')
#     }
#     return app.patients[app.id_counter]


# @app.get("/patient/{patient_id}", status_code=200)
# def get_patient(patient_id: int, response: Response):
#     if patient_id < 1:
#         response.status_code = 400
#         return
#     elif patient_id not in app.patients:
#         response.status_code = 404
#         return
#     else:
#         return app.patients[patient_id]
