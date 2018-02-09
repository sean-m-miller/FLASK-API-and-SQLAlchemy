#practice with SQLite
import sqlite3

connection = sqlite3.connect('data.db') # creates data.db file inside current directory, our "database"

cursor = connection.cursor() # responsible for executing queries, and storing result

create_table = "CREATE TABLE users (id int, username text, password text)"
cursor.execute(create_table)

user = (1, 'paul', 'password1')
insert_query = "INSERT INTO users VALUES (?, ?, ?)"
cursor.execute(insert_query, user)

users = [
    (2, 'ben', 'password2'),
    (3, 'john', 'pass3')
]

cursor.executemany(insert_query, users)

select_query = "SELECT * FROM users"
for row in cursor.execute(select_query):
    print(row)

connection.commit()

connection.close()
