import sqlite3

database = 'food.db'
create_table = 'CREATE TABLE basement_freezer (item Varchar(30), dateofpurchase datetime, weight Varchar(12), amount int); '

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table)   
        conn.commit()
        print("table created")
except sqlite3.OperationalError as e:
    print(e)