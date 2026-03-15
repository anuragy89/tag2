"""
handlers/broadcast.py – /broadcast and /stats with premium emoji HTML messages.
"""

import asyncio
import logging

from pyrogram import Client
from pyrogram.errors import (
    ChannelInvalid, ChannelPrivate, ChatAdminRequired,
    ChatWriteForbidden, FloodWait, InputUserDeactivated,
    PeerIdInvalid, RPCError, UserIsBlocked, UserNotParticipant,
)
from pyrogram.types import Message

from database import get_all_user_ids, get_all_chat_ids, count_users, count_groups
from utils import owner_only
from utils.tag_manager import tag_manager
from utils.botapi import reply_html, send_html, te

log = logging.getLogger(__name__)

_SKIP_ERRORS = (
    UserIsBlocked, InputUserDeactivated, PeerIdInvalid,
    ChannelInvalid, ChannelPrivate, ChatWriteForbidden,
    ChatAdminRequired, UserNotParticipant,
)


async def _forward_one(client, target_id, source_msg, plain_text) -> str:
    for attempt in range(3):
        try:
            if source_msg is not None:
                await source_msg.copy(target_id)
            else:
                await client.send_message(
                    target_id,
                    f"📢 **Broadcast from Bot Owner:**\n\n{plain_text}",
                )
            return "ok"
        except FloodWait as e:
            await asyncio.sleep(e.value + 3)
        except _SKIP_ERRORS:
            return "blocked"
        except RPCError as e:
            if attempt < 2:
                await asyncio.sleep(2)
            else:
                return "failed"
        except Exception:
            return "failed"
    return "failed"


