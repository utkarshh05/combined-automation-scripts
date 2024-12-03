#mh_database_module

import logging
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from typing import Tuple
from config import DATABASE_URL
from mh_automation.mh_config import configure_logging

# Initialize logging
logger = configure_logging()


def setup_maharashtra_db_connection() -> Tuple[sessionmaker, Table]:
    """
    Set up database connection for the Maharashtra website.
    
    Returns:
        Tuple[sessionmaker, Table]: A tuple containing the session factory and mh_website_credentials table.
    """
    engine = create_engine(DATABASE_URL)
    try:
        Session = sessionmaker(bind=engine)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        mh_table = Table('mh_website_credentials', metadata, autoload_with=engine)
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    return Session, mh_table

def get_credentials_by_id(session, mh_table, id: int) -> dict:
    """
    Retrieve a specific login credential by ID from the database.
    
    Args:
        session: Database session object.
        mh_table: Table name or query object.
        id (int): The ID of the record to retrieve.
    
    Returns:
        dict: A dictionary containing login credentials.
    """
    record = session.query(mh_table).filter_by(id=id).first()
    if record:
        return {'id': record.id, 'login_name': record.login_name, 'password': record.password}
    return None
