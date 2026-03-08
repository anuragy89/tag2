"""
handlers/broadcast.py – /broadcast and /stats for the bot owner.

BROADCAST USAGE:
  Reply to any message (text, photo, video, audio, document, sticker, etc.)
  with /broadcast to forward it to all chats, then all users.

  OR: /broadcast Your plain text here
  (sends as a text message with a header)

FLOW:
  1. Immediately sends "📡 Broadcast Started" with total count
  2. Sends to all GROUPS first
  3. Then sends to all USER DMs
  4. Final report: groups reached / users reached / failed / blocked
"""

import asyncio
import logging

from pyrogram import Client
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    ChatAdminRequired,
    ChatWriteForbidden,
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    RPCError,
    UserIsBlocked,
    UserNotParticipant,
)
from pyrogram.types import Message

from database import get_all_user_ids, get_all_chat_ids, count_users, count_groups
from utils import owner_only
from utils.tag_manager import tag_manager

log = logging.getLogger(__name__)

# Errors that mean "this target can never receive messages" — count as blocked
_BLOCKED_ERRORS = (
    UserIsBlocked, InputUserDeactivated, PeerIdInvalid,
    ChannelInvalid, ChannelPrivate, ChatWriteForbidden,
    ChatAdminRequired, UserNotParticipant,
)


async def _send_one(client: Client, target_id: int, message: Message,
                    bc_text: str) -> str:
    """
    Send one broadcast message to target_id.
    Returns "ok", "blocked", or "failed".
    Uses copy() to preserve any media type.
    Falls back to plain text if no reply message exists.
    """
    for attempt in range(3):
        try:
            if message.reply_to_message:
                # Forward the exact replied-to message (text/photo/video/audio/doc/sticker…)
                await message.reply_to_message.copy(target_id)
            else:
                # Plain text broadcast (/broadcast some text here)
                await client.send_message(
                    target_id,
                    f"📢 **Broadcast from Bot Owner:**\n\n{bc_text}",
                )
            return "ok"

        except FloodWait as e:
            wait = e.value + 3
            log.warning("FloodWait %ds for target %s", wait, target_id)
            await asyncio.sleep(wait)
            # retry after sleep

        except _BLOCKED_ERRORS:
            return "blocked"

        except RPCError as e:
            log.warning("RPCError for %s: %s", target_id, e)
            if attempt < 2:
                await asyncio.sleep(2)
            else:
                return "failed"

        except Exception as e:
            log.error("Unexpected error for %s: %s", target_id, e)
            return "failed"

    return "failed"


