import sqlite3

dbpath = 'E:\\Creations\\Programming\\WebDev\\MTG Customs\\MTG-Customs\\Organization\\mtgc.db'
conn = sqlite3.connect(dbpath)

def queryDB(query):
    cursor = conn.cursor()

    cursor.execute(query)

while True:
    query = input("Enter Query ('exit' to exit): ")
    if query == "exit":
        break
    
    try:
        queryDB(query)
    except Exception as e:
        print(f"Query Failed\n   {e}")