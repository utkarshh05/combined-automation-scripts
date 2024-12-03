import logging
from typing import List
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from sqlalchemy.engine import Engine
from config import DATABASE_URL

def create_database_engine(database_url: str) -> Engine:
    """
    Create and return a SQLAlchemy engine for the database connection.
    """
    try:
        return create_engine(database_url)
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise

def retrieve_ivrs_numbers(engine: Engine) -> List[str]:
    """
    Retrieve IVRS numbers from the database.
    
    Args:
        engine (Engine): SQLAlchemy engine instance.
    
    Returns:
        List[str]: List of IVRS numbers.
    
    Raises:
        ValueError: If no IVRS numbers are found.
    """
    metadata = MetaData()
    mp_table = Table(
        'mp_website_credentials', metadata,
        Column('id', Integer, primary_key=True),
        Column('ivrs_no', String, nullable=False)
    )

    try:
        with engine.connect() as connection:
            query = select(mp_table.c.ivrs_no)
            results = connection.execute(query).fetchall()
            # Each result is a tuple with a single element, so access the first element
            ivrs_numbers = [result[0] for result in results]
    except Exception as e:
        logging.error(f"Failed to retrieve IVRS numbers: {e}")
        raise
    
    if not ivrs_numbers:
        logging.error("No IVRS numbers found in the database.")
        raise ValueError("No IVRS numbers found")
    
    return ivrs_numbers



