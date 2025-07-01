import sqlite3

# filename to form database
file = "food.db"

try:
  conn = sqlite3.connect(file)
  print("Database food.db formed.")
except:
  print("Database food.db not formed.")



