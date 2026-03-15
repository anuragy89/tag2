"""
fetch_emoji_ids.py — Run this ONCE to get real custom emoji document IDs.

HOW TO USE:
  1.  heroku run python fetch_emoji_ids.py
      OR locally:  python fetch_emoji_ids.py

  2.  It will print a dict of emoji name → document_id for several
      popular free-to-use Telegram emoji packs.

  3.  Copy the IDs you like into config.py → PREMIUM_EMOJI dict.

  4.  The bot reads those IDs and puts the animated emoji icon on each button.

NOTE: icon_custom_emoji_id on InlineKeyboardButton is a Bot API 9.4 feature.
      It works because your bot owner account has Telegram Premium.
      All users can SEE the animated emoji on buttons — no Premium needed to view.
"""

import asyncio
import os
import sys

from pyrogram import Client
from pyrogram.raw import functions, types

API_ID    = int(os.environ.get("API_ID", 0))
API_HASH  = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ── Popular emoji packs to inspect ───────────────────────────────────────────
# These are well-known public packs. Add any pack short name here.
PACKS_TO_FETCH = [
    "HotCherry",          # 🍒 fun colorful emoji
    "AnimatedEmojies",    # Telegram's own animated set
    "EmojiAnimated",      # large animated pack
    "UtyaAnimated",       # cute duck emoji
]


async def fetch_pack(client: Client, short_name: str) -> dict:
    """Fetch all emoji from a sticker set and return {alt_emoji: document_id}."""
    try:
        result = await client.invoke(
            functions.messages.GetStickerSet(
                stickerset=types.InputStickerSetShortName(short_name=short_name),
                hash=0,
            )
        )
        emojis = {}
        for doc in result.documents:
            for attr in doc.attributes:
                # documentAttributeCustomEmoji has .alt (the base emoji char)
                if hasattr(attr, "alt"):
                    emojis[attr.alt] = doc.id
                elif hasattr(attr, "sticker"):
                    pass   # regular sticker, skip
        return emojis
    except Exception as e:
        print(f"  ⚠️  Could not fetch '{short_name}': {e}")
        return {}


async def main():
    print("=" * 60)
    print("  Telegram Custom Emoji ID Fetcher")
    print("=" * 60)
    print()

    app = Client(
        "emoji_fetcher",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    await app.start()
    print(f"✅ Connected\n")

    all_results = {}

    for pack in PACKS_TO_FETCH:
        print(f"📦 Fetching pack: {pack}")
        emojis = await fetch_pack(app, pack)
        if emojis:
            print(f"   Found {len(emojis)} emoji")
            all_results[pack] = emojis
        print()

    await app.stop()

    # ── Print useful IDs ─────────────────────────────────────────────────────
    print("=" * 60)
    print("  SUGGESTED IDs FOR config.py → PREMIUM_EMOJI")
    print("  Copy the ones you like!")
    print("=" * 60)
    print()

    # Look for specific emoji characters useful for buttons
    WANT = {
        "➕": "add",
        "📋": "help",
        "📢": "updates",
        "💬": "support",
        "🔙": "back",
        "🏷️": "tag",
        "🔥": "fire",
        "⭐": "star",
        "👑": "crown",
        "🚀": "rocket",
        "💎": "diamond",
        "🎯": "target",
        "⚡": "lightning",
        "🎉": "party",
        "❤️": "heart",
    }

    found = {}
    for pack_name, emojis in all_results.items():
        for char, key in WANT.items():
            if char in emojis and key not in found:
                found[key] = (emojis[char], pack_name, char)

    if found:
        print("PREMIUM_EMOJI = {")
        for key, (doc_id, pack, char) in sorted(found.items()):
            print(f'    "{key}": "{doc_id}",   # {char} from {pack}')
        print("}")
    else:
        print("No matching emoji found in those packs.")
        print("Try adding more pack names to PACKS_TO_FETCH above.")

    print()
    print("─" * 60)
    print("Full dump of ALL fetched emoji IDs:")
    print("─" * 60)
    for pack_name, emojis in all_results.items():
        print(f"\n# Pack: {pack_name}")
        for char, doc_id in list(emojis.items())[:30]:   # first 30 per pack
            print(f'  "{char}": "{doc_id}"')


if __name__ == "__main__":
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        print("❌ Set API_ID, API_HASH and BOT_TOKEN env vars first.")
        sys.exit(1)
    asyncio.run(main())
