"""
bot.py – Tag Master Bot entry point.

Registers all handlers using proper imports (no __import__ hacks).
Uses pyrogram.handlers directly.

Required environment variables:
  API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URI

Optional:
  UPDATES_CHANNEL, SUPPORT_GROUP, BOT_USERNAME,
  TAG_DELAY, BATCH_DELAY, FLOOD_SLEEP, USERS_PER_MSG, MONGO_DB_NAME
"""

import asyncio
import logging
import sys

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message

from config import Config
from database import init_db, close_db, upsert_user, upsert_group

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("TagBot")


# ── Validate required config early ───────────────────────────────────────────
def _validate_config() -> None:
    missing = []
    if not Config.API_ID:
        missing.append("API_ID")
    if not Config.API_HASH:
        missing.append("API_HASH")
    if not Config.BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not Config.OWNER_ID:
        missing.append("OWNER_ID")
    if not Config.MONGO_URI:
        missing.append("MONGO_URI")
    if missing:
        log.critical("❌ Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)

_validate_config()


# ── Create Pyrogram client ────────────────────────────────────────────────────
app = Client(
    "tagbot_session",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    sleep_threshold=Config.FLOOD_SLEEP,
)


# ── Import all handlers (after app is created) ────────────────────────────────
from handlers.start    import cmd_start, cmd_help, callback_handler, on_new_chat_member
from handlers.tagging  import (
    cmd_hitag, cmd_entag, cmd_gmtag, cmd_gntag,
    cmd_tagall, cmd_jtag, cmd_admin_tag, cmd_all_tag,
)
from handlers.control   import cmd_stop, cmd_pause, cmd_resume
from handlers.broadcast import cmd_broadcast, cmd_stats


# ══════════════════════════════════════════════════════════════════════════════
#  Register handlers
# ══════════════════════════════════════════════════════════════════════════════

_GRP = filters.group   # shorthand

# /start  (private DM only)
app.add_handler(MessageHandler(cmd_start, filters.command("start") & filters.private))

# /help   (anywhere)
app.add_handler(MessageHandler(cmd_help, filters.command("help")))

# Inline keyboard callbacks
app.add_handler(CallbackQueryHandler(callback_handler))

# Bot added to a group
app.add_handler(MessageHandler(on_new_chat_member, filters.new_chat_members & _GRP))

# ── 6 individual tagging commands (group + admin-only) ──────────────────────
app.add_handler(MessageHandler(cmd_hitag,  filters.command("hitag")  & _GRP))
app.add_handler(MessageHandler(cmd_entag,  filters.command("entag")  & _GRP))
app.add_handler(MessageHandler(cmd_gmtag,  filters.command("gmtag")  & _GRP))
app.add_handler(MessageHandler(cmd_gntag,  filters.command("gntag")  & _GRP))
app.add_handler(MessageHandler(cmd_tagall, filters.command("tagall") & _GRP))
app.add_handler(MessageHandler(cmd_jtag,   filters.command("jtag")   & _GRP))

# /admin  or  @admin  (anyone in group)
app.add_handler(MessageHandler(
    cmd_admin_tag,
    (filters.command("admin") | filters.regex(r"^@admin(\s|$)")) & _GRP,
))

# /all  or  @all  (group admins only – checked inside handler)
app.add_handler(MessageHandler(
    cmd_all_tag,
    (filters.command("all") | filters.regex(r"^@all(\s|$)")) & _GRP,
))

# ── Control commands (group admins only) ─────────────────────────────────────
app.add_handler(MessageHandler(cmd_stop,   filters.command("stop")   & _GRP))
app.add_handler(MessageHandler(cmd_pause,  filters.command("pause")  & _GRP))
app.add_handler(MessageHandler(cmd_resume, filters.command("resume") & _GRP))

# ── Owner commands (work in DM and groups) ────────────────────────────────────
app.add_handler(MessageHandler(cmd_broadcast, filters.command("broadcast")))
app.add_handler(MessageHandler(cmd_stats,     filters.command("stats")))


# ── Passive tracker – silently saves users & groups to MongoDB ────────────────
@app.on_message(filters.group & ~filters.bot)
async def _passive_tracker(client: Client, message: Message) -> None:
    """Track every user/group that interacts with the bot."""
    if message.from_user:
        await upsert_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name,
        )
    if message.chat:
        await upsert_group(
            message.chat.id,
            message.chat.title,
            getattr(message.chat, "username", None),
        )


# ══════════════════════════════════════════════════════════════════════════════
#  Main entry point
# ══════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    await init_db()
    log.info("🚀 Tag Master Bot starting…")

    async with app:
        me = await app.get_me()
        log.info("✅ Logged in as @%s  (ID: %s)", me.username, me.id)
        log.info("🏷️  Bot is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()    # block until SIGTERM / Ctrl+C

    await close_db()
    log.info("👋 Bot stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("⚡ KeyboardInterrupt received – shutting down.")
