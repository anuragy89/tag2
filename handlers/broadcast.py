"""
handlers/broadcast.py – /broadcast and /stats for the bot owner.

USAGE:
  • Reply to any message (text/photo/video/audio/doc/sticker) with /broadcast
  • OR: /broadcast Your plain text here

FLOW:
  1. Immediately replies "📡 Broadcast Started" with counts
  2. Sends to all GROUPS first
  3. Then sends to all USER DMs
  4. Final report: groups reached / users reached / blocked / failed
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

# Any error meaning "this target will never receive messages"
_SKIP_ERRORS = (
    UserIsBlocked, InputUserDeactivated, PeerIdInvalid,
    ChannelInvalid, ChannelPrivate, ChatWriteForbidden,
    ChatAdminRequired, UserNotParticipant,
)


async def _forward_one(
    client: Client,
    target_id: int,
    source_msg: Message,   # the actual content message to copy
    plain_text: str,       # used only if source_msg is None
) -> str:
    """Send one broadcast to target_id. Returns 'ok', 'blocked', or 'failed'."""
    for attempt in range(3):
        try:
            if source_msg is not None:
                # copy() sends the message as-is: photo, video, audio, text, sticker…
                await source_msg.copy(target_id)
            else:
                await client.send_message(
                    target_id,
                    f"📢 **Broadcast from Bot Owner:**\n\n{plain_text}",
                )
            return "ok"

        except FloodWait as e:
            log.warning("FloodWait %ds → %s", e.value, target_id)
            await asyncio.sleep(e.value + 3)
            # loop retries

        except _SKIP_ERRORS:
            return "blocked"

        except RPCError as e:
            log.warning("RPCError %s → %s", e, target_id)
            if attempt < 2:
                await asyncio.sleep(2)
            else:
                return "failed"

        except Exception as e:
            log.error("Unexpected %s → %s", e, target_id)
            return "failed"

    return "failed"


@owner_only
async def cmd_broadcast(client: Client, message: Message) -> None:

    # ── Determine what to send ────────────────────────────────────────────────
    raw   = (message.text or "").strip()
    parts = raw.split(maxsplit=1)
    plain_text = parts[1].strip() if len(parts) > 1 else ""

    # source_msg = the message whose content will be copied to every target
    source_msg = message.reply_to_message  # None if not a reply

    if source_msg is None and not plain_text:
        await message.reply_text(
            "📣 **How to use /broadcast:**\n\n"
            "**Text:** `/broadcast Hello everyone!`\n\n"
            "**Any media:** Reply to a photo/video/audio/doc/sticker with `/broadcast`\n\n"
            "_Groups receive it first, then user DMs._"
        )
        return

    # ── Detect content type label ─────────────────────────────────────────────
    if source_msg:
        if source_msg.photo:        ctype = "photo 📷"
        elif source_msg.video:      ctype = "video 🎬"
        elif source_msg.audio:      ctype = "audio 🎵"
        elif source_msg.voice:      ctype = "voice 🎤"
        elif source_msg.document:   ctype = "document 📄"
        elif source_msg.sticker:    ctype = "sticker 🎭"
        elif source_msg.animation:  ctype = "GIF 🎞️"
        else:                       ctype = "text 📝"
    else:
        ctype = "text 📝"

    # ── Fetch targets ─────────────────────────────────────────────────────────
    chat_ids = await get_all_chat_ids()
    user_ids = await get_all_user_ids()
    total_g  = len(chat_ids)
    total_u  = len(user_ids)
    total    = total_g + total_u

    # ── Immediate "started" reply ─────────────────────────────────────────────
    status_msg = await message.reply_text(
        f"📡 **Broadcast Started!**\n\n"
        f"📦 Type   : `{ctype}`\n"
        f"💬 Groups : `{total_g}`\n"
        f"👥 Users  : `{total_u}`\n"
        f"📊 Total  : `{total}`\n\n"
        f"_Sending to groups first, then user DMs…_"
    )

    # ── Phase 1 — Groups ──────────────────────────────────────────────────────
    g_ok = g_blocked = g_failed = 0

    for i, chat_id in enumerate(chat_ids, start=1):
        res = await _forward_one(client, chat_id, source_msg, plain_text)
        if res == "ok":      g_ok += 1
        elif res == "blocked": g_blocked += 1
        else:                g_failed += 1

        if i % 20 == 0 or i == total_g:
            try:
                await status_msg.edit_text(
                    f"📡 **Broadcasting to Groups…**\n\n"
                    f"💬 Progress : `{i}` / `{total_g}`\n"
                    f"✅ Sent     : `{g_ok}`\n"
                    f"🚫 Blocked  : `{g_blocked}`\n"
                    f"❌ Failed   : `{g_failed}`\n\n"
                    f"_Users DM starts after groups…_"
                )
            except Exception:
                pass

        await asyncio.sleep(0.3)

    # ── Phase 2 — User DMs ────────────────────────────────────────────────────
    u_ok = u_blocked = u_failed = 0

    for i, user_id in enumerate(user_ids, start=1):
        res = await _forward_one(client, user_id, source_msg, plain_text)
        if res == "ok":      u_ok += 1
        elif res == "blocked": u_blocked += 1
        else:                u_failed += 1

        if i % 20 == 0 or i == total_u:
            try:
                await status_msg.edit_text(
                    f"📡 **Broadcasting to Users…**\n\n"
                    f"✅ Groups done : `{g_ok}` / `{total_g}`\n\n"
                    f"👥 Users : `{i}` / `{total_u}`\n"
                    f"✅ Sent    : `{u_ok}`\n"
                    f"🚫 Blocked : `{u_blocked}`\n"
                    f"❌ Failed  : `{u_failed}`"
                )
            except Exception:
                pass

        await asyncio.sleep(0.3)

    # ── Final report ──────────────────────────────────────────────────────────
    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 **Groups**\n"
        f"  ├ ✅ Delivered : `{g_ok}` / `{total_g}`\n"
        f"  ├ 🚫 Blocked  : `{g_blocked}`\n"
        f"  └ ❌ Failed   : `{g_failed}`\n\n"
        f"👥 **Users (DM)**\n"
        f"  ├ ✅ Delivered : `{u_ok}` / `{total_u}`\n"
        f"  ├ 🚫 Blocked  : `{u_blocked}`\n"
        f"  └ ❌ Failed   : `{u_failed}`\n\n"
        f"📊 **Total Delivered : `{g_ok + u_ok}` / `{total}`**\n"
        f"📦 Type : `{ctype}`"
    )


# ── /stats ────────────────────────────────────────────────────────────────────

@owner_only
async def cmd_stats(client: Client, message: Message) -> None:
    total_users  = await count_users()
    total_groups = await count_groups()
    active_tags  = sum(
        1 for cid in list(tag_manager._sessions)
        if tag_manager.is_active(cid)
    )
    await message.reply_text(
        f"📊 **Tag Master Bot — Statistics**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 **Total Users  :** `{total_users}`\n"
        f"💬 **Total Groups :** `{total_groups}`\n"
        f"⚡ **Active Tags  :** `{active_tags}`\n\n"
        f"🗄️ **Database :** MongoDB\n"
        f"🤖 _Tag Master Bot — Online & Running!_ 🚀"
    )
