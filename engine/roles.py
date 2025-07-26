import random
from engine.animation import dagger_prophet_success_animation
from engine.animation import dagger_prophet_fail_message
from storage import database as db

# === Adaptive Role Pool Assignment ===
def assign_roles(chat_id, player_ids, context):
    assigned = {}
    num_players = len(player_ids)

    # Tiered role pools depending on player count
    core_roles = [
        "Shadeblade", "Oracle", "Lumen Priest", "Tinkerer", "Silent Fang", "Echo Seer", "Kiss Of Eclipse"
    ]
    mid_roles = [
        "Saboteur", "Puppetmaster", "Trickster", "Shadow Fang", "Dagger Prophet", "Goat"
    ]
    advanced_roles = [
        "Core Reverser", "Echo Hunter", "Blood Alchemist", "Ascended", "Archivist"
    ]

    full_pool = core_roles[:]
    if num_players >= 6:
        full_pool += mid_roles
    if num_players >= 9:
        full_pool += advanced_roles

    random.shuffle(full_pool)
    
    for player_id in player_ids:
        role = role_pool.pop() if role_pool else "Goat"
        db.assign_role(chat_id, player_id, role)
        assigned[player_id] = role
        db.games[chat_id]["players"][player_id]["faction"] = faction_map.get(role, "Neutral")
        
        faction_map = {
             # 🗡 Whispered Blades – Assassin Faction 
            "Silent Fang": "Whispered Blades",
            "Shadow Fang": "Whispered Blades",
            "Shadeblade": "Whispered Blades",

            # 🌟 Luminae – Mystics & Visionaries (formerly "Seers")
            "Oracle": "Luminae",
            "Echo Seer": "Luminae",
            "Dagger Prophet": "Luminae",
            "Lumen Priest": "Luminae",

            # 🔧 Nexus – Chaos & Control
            "Tinkerer": "Nexus",
            "Saboteur": "Nexus",
            "Puppetmaster": "Nexus",
            "Trickster": "Nexus",

            # 🌀 Veilbound – Rogues, Cursed & Fringe (Alt name for Common Enemies)
            "Core Reverser": "Veilbound (Common Enemies)",
            "Blood Alchemist": "Veilbound (Common Enemies)",
            "Echo Hunter": "Veilbound (Common Enemies)",
            "Kiss Of Eclipse": "Veilbound (Common Enemies)",
            "Ascended": "Veilbound (Common Enemies)",
            "Archivist": "Veilbound (Common Enemies)",
            "Goat": "Veilbound (Common Enemies)",
            }

        # ✅ Send role to player privately
        role_descriptions = {
            "Oracle": "🔮 See the role of a player.",
            "Core Reverser": "🌀🎭 Once per game, shuffle all final votes before execution.",
            "Shadeblade": "🗡️ Mark one player for elimination.",
            "Puppetmaster": "🧵 Control someone’s vote.",
            "Trickster": "🎭 Swap your vote with another.",
            "Saboteur": "🔧 Disable an item from a player.",
            
            "Silent Fang": "🗡️👁️ Assassinate a player. See if they’re protected before striking.",
            "Shadow Fang": "🫥🗳️ Knows the Silent Fang. Has double vote power.",
            "Echo Seer": "🌬️🌀 Hears whispers and secret exchanges.",
            "Dagger Prophet": "🩸🔮 Predicts a player's death. Gains power if correct.",
            "Blood Alchemist": "🧪💀 Absorb the last dead role’s power as a relic.",
            "Echo Hunter": "🎯🐺 Gets an extra kill when fewer than 4 players remain.",
            "Kiss Of Eclipse": "💋🌒 Kiss a player each night they get silenced for 1 round. Win by kissing all factions.",
        
            "Tinkerer": "🔨 Craft a random item.",
            "Lumen Priest": "🛡️ Shield someone from elimination.",
            "Ascended": "✨ Become immune to 1 vote.",
            
            "Archivist" : "📚 Reveal data from last death. Get 3 relic to win and to see behind death",
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
        "Archivist": use_archivist,
        "Tinkerer": use_tinkerer,
        "Silent Fang": use_silent_fang,
        "Shadow Fang": use_shadow_fang,
        "Blood Alchemist": use_blood_alchemist,
        "Echo Seer": use_echo_seer,
        "Echo Hunter": use_echo_hunter,
        "Dagger Prophet": use_dagger_prophet,
        "Core Reverser": use_core_reverser,
        "Lumen Priest": use_lumen_priest,
        
        "Saboteur": use_saboteur,
        "Kiss Of Eclipse": use_kiss_of_eclipse,
        "Puppetmaster": use_puppetmaster,
        "Trickster": use_trickster,
        "Ascended": use_ascended,
        
        "Goat": use_goat
    }

    power_fn = role_actions.get(user_role)
    if power_fn:
        return power_fn(user_id, target_id, target_username)
    return "❌ Your role has no defined power yet."


