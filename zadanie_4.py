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
    app.db_connection.execute('''
                                INSERT INTO Categories (CategoryName)
                                VALUES (:name)
                                ''', {"name": category.name})

    inserted_record = app.db_connection.execute('''
                                                   SELECT CategoryID, CategoryName
                                                   FROM Categories
                                                   ORDER BY CategoryID DESC
                                                   LIMIT 1
                                                ''').fetchone()

    return {"id": inserted_record[0], "name": inserted_record[1]}


@app.put("/categories/{id}")
async def put_categories(id: int, category: Category):

    cursor = app.db_connection.cursor()
    cursor.execute('''
                      UPDATE Categories
                      SET CategoryName = :name
                      WHERE CategoryID = :id
                   ''', {"name": category.name, "id": id})

    cursor.row_factory = sqlite3.Row

    updated_record = cursor.execute('''
                                       SELECT *
                                       FROM Categories
                                       WHERE CategoryID = :id
                                    ''', {"id": id}).fetchone()

    if updated_record is None or len(updated_record) == 0:
        raise HTTPException(status_code=404)

    return updated_record


@app.delete("/categories/{id}")
async def delete_categories(id: int):
    deleted_record = app.db_connection.execute('''
                                                  SELECT *
                                                  FROM Categories
                                                  WHERE CategoryID = :id
                                               ''', {"id": id}).fetchone()

    if deleted_record is None or len(deleted_record) == 0:
        raise HTTPException(status_code=404)
    
    app.db_connection.execute('''
                                 DELETE FROM Categories
                                 WHERE CategoryID = :id
                              ''', {"id": id})
    return {"deleted": 1}
