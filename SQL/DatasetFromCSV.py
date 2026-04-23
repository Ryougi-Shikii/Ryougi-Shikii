import pandas as pd
import sqlite3

conn = sqlite3.connect("datasets.db")
cur = conn.cursor()

data = pd.read_csv("sql-ultimate-course/datasets/Orders.csv")
CreateOrders = """
    CREATE TABLE IF NOT EXISTS Orders(
            OrderID int NOT NULL PRIMARY KEY,
            ProductID int,
            CustomerID int,
            SalesPersonID int,
            OrderDate date,
            ShipDate date,
            OrderStatus varchar(50),
            ShipAddress varchar(255),
            BillAddress varchar(255),
            Quantity int,
            Sales int,
            CreationTime TIMESTAMP
)"""
cur.execute(CreateOrders)

for _,v in data.iterrows():
    cur.execute("""INSERT INTO Orders
        (OrderID, ProductID, CustomerID, SalesPersonID, OrderDate,
        ShipDate, OrderStatus, ShipAddress, BillAddress, Quantity,
        Sales, CreationTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple(v))

q = "SELECT * FROM Orders"
cur.execute(q)
for row in cur.fetchall():
    print(row)
print()

