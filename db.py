import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "forecast"
)
mycursor = db.cursor()

# mycursor.execute("CREATE DATABASE forecast")