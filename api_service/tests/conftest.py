import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.main import app
from app.database.postgres import Base, engine

# Important models to import so that they are registered in the metadata
from app.database.models import Claim

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def db_engine():
    print("Setting up: Creating all tables")
    Base.metadata.create_all(bind=engine)
    print(f"All tables: {Base.metadata.tables.values()}")
    
    try:
        with TestingSessionLocal() as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
        print(f"Tearing down: Dropping all tables.")
        
@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()