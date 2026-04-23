import sqlite3
conn = sqlite3.connect("test.db")
cur = conn.cursor()

createtable = """
Create TABLE IF NOT EXISTS students(
    id int PRIMARY KEY,
    name varchar(25),
    rollnumber varchar(10),
    score int
)
"""
cur.execute(createtable)

# id, name, rollnumber, score
values = [(1, 'Sumit', 'CS-23411584', 1000), (2, 'Aman', 'CS-2341158', 700)]

for v in values:
    cur.execute("INSERT OR IGNORE INTO students VALUES ( ?, ?, ?, ? )", v)

conn.commit()

q = "SELECT * FROM students"
cur.execute(q)

for row in cur.fetchall():
    print(row)

conn.close()
