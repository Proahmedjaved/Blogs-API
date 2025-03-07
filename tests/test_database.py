from app.db.database import get_db

def test_get_db():
    """Test database session management"""
    db_generator = get_db()
    db = next(db_generator)
    assert db is not None
    try:
        next(db_generator)
    except StopIteration:
        pass  # Expected behavior 