@owner_only
async def cmd_broadcast(client: Client, message: Message) -> None:
    raw   = (message.text or "").strip()
    parts = raw.split(maxsplit=1)
    plain_text = parts[1].strip() if len(parts) > 1 else ""
    source_msg = message.reply_to_message

    if source_msg is None and not plain_text:
        text = (
            f"{te('bell','🔔')} <b>How to use /broadcast:</b>\n\n"
            f"<b>Text:</b> <code>/broadcast Hello everyone!</code>\n\n"
            f"<b>Any media:</b> Reply to a photo/video/audio/doc/sticker "
            f"with <code>/broadcast</code>\n\n"
            f"<i>Groups receive it first, then user DMs.</i>"
        )
        result = await reply_html(message.chat.id, message.id, text)
        if not result:
            await message.reply_text(text)
        return

    if source_msg:
        m = source_msg
        if m.photo:        ctype = f"photo 📷"
        elif m.video:      ctype = f"video 🎬"
        elif m.audio:      ctype = f"audio 🎵"
        elif m.voice:      ctype = f"voice 🎤"
        elif m.document:   ctype = f"document 📄"
        elif m.sticker:    ctype = f"sticker 🎭"
        elif m.animation:  ctype = f"GIF 🎞️"
        else:              ctype = f"text 📝"
    else:
        ctype = "text 📝"

    chat_ids = await get_all_chat_ids()
    user_ids = await get_all_user_ids()
    total_g, total_u = len(chat_ids), len(user_ids)

    start_text = (
        f"{te('broadcast','📡')} <b>Broadcast Started!</b>\n\n"
        f"📦 Type   : <code>{ctype}</code>\n"
        f"{te('chat','💬')} Groups : <code>{total_g}</code>\n"
        f"{te('people','👥')} Users  : <code>{total_u}</code>\n"
        f"📊 Total  : <code>{total_g + total_u}</code>\n\n"
        f"<i>Sending to groups first, then DMs…</i>"
    )
    result = await reply_html(message.chat.id, message.id, start_text)
    if not result:
        status_msg = await message.reply_text(start_text)
        status_chat_id = None   # can't edit fallback easily
    else:
        status_chat_id = message.chat.id
        status_msg_id  = result["message_id"]

    # ── Phase 1: Groups ───────────────────────────────────────────────────────
    g_ok = g_blocked = g_failed = 0
    for i, chat_id in enumerate(chat_ids, 1):
        res = await _forward_one(client, chat_id, source_msg, plain_text)
        if res == "ok":       g_ok += 1
        elif res == "blocked": g_blocked += 1
        else:                 g_failed += 1

        if (i % 20 == 0 or i == total_g) and status_chat_id:
            update = (
                f"{te('broadcast','📡')} <b>Broadcasting to Groups…</b>\n\n"
                f"{te('chat','💬')} Progress : <code>{i}</code> / <code>{total_g}</code>\n"
                f"{te('check','✅')} Sent     : <code>{g_ok}</code>\n"
                f"🚫 Blocked  : <code>{g_blocked}</code>\n"
                f"{te('cross','❌')} Failed   : <code>{g_failed}</code>\n\n"
                f"<i>User DMs start after groups…</i>"
            )
            await _edit(status_chat_id, status_msg_id, update)
        await asyncio.sleep(0.3)

    # ── Phase 2: User DMs ─────────────────────────────────────────────────────
    u_ok = u_blocked = u_failed = 0
    for i, user_id in enumerate(user_ids, 1):
        res = await _forward_one(client, user_id, source_msg, plain_text)
        if res == "ok":       u_ok += 1
        elif res == "blocked": u_blocked += 1
        else:                 u_failed += 1

        if (i % 20 == 0 or i == total_u) and status_chat_id:
            update = (
                f"{te('broadcast','📡')} <b>Broadcasting to Users…</b>\n\n"
                f"{te('check','✅')} Groups done : <code>{g_ok}</code> / <code>{total_g}</code>\n\n"
                f"{te('people','👥')} Users : <code>{i}</code> / <code>{total_u}</code>\n"
                f"{te('check','✅')} Sent    : <code>{u_ok}</code>\n"
                f"🚫 Blocked : <code>{u_blocked}</code>\n"
                f"{te('cross','❌')} Failed  : <code>{u_failed}</code>"
            )
            await _edit(status_chat_id, status_msg_id, update)
        await asyncio.sleep(0.3)

    # ── Final report ──────────────────────────────────────────────────────────
    report = (
        f"{te('check','✅')} <b>Broadcast Complete!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{te('chat','💬')} <b>Groups</b>\n"
        f"  ├ {te('check','✅')} Delivered : <code>{g_ok}</code> / <code>{total_g}</code>\n"
        f"  ├ 🚫 Blocked  : <code>{g_blocked}</code>\n"
        f"  └ {te('cross','❌')} Failed   : <code>{g_failed}</code>\n\n"
        f"{te('people','👥')} <b>Users (DM)</b>\n"
        f"  ├ {te('check','✅')} Delivered : <code>{u_ok}</code> / <code>{total_u}</code>\n"
        f"  ├ 🚫 Blocked  : <code>{u_blocked}</code>\n"
        f"  └ {te('cross','❌')} Failed   : <code>{u_failed}</code>\n\n"
        f"📊 <b>Total Delivered : <code>{g_ok+u_ok}</code> / <code>{total_g+total_u}</code></b>\n"
        f"📦 Type : <code>{ctype}</code>"
    )
    if status_chat_id:
        await _edit(status_chat_id, status_msg_id, report)
    else:
        await send_html(message.chat.id, report)


async def _edit(chat_id: int, message_id: int, text: str):
    """Edit a message via Bot API HTTP (HTML)."""
    from utils.botapi import _call
    await _call("editMessageText", {
        "chat_id": chat_id, "message_id": message_id,
        "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })


@owner_only
async def cmd_stats(client: Client, message: Message) -> None:
    total_users  = await count_users()
    total_groups = await count_groups()
    active_tags  = sum(
        1 for cid in list(tag_manager._sessions)
        if tag_manager.is_active(cid)
    )
    text = (
        f"{te('chart','📊')} <b>Tag Master Bot — Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{te('people','👥')} <b>Total Users  :</b> <code>{total_users}</code>\n"
        f"{te('chat','💬')} <b>Total Groups :</b> <code>{total_groups}</code>\n"
        f"{te('lightning','⚡')} <b>Active Tags  :</b> <code>{active_tags}</code>\n\n"
        f"🗄️ <b>Database :</b> MongoDB\n"
        f"{te('robot','🤖')} <i>Tag Master Bot — Online &amp; Running!</i> {te('rocket','🚀')}"
    )
    result = await reply_html(message.chat.id, message.id, text)
    if not result:
        await message.reply_text(text)