@owner_only
async def cmd_broadcast(client: Client, message: Message) -> None:
    # ── Validate input ────────────────────────────────────────────────────────
    raw_text = (message.text or "").strip()
    parts = raw_text.split(maxsplit=1)
    bc_text = parts[1].strip() if len(parts) > 1 else ""

    has_reply   = bool(message.reply_to_message)
    has_text    = bool(bc_text)

    if not has_reply and not has_text:
        await message.reply_text(
            "📣 **How to use /broadcast:**\n\n"
            "**Option 1 — Any media:**\n"
            "Reply to any message (photo, video, audio, text…) with `/broadcast`\n\n"
            "**Option 2 — Plain text:**\n"
            "`/broadcast Your message here`\n\n"
            "_Broadcasts to all groups first, then all user DMs._"
        )
        return

    # ── Fetch all targets ─────────────────────────────────────────────────────
    chat_ids = await get_all_chat_ids()
    user_ids = await get_all_user_ids()

    total_groups = len(chat_ids)
    total_users  = len(user_ids)
    total        = total_groups + total_users

    # ── Immediate "started" confirmation ─────────────────────────────────────
    content_type = "media" if has_reply else "text"
    if has_reply and message.reply_to_message:
        m = message.reply_to_message
        if m.photo:        content_type = "photo 📷"
        elif m.video:      content_type = "video 🎬"
        elif m.audio:      content_type = "audio 🎵"
        elif m.voice:      content_type = "voice 🎤"
        elif m.document:   content_type = "document 📄"
        elif m.sticker:    content_type = "sticker 🎭"
        elif m.animation:  content_type = "GIF 🎞️"
        elif m.text:       content_type = "text 📝"

    status_msg = await message.reply_text(
        f"📡 **Broadcast Started!**\n\n"
        f"📦 Type    : `{content_type}`\n"
        f"💬 Groups  : `{total_groups}`\n"
        f"👥 Users   : `{total_users}`\n"
        f"📊 Total   : `{total}`\n\n"
        f"_Broadcasting to groups first, then DMs…_"
    )

    # ── Phase 1: Groups ───────────────────────────────────────────────────────
    g_ok = g_blocked = g_failed = 0

    for idx, chat_id in enumerate(chat_ids, start=1):
        result = await _send_one(client, chat_id, message, bc_text)
        if result == "ok":       g_ok += 1
        elif result == "blocked": g_blocked += 1
        else:                    g_failed += 1

        # Live update every 20 groups
        if idx % 20 == 0 or idx == total_groups:
            try:
                await status_msg.edit_text(
                    f"📡 **Broadcasting to Groups…**\n\n"
                    f"💬 Groups  : `{idx}` / `{total_groups}`\n"
                    f"✅ Sent    : `{g_ok}`\n"
                    f"🚫 Blocked : `{g_blocked}`\n"
                    f"❌ Failed  : `{g_failed}`\n\n"
                    f"_Users DM will start after groups…_"
                )
            except Exception:
                pass

        await asyncio.sleep(0.3)   # avoid rate limits

    # ── Phase 2: User DMs ─────────────────────────────────────────────────────
    u_ok = u_blocked = u_failed = 0

    for idx, user_id in enumerate(user_ids, start=1):
        result = await _send_one(client, user_id, message, bc_text)
        if result == "ok":       u_ok += 1
        elif result == "blocked": u_blocked += 1
        else:                    u_failed += 1

        # Live update every 20 users
        if idx % 20 == 0 or idx == total_users:
            try:
                await status_msg.edit_text(
                    f"📡 **Broadcasting to Users…**\n\n"
                    f"✅ Groups done : `{g_ok}` / `{total_groups}`\n\n"
                    f"👥 Users   : `{idx}` / `{total_users}`\n"
                    f"✅ Sent    : `{u_ok}`\n"
                    f"🚫 Blocked : `{u_blocked}`\n"
                    f"❌ Failed  : `{u_failed}`"
                )
            except Exception:
                pass

        await asyncio.sleep(0.3)

    # ── Final report ──────────────────────────────────────────────────────────
    total_sent    = g_ok + u_ok
    total_blocked = g_blocked + u_blocked
    total_failed  = g_failed + u_failed

    report = (
        f"✅ **Broadcast Complete!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 **Groups**\n"
        f"  ├ ✅ Delivered : `{g_ok}` / `{total_groups}`\n"
        f"  ├ 🚫 Blocked  : `{g_blocked}`\n"
        f"  └ ❌ Failed   : `{g_failed}`\n\n"
        f"👥 **Users (DM)**\n"
        f"  ├ ✅ Delivered : `{u_ok}` / `{total_users}`\n"
        f"  ├ 🚫 Blocked  : `{u_blocked}`\n"
        f"  └ ❌ Failed   : `{u_failed}`\n\n"
        f"📊 **Total Delivered : `{total_sent}` / `{total}`**\n"
        f"📦 Type : `{content_type}`"
    )

    try:
        await status_msg.edit_text(report)
    except Exception:
        await message.reply_text(report)


# ── /stats ────────────────────────────────────────────────────────────────────

@owner_only
async def cmd_stats(client: Client, message: Message) -> None:
    total_users  = await count_users()
    total_groups = await count_groups()

    active_sessions = sum(
        1 for cid in list(tag_manager._sessions)
        if tag_manager.is_active(cid)
    )

    await message.reply_text(
        f"📊 **Tag Master Bot — Statistics**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 **Total Users  :** `{total_users}`\n"
        f"💬 **Total Groups :** `{total_groups}`\n"
        f"⚡ **Active Tags  :** `{active_sessions}`\n\n"
        f"🗄️ **Database :** MongoDB\n"
        f"🤖 _Tag Master Bot — Online & Running!_ 🚀"
    )
