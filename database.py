import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


load_dotenv()


db_server = os.getenv("DB_SERVER")
db_name = os.getenv("DB_NAME")
db_driver = os.getenv("DB_DRIVER")


connection_string = (
    f"DRIVER={{{db_driver}}};"
    f"SERVER={db_server};"
    f"DATABASE={db_name};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


database_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": connection_string},
)


engine = create_engine(
    database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    database_session = SessionLocal()

    try:
        yield database_session

    finally:
        database_session.close()


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    DB_NAME() AS database_name,
                    @@SERVERNAME AS server_name,
                    SUSER_SNAME() AS connected_user
                """
            )
        )

        row = result.fetchone()

        print("SQL Server connection successful.")
        print("Database:", row.database_name)
        print("Server:", row.server_name)
        print("Connected user:", row.connected_user)


if __name__ == "__main__":
    test_database_connection()