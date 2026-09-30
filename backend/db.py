"""
Shared SQLAlchemy engine for the FastAPI backend and benchmarks.
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASS',''))}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, pool_pre_ping=True, pool_size=10)