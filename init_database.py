import sqlite3

DATABASE = "data/company.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

with open("data/schema.sql", "r") as file:
    cursor.executescript(file.read())

with open("data/sample_data.sql", "r") as file:
    cursor.executescript(file.read())

connection.commit()
connection.close()

print("Database created successfully!")