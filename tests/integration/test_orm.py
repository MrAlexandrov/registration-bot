"""
Integration tests for ORM implementation.
Tests the database and models work correctly.
"""
import pytest
import tempfile
import os
from src.user_storage import UserStorage


@pytest.fixture(scope="function")
def test_storage():
    """Create a temporary test database for ORM tests."""
    fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)
    
    storage = UserStorage(db_path)
    
    yield storage
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


class TestORMImplementation:
    """Tests for ORM implementation."""

    def test_create_user(self, test_storage):
        """Test creating a new user."""
        test_user_id = 123456789
        
        test_storage.create_user(test_user_id, initial_state="name")
        
        user = test_storage.get_user(test_user_id)
        assert user is not None
        assert user['telegram_id'] == test_user_id
        assert user['state'] == "name"

    def test_create_duplicate_user(self, test_storage):
        """Test that creating duplicate user raises ValueError."""
        test_user_id = 123456789
        
        test_storage.create_user(test_user_id, initial_state="name")
        
        with pytest.raises(ValueError, match="already exists"):
            test_storage.create_user(test_user_id, initial_state="name")

    def test_get_user(self, test_storage):
        """Test getting user data."""
        test_user_id = 123456789
        test_storage.create_user(test_user_id, initial_state="name")
        
        user = test_storage.get_user(test_user_id)
        
        assert user is not None
        assert user['telegram_id'] == test_user_id
        assert user['state'] == "name"

    def test_get_nonexistent_user(self, test_storage):
        """Test getting non-existent user returns None."""
        user = test_storage.get_user(999999999)
        assert user is None

    def test_update_user_field(self, test_storage):
        """Test updating a user field."""
        test_user_id = 123456789
        test_storage.create_user(test_user_id, initial_state="name")
        
        test_storage.update_user(test_user_id, "name", "Иван Иванов")
        
        user = test_storage.get_user(test_user_id)
        assert user['name'] == "Иван Иванов"

    def test_update_state(self, test_storage):
        """Test updating user state."""
        test_user_id = 123456789
        test_storage.create_user(test_user_id, initial_state="name")
        
        test_storage.update_state(test_user_id, "birth_date")
        
        user = test_storage.get_user(test_user_id)
        assert user['state'] == "birth_date"

    def test_get_all_users(self, test_storage):
        """Test getting all users."""
        # Create multiple users
        test_storage.create_user(111111111, initial_state="name")
        test_storage.create_user(222222222, initial_state="phone")
        test_storage.create_user(333333333, initial_state="email")
        
        all_users = test_storage.get_all_users()
        
        assert len(all_users) == 3
        assert 111111111 in all_users
        assert 222222222 in all_users
        assert 333333333 in all_users

    def test_get_users_count(self, test_storage):
        """Test getting users count."""
        # Create multiple users
        test_storage.create_user(111111111, initial_state="name")
        test_storage.create_user(222222222, initial_state="phone")
        
        count = test_storage.get_users_count()
        
        assert count == 2

    def test_get_users_by_state(self, test_storage):
        """Test getting users by state."""
        # Create users with different states
        test_storage.create_user(111111111, initial_state="name")
        test_storage.create_user(222222222, initial_state="birth_date")
        test_storage.create_user(333333333, initial_state="birth_date")
        
        users_in_state = test_storage.get_users_by_state("birth_date")
        
        assert len(users_in_state) == 2
        user_ids = [user['telegram_id'] for user in users_in_state]
        assert 222222222 in user_ids
        assert 333333333 in user_ids

    def test_delete_user(self, test_storage):
        """Test deleting a user."""
        test_user_id = 123456789
        test_storage.create_user(test_user_id, initial_state="name")
        
        deleted = test_storage.delete_user(test_user_id)
        
        assert deleted is True
        user = test_storage.get_user(test_user_id)
        assert user is None

    def test_delete_nonexistent_user(self, test_storage):
        """Test deleting non-existent user returns False."""
        deleted = test_storage.delete_user(999999999)
        assert deleted is False

    def test_update_nonexistent_user(self, test_storage):
        """Test updating non-existent user raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            test_storage.update_user(999999999, "name", "Test")