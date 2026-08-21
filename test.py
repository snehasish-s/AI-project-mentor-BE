import pyodbc

server = r"DESKTOP-9P1IGU0\SQLEXPRESS"   # Change if your server name is different
database = "AIProjectMentor"

try:
    connection = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )

    print("✅ SQL Server connection successful!")

    cursor = connection.cursor()
    cursor.execute("SELECT @@VERSION")

    row = cursor.fetchone()
    print("\nSQL Server Version:")
    print(row[0])

    connection.close()
    print("\nConnection closed.")

except pyodbc.Error as e:
    print("❌ Connection failed!")
    print(e)