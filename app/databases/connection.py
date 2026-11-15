import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
url = os.getenv("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL ontbreekt. Vul .env in met jouw bestaande PostgreSQL-verbinding.")
engine = create_engine(url, pool_pre_ping=True)
