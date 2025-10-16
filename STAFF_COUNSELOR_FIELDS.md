# Staff and Counselor Fields Documentation

## Overview

The bot now supports automatic tracking of staff members (organizers) and counselors through dedicated chat groups. Two new fields have been added to the user database:

- **`is_staff`**: Indicates if a user is a staff member (organizer)
- **`is_counselor`**: Indicates if a user is a counselor

These fields are automatically updated based on chat membership.

## Database Fields

### `is_staff` (INTEGER)
- **Values**: `0` (not staff) or `1` (staff member)
- **Default**: `0`
- **Purpose**: Identifies users who are part of the organizing team
- **Auto-updated**: Yes, based on staff chat membership

### `is_counselor` (INTEGER)
- **Values**: `0` (not counselor) or `1` (counselor)
- **Default**: `0`
- **Purpose**: Identifies users who are counselors
- **Auto-updated**: Yes, based on counselor chat membership

## Setup Instructions

### 1. Register Staff Chat

To designate a chat as the staff chat:

1. Add the bot to your staff group chat
2. Make sure you are the ROOT user (configured in `.env`)
3. Send the command: `/register_staff_chat`
4. **Important**: Send `/sync_staff_chat` to mark all existing members

The bot will confirm registration and automatically track all members of this chat.

### 2. Register Counselor Chat

To designate a chat as the counselor chat:

1. Add the bot to your counselor group chat
2. Make sure you are the ROOT user (configured in `.env`)
3. Send the command: `/register_counselor_chat`
4. **Important**: Send `/sync_counselor_chat` to mark all existing members

The bot will confirm registration and automatically track all members of this chat.

### 3. Sync Existing Members

⚠️ **Important**: When you first register a chat, the bot only tracks NEW events (users joining/leaving). To mark existing members, you MUST run the sync command:

- For staff chat: `/sync_staff_chat`
- For counselor chat: `/sync_counselor_chat`

These commands will:
- Check all users in your database
- Verify if they are members of the registered chat
- Update their `is_staff` or `is_counselor` status accordingly
- Show you how many users were synced

## Automatic Updates

Once chats are registered, the bot automatically:

### When a user joins the staff chat:
- Sets `is_staff = 1` in the database
- Grants `STAFF` permission to the user
- Logs the action

### When a user leaves the staff chat:
- Sets `is_staff = 0` in the database
- Revokes `STAFF` permission from the user
- Logs the action

### When a user joins the counselor chat:
- Sets `is_counselor = 1` in the database
- Logs the action

### When a user leaves the counselor chat:
- Sets `is_counselor = 0` in the database
- Logs the action

## Migration for Existing Databases

If you have an existing database, you need to run the migration script to add the new fields:

```bash
python migrate_add_staff_counselor_fields.py
```

Or specify a custom database path:

```bash
python migrate_add_staff_counselor_fields.py --db-path /path/to/database.sqlite
```

The migration script will:
1. Add `is_staff` and `is_counselor` columns to the users table
2. Set default values to `0` for all existing users
3. Create indexes for efficient querying
4. Verify the changes

## Admin Commands

### Chat Registration (ROOT only)

- `/register_staff_chat` - Register current chat as staff chat
- `/register_counselor_chat` - Register current chat as counselor chat
- `/register_superuser_chat` - Register current chat for error notifications
- `/sync_staff_chat` - Sync all existing staff chat members (mark existing users)
- `/sync_counselor_chat` - Sync all existing counselor chat members (mark existing users)

### Permission Management

- `/grant_permission <user_id> <permission>` - Grant permission to user
- `/revoke_permission <user_id> <permission>` - Revoke permission from user
- `/list_permissions <user_id>` - Show user's permissions
- `/list_users <permission>` - List users with specific permission
- `/my_permissions` - Show your own permissions

## Technical Details

### Database Schema

```sql
-- New fields added to users table
ALTER TABLE users ADD COLUMN is_staff INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN is_counselor INTEGER DEFAULT 0 NOT NULL;

-- Indexes for efficient querying
CREATE INDEX idx_user_is_staff ON users(is_staff);
CREATE INDEX idx_user_is_counselor ON users(is_counselor);
```

### Chat Tracking

The bot uses Telegram's `ChatMemberUpdated` events to track when users join or leave registered chats. This requires:

1. The bot must be an administrator in the chat (or have appropriate permissions)
2. The chat must be registered using the appropriate command
3. The bot must have the `chat_member` update enabled in its configuration

### Files Modified

- **`src/models.py`**: Added `is_staff` and `is_counselor` fields to User model
- **`src/chat_tracker.py`**: Added counselor chat tracking and field updates
- **`src/admin_commands.py`**: Added `/register_counselor_chat` command
- **`migrate_add_staff_counselor_fields.py`**: Migration script for existing databases

## Querying Users

### Get all staff members:
```python
from src.database import db
from src.models import get_user_model

User = get_user_model()

with db.get_session() as session:
    staff_users = session.query(User).filter_by(is_staff=1).all()
    for user in staff_users:
        print(f"Staff: {user.telegram_id}")
```

### Get all counselors:
```python
with db.get_session() as session:
    counselors = session.query(User).filter_by(is_counselor=1).all()
    for user in counselors:
        print(f"Counselor: {user.telegram_id}")
```

### Get users who are both staff and counselors:
```python
with db.get_session() as session:
    both = session.query(User).filter_by(is_staff=1, is_counselor=1).all()
    for user in both:
        print(f"Staff & Counselor: {user.telegram_id}")
```

## Troubleshooting

### Users not being tracked

**Problem**: You registered a chat but existing members are not marked as staff/counselors.

**Solution**: Run the sync command!
- `/sync_staff_chat` for staff chat
- `/sync_counselor_chat` for counselor chat

The bot only tracks NEW events by default. The sync command checks all existing users.

### Other issues

1. **Check bot permissions**: The bot must be an administrator in the chat
2. **Verify chat registration**: Use `/my_permissions` to check if you're ROOT
3. **Check logs**: Look for chat member update events in the bot logs
4. **Verify user exists**: Users must be registered in the bot before their status can be updated
5. **Run sync after registration**: Always run sync commands after registering a new chat

### Migration issues

1. **Backup your database** before running migrations
2. Check that the database file path is correct
3. Ensure the database is not locked by another process
4. Review migration logs for specific errors

### Manual updates

If automatic tracking isn't working, you can manually update fields:

```python
from src.user_storage import user_storage

# Set user as staff
user_storage.update_user(user_id, "is_staff", 1)

# Set user as counselor
user_storage.update_user(user_id, "is_counselor", 1)
```

## Security Notes

- Only ROOT users can register chats
- Chat registration is persistent across bot restarts
- Users automatically lose status when removed from chats
- All status changes are logged for audit purposes

## Future Enhancements

Potential improvements:
- Bulk sync of existing chat members on bot startup
- Manual override commands for special cases
- Export functionality for staff/counselor lists
- Integration with permission system for counselor-specific features