# --- Individual Role Powers ---
def use_core_reverser(user_id, target_id, username):
    chat_id = db.get_chat_id_by_user(user_id)

    if db.has_used_core_reverser(user_id):
        return "⚠️ You have already twisted the Core once. Its gears won’t bend again."

    db.mark_core_reverser_used(user_id)
    db.shuffle_votes(chat_id)
    return "🔁 *The Core has been reversed!* The outcome may shift... fate is rewritten."
    
def use_shadeblade(user_id, target_id, username):
    if db.is_player_protected(target_id):
        return "⚠️ Target was protected!"
    db.mark_player_for_death(target_id)
    return f"🗡 You marked @{username} for death tonight."

def use_oracle(user_id, target_id, username):
    faction = db.get_player_faction(target_id)
    return f"🔮 Oracle's Vision: @{username} is part of *{faction}*."

def use_tinkerer(user_id, target_id, username):
    loot_table = ["relic", "truth_crystal", "shadow_ring", "goat_scroll", "core_key"]
    item = random.choice(loot_table)
    inventory = db.get_inventory(user_id)
    inventory[item] = inventory.get(item, 0) + 1
    return f"🛠️ You tinkered and created a '{item}'!"
    
def use_lumen_priest(user_id, target_id, username):
    db.set_protection(db.get_chat_id_by_user(user_id), target_id)
    return f"🛐 @{username} was cleansed and shielded from harm."

def use_saboteur(user_id, target_id, username):
    db.disable_inventory_item(db.get_chat_id_by_user(user_id), target_id)
    return f"🧨 You sabotaged one of @{username}'s items."

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
    chat_id = db.get_chat_id_by_user(user_id)
    prediction = db.get_prediction(chat_id)

    if not prediction:
        db.set_death_prediction(chat_id, target_id)
        return f"📿 You inscribe a death prophecy upon @{target_username}....If true, you’ll be rewarded."

    if prediction == target_id:
        # Prediction correct — dramatic reveal
        dagger_prophet_success_animation(context.bot, chat_id, target_username)
        db.mark_player_for_death(target_id)
        db.clear_prediction(chat_id)
        return f"💀 Your prophecy is fulfilled. @{username} shall perish."
    else:
        # Prediction failed
        dagger_prophet_fail_message(context.bot, chat_id)
        db.clear_prediction(chat_id)
        return "❌ Your prophecy failed. The blade hungers still."

def use_kiss_of_eclipse(user_id, target_id, username):
    chat_id = db.get_chat_id_by_user(user_id)
    bot = db.get_bot()

    # Break old bond and kill ex if exists
    previous = db.get_kissed_target(chat_id, user_id)
    if previous and previous != target_id:
        ex_username = db.get_username(previous)
        db.kill_player(chat_id, previous)
        db.remove_couple(chat_id, user_id)
        from engine.animation import eclipse_breakup_animation
        eclipse_breakup_animation(bot, chat_id, ex_username)

    # Form new bond
    db.set_couple(chat_id, user_id, target_id)
    db.silence_player(chat_id, target_id)

    from engine.animation import eclipse_couple_formed
    eclipse_couple_formed(bot, chat_id, db.get_username(user_id), username)

    return f"💋 @{username} has been kissed under the *Eclipse*. Their voice fades for a round..."
