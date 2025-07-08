import random
from storage import database as db

def assign_roles(chat_id, player_ids):
    role_pool = [
        "Shadeblade", "Oracle", "Succubus", "Tinkerer",
        "Whispersmith", "Blight Whisperer", "Lumen Priest",
        "Light Herald", "Ascended", "Saboteur", "Courtesan",
        "Archivist", "Puppetmaster", "Trickster", "Goat"
    ]
    random.shuffle(role_pool)
    assigned = {}

    for player_id in player_ids:
        role = role_pool.pop() if role_pool else "Goat"
        db.assign_role(chat_id, player_id, role)
        assigned[player_id] = role

    return assigned

def use_power(user_id, target_username):
    target_username = target_username.replace("@", "")
    target_id = db.get_user_id_by_name(target_username)

    if not target_id:
        return "❌ Target not found."

    user_role = db.get_user_role(user_id)
    if not user_role:
        return "❌ You don't have a role assigned."

    role_actions = {
        "Shadeblade": use_shadeblade,
        "Oracle": use_oracle,
        "Succubus": use_succubus,
        "Tinkerer": use_tinkerer,
        "Whispersmith": use_whispersmith,
        "Blight Whisperer": use_blight,
        "Lumen Priest": use_lumen_priest,
        "Light Herald": use_light_herald,
        "Saboteur": use_saboteur,
        "Courtesan": use_courtesan,
        "Puppetmaster": use_puppetmaster,
        "Trickster": use_trickster,
        "Ascended": use_ascended,
        "Archivist": use_archivist,
        "Goat": use_goat
    }

    power_fn = role_actions.get(user_role)
    if power_fn:
        return power_fn(user_id, target_id, target_username)
    return "❌ Your role has no defined power yet."

# --- Individual Role Powers ---

def use_shadeblade(user_id, target_id, username):
    if db.is_player_protected(target_id):
        return "⚠️ Target was protected!"
    db.mark_player_for_death(target_id)
    return f"🗡 You marked @{username} for death tonight."

def use_oracle(user_id, target_id, username):
    faction = db.get_player_faction(target_id)
    return f"🔮 Oracle's Vision: @{username} is part of *{faction}*."

def use_succubus(user_id, target_id, username):
    db.disable_player_next_vote(target_id)
    return f"💋 @{username} is seduced and can’t vote tomorrow."

def use_tinkerer(user_id, target_id, username):
    inv = db.get_inventory(target_id)
    return f"🧪 @{username}'s inventory: {', '.join(inv) if inv else 'Empty'}"

def use_whispersmith(user_id, target_id, username):
    return "📝 You planted false evidence on @" + username + "."

def use_blight(user_id, target_id, username):
    return f"☣️ You corrupted @{username}'s faction alignment."

def use_lumen_priest(user_id, target_id, username):
    return f"🛐 @{username} was cleansed of any dark influences."

def use_light_herald(user_id, target_id, username):
    return "📜 You sent a public message disguised as another."

def use_saboteur(user_id, target_id, username):
    return f"🧨 @{username}'s next action has been jammed!"

def use_courtesan(user_id, target_id, username):
    db.disable_player_next_vote(target_id)
    return f"💃 @{username} is charmed and can't vote."

def use_puppetmaster(user_id, target_id, username):
    return "🎭 You pulled the strings. A vote will be overridden. (stub)"

def use_trickster(user_id, target_id, username):
    return "🎲 Swapped roles between you and @" + username + " (stub)"

def use_ascended(user_id, target_id, username):
    return "🔥 Prophecy flows through you. Override power unlocked. (stub)"

def use_archivist(user_id, target_id, username):
    count = db.get_relic_count(user_id)
    if count >= 3:
        return "📚 You possess 3 relics! Victory condition met!"
    return f"🪙 You have {count} relic(s). Find more to win."

def use_goat(user_id, target_id, username):
    return "🐐 You are the Goat. Bide your time and survive."