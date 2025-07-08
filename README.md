
# Echoes of Aether: The Silent War

> A strategic, emotional social deduction game played entirely within Telegram group chats via a bot.

---

## 🧩 Game Overview

**Echoes of Aether** blends role-based mechanics, secret powers, and emotionally-driven storytelling into a rich multiplayer game experience. Up to 15 players engage in factions, form alliances, complete secret tasks, and attempt to outmaneuver one another to win.

- **Platform:** Telegram Group Chats
- **Genre:** Social Deduction / RPG / Interactive Story
- **Modes:** Group Game, Story Tasks, Item Mechanics

---

## 🔥 Gameplay Cycle

```
Setup → Day Phase → Night Phase → Dawn → Win Check → Repeat/End
```

- **Day Phase:** Vote, Discuss, Accuse
- **Night Phase:** Use powers, items, complete secret tasks
- **Dawn:** Story updates, results, emotional turns
- **Plot Twists:** Can randomly alter game flow (every 2–3 rounds)

---

## 🧙 Roles & Factions

### 🌂 Veilborn (Corruptors)
- Shadeblade – Assassinate
- Whispersmith – Forge messages
- Blight Whisperer – Change loyalties
- Succubus – Disable voting

### 🌞 Luminae (Purifiers)
- Oracle – Reveal faction
- Lumen Priest – Cleanse
- Light Herald – Send disguised message
- Ascended – Override vote (late game)

### ⚙️ Nexus Guild (Controllers)
- Tinkerer – View inventory
- Saboteur – Cancel action
- Courtesan – Seduce/block vote
- Archivist – Win by collecting relics

### 🌀 Rogues (Neutrals)
- Trickster – Swap roles
- Puppetmaster – Override vote
- Goat – Win by surviving to final 3

---

## 📦 Bot Commands

| Command | Description |
|--------|-------------|
| /startgame | Start new match |
| /join | Join lobby |
| /vote @user | Vote to eliminate |
| /flee | Leave game |
| /extendtime | Extend join timer |
| /cancelgame | Cancel current match |
| /mytasks | View your secret quests |
| /complete_task CODE | Submit task |
| /abandon_task | Give up current task |
| /usepower @user | Use your role power |
| /useitem ITEM | Use item from inventory |

---

## 🧠 Emotional Engine

Each bot story message is crafted to reflect:
- Hope, Betrayal, Mystery, Longing, Dread
- Story-based item drops, tasks, or events

---

## 🚀 Setup & Deployment

1. Clone the repo
2. Install dependencies (Python + `python-telegram-bot`)
3. Set environment:
    - `TOKEN=your_bot_token`
    - `APP_URL=https://yourdomain.com`
4. Run with:
```bash
python bot.py
```

Ensure Flask `server.py` is running for webhook support.

---

## 📜 License & Credits

Created by a passionate team of narrative and game design fans.
Powered by open-source tools and Telegram.

