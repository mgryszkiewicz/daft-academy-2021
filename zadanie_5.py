from fastapi import FastAPI, Response, status, HTTPException
from typing import NoReturn, Optional
from pydantic import BaseModel
import sqlite3
import sys

app = FastAPI()

class Supplier(BaseModel):
    CompanyName: str
    ContactName: Optional[str] = ""
    ContactTitle: Optional[str] = ""
    Address: Optional[str] = ""
    City: Optional[str] = ""
    PostalCode: Optional[str] = ""
    Country: Optional[str] = ""
    Phone: Optional[str] = ""

class SupplierPut(BaseModel):
    CompanyName: Optional[str] = ""
    ContactName: Optional[str] = ""
    ContactTitle: Optional[str] = ""
    Address: Optional[str] = ""
    City: Optional[str] = ""
    PostalCode: Optional[str] = ""
    Country: Optional[str] = ""
    Phone: Optional[str] = ""


def text_factory_custom(text: str):
    text = text.decode(encoding='latin1')
    text = text.replace("\n", " ")
    if len(text) > 0:
        while text[-1] == " ":
            text = text[:-1]

    return text


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = text_factory_custom


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/suppliers")
async def suppliers():
    suppliers = app.db_connection.execute('''SELECT SupplierID, CompanyName
                                             FROM Suppliers''').fetchall()
    return [{"SupplierID": row[0], "CompanyName": row[1]} for row in suppliers]


@app.get("/suppliers/{id}")
async def suppliers_id(id: int):
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    suppliers_id = cursor.execute('''SELECT *
                                     FROM Suppliers
                                     WHERE SupplierID = :id''', {"id": id}).fetchone()

    if suppliers_id is None:
        raise HTTPException(status_code=404)
    return suppliers_id


@app.get("/suppliers/{id}/products")
async def suppliers_products(id: int):
    cursor = app.db_connection.cursor()
    suppliers_products = cursor.execute('''SELECT ProductID, ProductName, Discontinued, p.CategoryID, CategoryName
                                          FROM Products AS p
                                          JOIN Categories AS c
                                          ON p.CategoryID = c.CategoryID
                                          WHERE SupplierID = :id
                                          ORDER BY ProductID DESC                    
                                       ''', {"id": id}).fetchall()
    if suppliers_products is None or len(suppliers_products) == 0:
        raise HTTPException(status_code=404)

    return [{"ProductID": row[0], "ProductName": row[1], "Category": {"CategoryID": row[3], "CategoryName": row[4]}, "Discontinued": int(row[2])} for row in suppliers_products]


@app.post("/suppliers", status_code=201)
async def post_suppliers(supplier: Supplier):
    for atribute in supplier.__fields__:
        if atribute == "":
            atribute = None
    app.db_connection.execute('''
                                INSERT INTO Suppliers (CompanyName, ContactName, ContactTitle, Address, City, PostalCode, Country, Phone)
                                VALUES (:CompanyName, :ContactName, :ContactTitle, :Address, :City, :PostalCode, :Country, :Phone)
                                ''', {"CompanyName": supplier.CompanyName, "ContactName": supplier.ContactName, "ContactTitle": supplier.ContactTitle,
                                      "Address": supplier.Address, "City": supplier.City, "PostalCode": supplier.PostalCode, "Country": supplier.Country, "Phone": supplier.Phone})
                        
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    suppliers = cursor.execute('''SELECT *
                                  FROM Suppliers
                                  ORDER BY SupplierID DESC
                                  LIMIT 1''').fetchone()

    suppliers = dict(suppliers)
    for key in suppliers:
        if suppliers[key] == "":
            suppliers[key] = None

    return suppliers
    

@app.put("/suppliers/{id}")
async def put_suppliers(id: int, supplier: SupplierPut):
    supplier = dict(supplier)

    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    if row is None or len(row) == 0:
        raise HTTPException(status_code=404)

    for key in supplier:
        if supplier[key] == "":
            supplier[key] = row[key]
        
    
    supplier["id"] = id
    app.db_connection.execute('''UPDATE Suppliers
                                 SET CompanyName = :CompanyName, ContactName = :ContactName, ContactTitle = :ContactTitle, Address = :Address, City = :City, PostalCode = :PostalCode, Country = :Country, Phone = :Phone
                                 WHERE SupplierID = :id''', supplier)

    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    return row


@app.delete("/suppliers/{id}", status_code=204)
async def delete(id: int):
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    if row is None or len(row) == 0:
        raise HTTPException(status_code=404)

    cursor.execute("DELETE FROM Suppliers WHERE SupplierID = :id", {"id": id})