# 🏷️ Tag Master Bot

> The most powerful Telegram tagging bot — **8 tag styles**, flood protection, admin controls, and one-click Heroku deploy.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🇮🇳 **Hindi Tag** | `/hitag` – Funny + flirty Hindi messages |
| 🇬🇧 **English Tag** | `/entag` – Funny + flirty English messages |
| 🌅 **Good Morning** | `/gmtag` – Hinglish GM messages |
| 🌙 **Good Night** | `/gntag` – Hinglish GN messages |
| 🔥 **General Tag** | `/tagall` – Hinglish mix of meme, flirt, normal |
| 😂 **Joke Tag** | `/jtag` – Hinglish jokes |
| 📢 **Admin Tag** | `/admin` or `@admin` – Tag only admins (6/msg) |
| 📣 **All Tag** | `/all` or `@all` – Tag everyone (6/msg) |
| ⏸️ **Pause / Resume** | `/pause` · `/resume` |
| 🛑 **Stop** | `/stop` |
| 📡 **Broadcast** | `/broadcast` (owner only) |
| 📊 **Stats** | `/stats` (owner only) |
| 🛡️ **Flood Guard** | Auto-sleeps on FloodWait |
| 💬 **Inline UI** | Beautiful start screen with buttons |

---

## 🚀 Quick Deploy to Heroku

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/tagbot)

**Manual steps:**

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/tagbot
cd tagbot

# 2. Login to Heroku
heroku login
heroku create your-tagbot-name

# 3. Set environment variables
heroku config:set API_ID=12345678
heroku config:set API_HASH=abcdef1234567890
heroku config:set BOT_TOKEN=123456:YourToken
heroku config:set OWNER_ID=123456789
heroku config:set BOT_USERNAME=YourTagBot
heroku config:set UPDATES_CHANNEL=https://t.me/yourchannel

# 4. Deploy
git push heroku main

# 5. Start the worker dyno
heroku ps:scale worker=1
```

---

## 🔧 Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in credentials
cp .env.example .env
nano .env

# Run
python bot.py
```

---

## 📋 All Commands

### 🏷️ Tagging (Admins only)

| Command | Description |
|---|---|
| `/hitag` | Tag all members – Hindi messages |
| `/entag` | Tag all members – English messages |
| `/gmtag` | Good Morning tag – Hinglish |
| `/gntag` | Good Night tag – Hinglish |
| `/tagall` | General tag – Hinglish mix |
| `/jtag` | Joke tag – Hinglish |

### 🎯 Mention Commands

| Command | Who Can Use | Description |
|---|---|---|
| `/admin` or `@admin` | Everyone | Tag only admins (6/msg) |
| `/admin <msg>` | Everyone | Tag admins with custom message |
| `/all` or `@all` | Admins | Tag everyone (6/msg) |
| `/all <msg>` | Admins | Tag everyone with custom message |

### ⏸️ Control (Admins only)

| Command | Description |
|---|---|
| `/stop` | Stop current tagging completely |
| `/pause` | Pause tagging (resumes from same point) |
| `/resume` | Resume paused tagging |

### 👑 Owner Only

| Command | Description |
|---|---|
| `/broadcast <msg>` | Send message to all users & groups |
| `/stats` | Bot usage statistics |

---

## ➕ Adding New Message Templates

Open `utils/messages.py` and append to the relevant list:

```python
# Example: add a new Hindi message
HITAG_MSGS.append("अरे {mention}! नया message! 😄")

# Example: add a new Joke tag
JTAG_MSGS.append("{mention} 😂 New joke here!")
```

The `{mention}` placeholder is replaced automatically with the tagged user's name.

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `API_ID` | ✅ | — | Telegram API ID |
| `API_HASH` | ✅ | — | Telegram API Hash |
| `BOT_TOKEN` | ✅ | — | Bot token from @BotFather |
| `OWNER_ID` | ✅ | — | Your Telegram user ID |
| `UPDATES_CHANNEL` | ❌ | — | Link to updates channel |
| `SUPPORT_GROUP` | ❌ | — | Link to support group |
| `BOT_USERNAME` | ❌ | — | Bot username (no @) |
| `TAG_DELAY` | ❌ | `1.5` | Seconds between each tag |
| `BATCH_DELAY` | ❌ | `3.0` | Seconds between 6-user batches |
| `FLOOD_SLEEP` | ❌ | `60` | Max FloodWait sleep seconds |
| `USERS_PER_MSG` | ❌ | `6` | Mentions per message (/all, /admin) |

---

## 📁 Project Structure

```
tagbot/
├── bot.py               # Main entry point + handler registration
├── config.py            # All configuration via env vars
├── database.py          # Async SQLite database layer
├── requirements.txt
├── Procfile             # Heroku worker definition
├── runtime.txt          # Python 3.11
├── app.json             # Heroku one-click deploy config
├── .env.example         # Template for local .env
├── handlers/
│   ├── __init__.py
│   ├── start.py         # /start, /help, inline buttons, group join
│   ├── tagging.py       # All 8 tag command handlers
│   ├── control.py       # /stop, /pause, /resume
│   └── broadcast.py     # /broadcast, /stats
└── utils/
    ├── __init__.py
    ├── messages.py      # 150+ message templates, easily extensible
    ├── helpers.py       # safe_send, admin_only, owner_only decorators
    └── tag_manager.py   # Per-group tag session state machine
```

---

## 🛡️ Spam & Flood Protection

- **FloodWait**: Caught at every send and retried after the required sleep
- **TAG_DELAY**: Configurable pause between each tag message
- **BATCH_DELAY**: Longer pause between 6-user batches  
- **sleep_threshold**: Pyrogram auto-sleeps on minor floods
- **Retry logic**: Up to 4 retries per message before skipping

---

## 📄 License

MIT License – free to use, modify, and deploy.

---

Made with ❤️ using [Kurigram](https://github.com/KurimuzonAkuma/pyrogram) + [TgCrypto](https://github.com/pyrogram/tgcrypto)
