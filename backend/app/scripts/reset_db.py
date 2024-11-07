from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

def reset_database():
    # Create a connection
    with engine.connect() as connection:
        # Drop all tables with CASCADE
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        
        # Commit the transaction
        connection.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    reset_database() 