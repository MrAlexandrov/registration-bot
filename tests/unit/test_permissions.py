"""
Tests for permission system.
"""

import pytest

from src.database import Database
from src.permissions import Permission, PermissionManager


@pytest.fixture
def test_db():
    """Create a test database."""
    db = Database("data/test_permissions.db")
    yield db
    # Cleanup
    import os

    if os.path.exists("data/test_permissions.db"):
        os.remove("data/test_permissions.db")


@pytest.fixture
def permission_manager(test_db):
    """Create a permission manager with test database."""
    return PermissionManager()


def test_root_user(permission_manager, monkeypatch):
    """Test root user has all permissions."""
    # Mock config.root_id
    from src import config

    monkeypatch.setattr(config.config, "root_id", 12345)

    assert permission_manager.is_root(12345)
    assert not permission_manager.is_root(67890)

    # Root should have all permissions
    assert permission_manager.has_permission(12345, Permission.ADMIN)
    assert permission_manager.has_permission(12345, Permission.TABLE_VIEWER)
    assert permission_manager.has_permission(12345, Permission.MESSAGE_SENDER)
    assert permission_manager.has_permission(12345, Permission.STAFF)


# def test_grant_permission(permission_manager):
#     """Test granting permissions."""
#     user_id = 123456
#     granted_by = 999999

#     # Grant permission
#     result = permission_manager.grant_permission(user_id, Permission.ADMIN, granted_by)
#     assert result is True

#     # Check permission was granted
#     assert permission_manager.has_permission(user_id, Permission.ADMIN)

#     # Granting same permission again should return False
#     result = permission_manager.grant_permission(user_id, Permission.ADMIN, granted_by)
#     assert result is False


def test_revoke_permission(permission_manager):
    """Test revoking permissions."""
    user_id = 123456
    granted_by = 999999

    # Grant permission first
    permission_manager.grant_permission(user_id, Permission.TABLE_VIEWER, granted_by)
    assert permission_manager.has_permission(user_id, Permission.TABLE_VIEWER)

    # Revoke permission
    result = permission_manager.revoke_permission(user_id, Permission.TABLE_VIEWER)
    assert result is True
    assert not permission_manager.has_permission(user_id, Permission.TABLE_VIEWER)

    # Revoking non-existent permission should return False
    result = permission_manager.revoke_permission(user_id, Permission.TABLE_VIEWER)
    assert result is False


def test_get_user_permissions(permission_manager, monkeypatch):
    """Test getting all user permissions."""
    from src import config

    monkeypatch.setattr(config.config, "root_id", 12345)

    user_id = 123456
    granted_by = 999999

    # Grant multiple permissions
    permission_manager.grant_permission(user_id, Permission.ADMIN, granted_by)
    permission_manager.grant_permission(user_id, Permission.TABLE_VIEWER, granted_by)

    # Get permissions
    perms = permission_manager.get_user_permissions(user_id)
    assert Permission.ADMIN.value in perms
    assert Permission.TABLE_VIEWER.value in perms
    assert Permission.MESSAGE_SENDER.value not in perms

    # Root should have all permissions
    root_perms = permission_manager.get_user_permissions(12345)
    assert len(root_perms) == len(Permission)


def test_list_users_with_permission(permission_manager, monkeypatch):
    """Test listing users with specific permission."""
    from src import config

    monkeypatch.setattr(config.config, "root_id", 12345)

    user1 = 111111
    user2 = 222222
    user3 = 333333
    granted_by = 999999

    # Grant permission to multiple users
    permission_manager.grant_permission(user1, Permission.ADMIN, granted_by)
    permission_manager.grant_permission(user2, Permission.ADMIN, granted_by)
    permission_manager.grant_permission(user3, Permission.TABLE_VIEWER, granted_by)

    # List users with ADMIN permission
    admin_users = permission_manager.list_users_with_permission(Permission.ADMIN)
    assert user1 in admin_users
    assert user2 in admin_users
    assert user3 not in admin_users
    assert 12345 in admin_users  # Root should be included

    # List users with TABLE_VIEWER permission
    viewer_users = permission_manager.list_users_with_permission(Permission.TABLE_VIEWER)
    assert user3 in viewer_users
    assert user1 not in viewer_users


# def test_register_chat(permission_manager):
#     """Test registering bot chats."""
#     chat_id = -1001234567890
#     chat_type = "staff"
#     chat_title = "Test Staff Chat"

#     # Register chat
#     result = permission_manager.register_chat(chat_id, chat_type, chat_title)
#     assert result is True

#     # Registering same chat again should return False
#     result = permission_manager.register_chat(chat_id, chat_type, chat_title)
#     assert result is False

#     # Get chat by type
#     found_chat_id = permission_manager.get_chat_by_type(chat_type)
#     assert found_chat_id == chat_id


# def test_get_chat_by_type(permission_manager):
#     """Test getting chat by type."""
#     staff_chat_id = -1001111111111
#     superuser_chat_id = -1002222222222

#     # Register chats
#     permission_manager.register_chat(staff_chat_id, "staff", "Staff Chat")
#     permission_manager.register_chat(superuser_chat_id, "superuser", "Superuser Chat")

#     # Get chats
#     assert permission_manager.get_chat_by_type("staff") == staff_chat_id
#     assert permission_manager.get_chat_by_type("superuser") == superuser_chat_id
#     assert permission_manager.get_chat_by_type("nonexistent") is None


# def test_is_staff_member(permission_manager, monkeypatch):
#     """Test staff member check."""
#     from src import config

#     monkeypatch.setattr(config.config, "root_id", 12345)

#     user_id = 123456
#     granted_by = 999999

#     # User without STAFF permission
#     assert not permission_manager.is_staff_member(user_id)

#     # Grant STAFF permission
#     permission_manager.grant_permission(user_id, Permission.STAFF, granted_by)
#     assert permission_manager.is_staff_member(user_id)

#     # Root should always be staff
#     assert permission_manager.is_staff_member(12345)
