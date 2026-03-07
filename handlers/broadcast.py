"""
handlers/broadcast.py – /broadcast and /stats for the bot owner only.
"""

import asyncio
import logging

from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    RPCError,
    UserIsBlocked,
)
from pyrogram.types import Message

from database import get_all_user_ids, get_all_chat_ids, count_users, count_groups
from utils import owner_only
from utils.tag_manager import tag_manager

log = logging.getLogger(__name__)


@owner_only
async def cmd_broadcast(client: Client, message: Message) -> None:
    """
    Usage: /broadcast Your message here
    Sends the message to all tracked users and groups.
    """
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply_text(
            "📣 **Broadcast Usage:**\n\n"
            "`/broadcast Your message here`\n\n"
            "_Supports Markdown formatting._",
            parse_mode="markdown",
        )
        return

    bc_text = parts[1].strip()

    status_msg = await message.reply_text(
        "📡 **Broadcast starting…**\nFetching recipients — please wait.",
        parse_mode="markdown",
    )

    user_ids  = await get_all_user_ids()
    chat_ids  = await get_all_chat_ids()

    total   = len(user_ids) + len(chat_ids)
    success = failed = blocked = 0

    full_text = f"📢 **Message from Bot Owner:**\n\n{bc_text}"

    all_targets = [(uid, "user") for uid in user_ids] + [(cid, "group") for cid in chat_ids]

    for idx, (target_id, kind) in enumerate(all_targets, start=1):
        try:
            await client.send_message(target_id, full_text, parse_mode="markdown")
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 3)
            try:
                await client.send_message(target_id, full_text, parse_mode="markdown")
                success += 1
            except Exception:
                failed += 1
        except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
            blocked += 1
        except RPCError:
            failed += 1

        # Update status every 50 sends
        if idx % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📡 **Broadcasting…**\n\n"
                    f"Progress : `{idx}` / `{total}`\n"
                    f"✅ Sent: `{success}` | ❌ Failed: `{failed}` | 🚫 Blocked: `{blocked}`",
                    parse_mode="markdown",
                )
            except Exception:
                pass

        await asyncio.sleep(0.05)   # gentle rate limiting

    report = (
        f"✅ **Broadcast Complete!**\n\n"
        f"📊 **Results:**\n"
        f"  ├ ✅ Delivered : `{success}`\n"
        f"  ├ ❌ Failed    : `{failed}`\n"
        f"  └ 🚫 Blocked   : `{blocked}`\n\n"
        f"📦 Total targets: `{total}` "
        f"(`{len(user_ids)}` users · `{len(chat_ids)}` groups)"
    )
    await status_msg.edit_text(report, parse_mode="markdown")


@owner_only
async def cmd_stats(client: Client, message: Message) -> None:
    """Display bot usage statistics."""
    total_users  = await count_users()
    total_groups = await count_groups()

    # Count active tagging sessions
    active_sessions = sum(
        1 for cid in list(tag_manager._sessions)
        if tag_manager.is_active(cid)
    )

    await message.reply_text(
        f"📊 **Tag Master Bot — Statistics**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 **Total Users :**   `{total_users}`\n"
        f"💬 **Total Groups :**  `{total_groups}`\n"
        f"⚡ **Active Tags :**   `{active_sessions}`\n\n"
        f"🗄️ **Database :** MongoDB\n"
        f"🤖 _Tag Master Bot – Online & Running!_ 🚀",
        parse_mode="markdown",
    )
