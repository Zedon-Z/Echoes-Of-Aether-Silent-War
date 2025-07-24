import random
from storage import database as db

def assign_roles(chat_id, player_ids, context):
    role_pool = [
        "Shadeblade", "Oracle", "Succubus", "Tinkerer",
        "Whispersmith", "Blight Whisperer", "Lumen Priest",
        "Light Herald", "Ascended", "Saboteur", "Courtesan",
        "Archivist", "Puppetmaster", "Trickster", "Goat"
    ]
    faction_map = {
    "Shadeblade": "Shadowborn",
    "Oracle": "Seers",
    "Succubus": "Shadowborn",
    "Tinkerer": "Nexus",
    "Whispersmith": "Neutral",
    "Blight": "Shadowborn",
    "Lumen Priest": "Seers",
    "Light Herald": "Seers",
    "Saboteur": "Nexus",
    "Courtesan": "Neutral",
    "Puppetmaster": "Neutral",
    "Trickster": "Neutral",
    "Ascended": "Neutral",
    "Archivist": "Neutral",
    "Goat": "Goat"
    }
    random.shuffle(role_pool)
    assigned = {}

    for player_id in player_ids:
        role = role_pool.pop() if role_pool else "Goat"
        db.assign_role(chat_id, player_id, role)
        assigned[player_id] = role
        db.games[chat_id]["players"][player_id]["faction"] = faction_map.get(role, "Neutral")
        
        faction_map = {
            "Oracle": "Luminae",
            "Lumen Priest": "Luminae",
            "Light Herald": "Luminae",
            "Shadeblade": "Veilborn",
            "Succubus": "Veilborn",
            "Blight Whisperer": "Veilborn",
            "Puppetmaster": "Nexus",
            "Trickster": "Nexus",
            "Saboteur": "Nexus",
            "Ascended": "Rogue",
            "Courtesan": "Rogue",
            "Archivist": "Rogue",
            "Tinkerer": "Rogue",
            "Whispersmith": "Neutral",
            "Goat": "Goat"
            }

        # ✅ Send role to player privately
        role_descriptions = {
            "Oracle": "🔮 See the role of a player.",
            "Succubus": "💘 Charm a player — they cannot vote you.",
            "Shadeblade": "🗡️ Mark one player for elimination.",
            "Puppetmaster": "🧵 Control someone’s vote.",
            "Trickster": "🎭 Swap your vote with another.",
            "Saboteur": "🔧 Disable an item from a player.",
            "Blight Whisperer": "☠️ Curse someone's task.",
            "Tinkerer": "🔨 Craft a random item.",
            "Lumen Priest": "🛡️ Shield someone from elimination.",
            "Light Herald": "🌟 Reveal someone’s alignment.",
            "Ascended": "✨ Become immune to 1 vote.",
            "Courtesan": "💋 Silence someone for 1 round.",
            "Archivist": "📚 Reveal data from last death.",
            "Whispersmith": "💬 Whisper secret messages.",
            "Goat": "🐐 No power, only vibes."
            }
        description = role_descriptions.get(role, "No description available.")

        try:
            context.bot.send_message(
            chat_id=player_id,
            text=(
                f"🎭 Your role is *{role}*.\n"
                f"{description}"
            ),
            parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[WARN] Could not DM {player_id} their role: {e}")
    return assigned
def use_power(user_id, target_username):
    from storage import database as db
    chat_id = db.get_chat_id_by_user(user_id)
    target_username = target_username.replace("@", "")
    target_id = db.get_user_id_by_name(target_username)

    if not target_id:
        return "❌ Target not found."

    user_role = db.get_player_role(chat_id, user_id)
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
    loot_table = ["relic", "truth_crystal", "shadow_ring", "goat_scroll", "core_key"]
    item = random.choice(loot_table)
    inventory = db.get_inventory(user_id)
    inventory[item] = inventory.get(item, 0) + 1
    return f"🛠️ You tinkered and created a '{item}'!"
    
def use_whispersmith(user_id, target_id, username):
    db.enable_whisper(db.get_chat_id_by_user(user_id), user_id, target_id)
    return f"📝 You may now whisper to @{username}."

def use_blight(user_id, target_id, username):
    db.curse_alignment(db.get_chat_id_by_user(user_id), target_id)
    return f"☣️ You corrupted @{username}'s faction alignment."

def use_lumen_priest(user_id, target_id, username):
    db.set_protection(db.get_chat_id_by_user(user_id), target_id)
    return f"🛐 @{username} was cleansed and shielded from harm."

def use_light_herald(user_id, target_id, username):
    alignment = db.reveal_alignment(db.get_chat_id_by_user(user_id), target_id)
    return f"🌟 @{username}'s aura is *{alignment}*."

def use_saboteur(user_id, target_id, username):
    db.disable_inventory_item(db.get_chat_id_by_user(user_id), target_id)
    return f"🧨 You sabotaged one of @{username}'s items."

def use_courtesan(user_id, target_id, username):
    db.disable_player_next_vote(target_id)
    return f"💃 @{username} is distracted and cannot vote next round."

def use_puppetmaster(user_id, target_id, username):
    db.force_vote(db.get_chat_id_by_user(user_id), target_id, user_id)
    return f"🎭 You control @{username}'s next vote."

def use_trickster(user_id, target_id, username):
    db.swap_roles(db.get_chat_id_by_user(user_id), user_id, target_id)
    return f"🎲 You swapped roles with @{username}."

def use_ascended(user_id, target_id, username):
    db.mark_immune(db.get_chat_id_by_user(user_id), user_id)
    return "🔥 You are immune to the next vote."

def use_archivist(user_id, target_id, username):
    count = db.get_relic_count(user_id)
    if count >= 3:
        return "📚 You possess 3 relics! Victory condition met!"
    return f"🪙 You have {count} relic(s). Find more to win."

def use_goat(user_id, target_id, username):
    return "🐐 You are the Goat. Bide your time and survive."
#NewRoles
def use_silent_fang(user_id, target_id, username):
    chat_id = db.get_chat_id_by_user(user_id)
    if db.is_player_protected(target_id):
        return f"🔪 @{username} is protected. Your blade couldn't reach."
    db.mark_player_for_death(target_id)
    return f"🔪 You silently targeted @{username} for death."

def use_shadow_fang(user_id, target_id, username):
    db.double_vote_power(user_id)
    return "🌑 Your vote holds double weight this round."

def use_blood_alchemist(user_id, target_id, username):
    relic = db.extract_relic_from_recent_death()
    if relic:
        db.give_item(user_id, relic)
        return f"🩸 You forged a relic from the blood of the fallen: {relic}."
    return "🩸 No fresh corpse to extract power from."

def use_echo_seer(user_id, target_id, username):
    echoes = db.get_recent_target_history(target_id)
    if not echoes:
        return f"🪞 No echoes trail @{username}. Nothing to reveal."
    return f"🪞 Echoes reveal @{username}'s past targets: {', '.join(echoes)}"

def use_echo_hunter(user_id, target_id, username):
    if db.get_alive_count() <= 4:
        db.mark_player_for_death(target_id)
        return f"🎯 You hunted @{username} in the chaos. They will fall tonight."
    return "🎯 The shadows are not yet thin enough to hunt freely."

def use_dagger_prophet(user_id, target_id, username):
    db.set_death_prediction(user_id, target_id)
    return f"🗡 You’ve whispered a prophecy: @{username} shall perish. If true, you’ll be rewarded."

def use_kiss_of_eclipse(user_id, target_id, username):
    db.mark_nsfl(user_id)
    db.disable_vote_and_task(target_id)
    return f"💋 You seduced @{username}. They are silenced for one round."
    
