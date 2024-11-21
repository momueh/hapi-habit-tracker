import pytest
from database import setup_test_db, get_db_session

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a clean test database session for each test.
    Tables are created but empty - each testcase should create its own data.
    """
    setup_test_db()
    session = get_db_session(test=True)
    yield session
    session.close()