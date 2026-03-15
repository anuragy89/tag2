"""
config.py – All bot configuration loaded from environment variables.
"""

import os


class Config:
    # ── Core Telegram Credentials ─────────────────────────────────────────────
    API_ID    = int(os.environ.get("API_ID", 0))
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # ── Owner ─────────────────────────────────────────────────────────────────
    OWNER_ID  = int(os.environ.get("OWNER_ID", 0))

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI     = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "tagbot")

    # ── Tagging Speed / Flood Protection ──────────────────────────────────────
    TAG_DELAY     = float(os.environ.get("TAG_DELAY",   1.5))
    BATCH_DELAY   = float(os.environ.get("BATCH_DELAY", 3.0))
    FLOOD_SLEEP   = int(os.environ.get("FLOOD_SLEEP",   60))
    USERS_PER_MSG = int(os.environ.get("USERS_PER_MSG", 6))

    # ── Bot Links ─────────────────────────────────────────────────────────────
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "https://t.me/yourchannel")
    SUPPORT_GROUP   = os.environ.get("SUPPORT_GROUP",   "https://t.me/yoursupport")
    BOT_USERNAME    = os.environ.get("BOT_USERNAME",    "YourTagBot")

    # ══════════════════════════════════════════════════════════════════════════
    #  PREMIUM EMOJI IDs
    #  ─────────────────
    #  Run:  heroku run python fetch_emoji_ids.py
    #  Paste the printed document IDs below.  Leave "" to use plain emoji.
    #
    #  HOW IT WORKS:
    #   • Telegram renders  <tg-emoji emoji-id="ID">fallback</tg-emoji>
    #     in HTML parse mode as an animated sticker inline in the text.
    #   • Every user sees it — Premium is only needed on the BOT OWNER account
    #     to SEND them (which your bot does on your behalf).
    #
    #  Keys are used in te() calls throughout handlers and messages.py.
    # ══════════════════════════════════════════════════════════════════════════
    PREMIUM_EMOJI = {

        # ── Inline button icons ───────────────────────────────────────────────
        "add":       "",   # ➕  Add to Your Group  (red button)
        "help":      "",   # 📋  Help & Commands    (blue button)
        "updates":   "",   # 📢  Updates            (blue button)
        "support":   "",   # 💬  Support            (green button)
        "back":      "",   # 🔙  Back               (blue button)

        # ── START / HELP / GROUP JOIN messages ───────────────────────────────
        "tag":       "",   # 🏷️  main bot identity emoji
        "rocket":    "",   # 🚀  launch / live / go
        "star":      "",   # 🌟  features / highlights
        "lightning": "",   # ⚡  controls / speed
        "shield":    "",   # 🛡️  spam protection
        "chart":     "",   # 📊  owner tools / stats
        "wave":      "",   # 👋  hello / welcome
        "robot":     "",   # 🤖  bot identity in group join
        "fire":      "",   # 🔥  hype
        "crown":     "",   # 👑  owner / admin / premium
        "diamond":   "",   # 💎  premium / special
        "sparkle":   "",   # ✨  extra flair
        "target":    "",   # 🎯  mention commands
        "pause":     "",   # ⏸️  control commands
        "bulb":      "",   # 💡  tips section
        "check":     "",   # ✅  success / delivered
        "cross":     "",   # ❌  stop / failed
        "warning":   "",   # ⚠️  admin alert
        "bell":      "",   # 🔔  attention / notification
        "trophy":    "",   # 🏆  achievement
        "heart":     "",   # 💖  warm / love
        "zap":       "",   # ⚡  energy (alias fire)
        "tada":      "",   # 🎉  celebration
        "stats":     "",   # 📈  stats / numbers
        "broadcast": "",   # 📡  broadcast
        "people":    "",   # 👥  users
        "chat":      "",   # 💬  groups / chat
        "done":      "",   # 🏁  tagging complete
        "stop":      "",   # 🛑  stopped
        "play":      "",   # ▶️  resumed
        "mic":       "",   # 🎙️  VC / voice
    }
