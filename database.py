"""
database.py – Async MongoDB layer using Motor.

Collections:
  • users  → tracks every user who starts the bot or messages in a group
  • groups → tracks every group the bot is added to

Motor is the official async MongoDB driver for Python (asyncio-compatible).
Install: pip install motor dnspython
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import motor.motor_asyncio

from config import Config

log = logging.getLogger(__name__)

# ── Module-level client & collection references ───────────────────────────────
_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

users_col:  Optional[motor.motor_asyncio.AsyncIOMotorCollection] = None
groups_col: Optional[motor.motor_asyncio.AsyncIOMotorCollection] = None


# ── Initialise ────────────────────────────────────────────────────────────────

async def _deduplicate(col, key: str) -> None:
    """
    Remove duplicate documents keeping only the most recently inserted one.
    Must run BEFORE creating a unique index on an existing collection.
    """
    pipeline = [
        {"$group": {
            "_id": f"${key}",
            "count": {"$sum": 1},
            "ids":   {"$push": "$_id"},
        }},
        {"$match": {"count": {"$gt": 1}}},
    ]
    async for doc in col.aggregate(pipeline):
        # Keep the last _id, delete all others
        ids_to_delete = doc["ids"][:-1]
        await col.delete_many({"_id": {"$in": ids_to_delete}})
        log.warning("Removed %d duplicate(s) for %s=%s", len(ids_to_delete), key, doc["_id"])


async def init_db() -> None:
    """Connect to MongoDB, deduplicate existing data, and ensure indexes exist."""
    global _client, _db, users_col, groups_col

    _client = motor.motor_asyncio.AsyncIOMotorClient(
        Config.MONGO_URI,
        serverSelectionTimeoutMS=10_000,
    )
    _db = _client[Config.MONGO_DB_NAME]

    users_col  = _db["users"]
    groups_col = _db["groups"]

    # Verify connection is alive first
    await _client.admin.command("ping")
    log.info("✅ MongoDB connected  –  db: %s", Config.MONGO_DB_NAME)

    # Step 1: Remove any existing duplicates BEFORE creating unique indexes.
    # This handles the case where the bot was previously run without unique indexes.
    await _deduplicate(users_col,  "user_id")
    await _deduplicate(groups_col, "chat_id")

    # Step 2: Create unique indexes. Using try/except so a pre-existing
    # valid unique index (already built) doesn't crash startup.
    try:
        await users_col.create_index(
            "user_id", unique=True, background=False
        )
        log.info("✅ Index ensured: users.user_id (unique)")
    except Exception as e:
        log.warning("users.user_id index: %s", e)

    try:
        await groups_col.create_index(
            "chat_id", unique=True, background=False
        )
        log.info("✅ Index ensured: groups.chat_id (unique)")
    except Exception as e:
        log.warning("groups.chat_id index: %s", e)


async def close_db() -> None:
    """Close the MongoDB connection gracefully."""
    if _client is not None:
        _client.close()
        log.info("🔒 MongoDB connection closed.")


# ══════════════════════════════════════════════════════════════════════════════
#  Users
# ══════════════════════════════════════════════════════════════════════════════

async def upsert_user(
    user_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
) -> None:
    """Insert or update a user document."""
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username":  username,
                "full_name": full_name,
                "updated_at": datetime.now(timezone.utc),
            },
            "$setOnInsert": {
                "user_id":   user_id,
                "joined_at": datetime.now(timezone.utc),
            },
        },
        upsert=True,
    )


async def get_all_user_ids() -> List[int]:
    """Return a list of all tracked user IDs."""
    cursor = users_col.find({}, {"user_id": 1, "_id": 0})
    return [doc["user_id"] async for doc in cursor]


async def count_users() -> int:
    """Return total number of tracked users."""
    return await users_col.count_documents({})


# ══════════════════════════════════════════════════════════════════════════════
#  Groups
# ══════════════════════════════════════════════════════════════════════════════

async def upsert_group(
    chat_id: int,
    title: Optional[str] = None,
    username: Optional[str] = None,
    member_count: int = 0,
) -> None:
    """Insert or update a group document."""
    await groups_col.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "title":        title,
                "username":     username,
                "member_count": member_count,
                "updated_at":   datetime.now(timezone.utc),
            },
            "$setOnInsert": {
                "chat_id":   chat_id,
                "joined_at": datetime.now(timezone.utc),
            },
        },
        upsert=True,
    )


async def remove_group(chat_id: int) -> None:
    """Remove a group from the database (bot was kicked)."""
    await groups_col.delete_one({"chat_id": chat_id})


async def get_all_chat_ids() -> List[int]:
    """Return a list of all tracked group chat IDs."""
    cursor = groups_col.find({}, {"chat_id": 1, "_id": 0})
    return [doc["chat_id"] async for doc in cursor]


async def count_groups() -> int:
    """Return total number of tracked groups."""
    return await groups_col.count_documents({})
