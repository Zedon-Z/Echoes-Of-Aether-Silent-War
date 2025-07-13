
# NOTE: For production, replace this with persistent DB

games = {}
game_start_times = {}
timers = {}
usernames = {}

def is_game_active(chat_id):
    return chat_id in games
    
def has_game_started(chat_id):
    return games.get(chat_id, {}).get("started", False)
    
def mark_game_started(chat_id):
    if chat_id in games:
        games[chat_id]["started"] = True
        
def start_new_game(chat_id):
    games[chat_id] = {
        "phase": "day",
        "players": {},
        "votes": {},
        "deaths": [],
    }

def set_phase(chat_id, phase):
    games[chat_id]["phase"] = phase

def get_phase(chat_id):
    return games[chat_id].get("phase", "day")

def add_player(chat_id, user_id, full_name):
    if chat_id not in games:
        return False  # ❌ No game active in this chat

    if user_id in games[chat_id]["players"]:
        return False  # Already joined

    games[chat_id]["players"][user_id] = {
        "role": None,
        "alive": True,
        "task": None,
        "inventory": [],
        "faction": None,
        "vote": None,
        "protected": False,
        "relics": [],
        "name": full_name,
        "tasks": []
    }
    return True

def get_player_list(chat_id):
    return {
        uid: data["name"]
        for uid, data in games[chat_id]["players"].items()
        if data["alive"]
    }

def cast_vote(chat_id, voter_id, target_id):
    if chat_id not in games:
        return False
    if voter_id == target_id:
        return False
    games[chat_id].setdefault("votes", {})[voter_id] = target_id
    return True

def get_user_role(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("role")
    return None

def get_player_faction(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("faction")
    return "Unknown"

def get_user_id_by_name(name):
    for game in games.values():
        for uid, data in game["players"].items():
            if data["name"] == name.replace("@", ""):
                return uid
    return None

def disable_player_next_vote(user_id):
    for game in games.values():
        if user_id in game["players"]:
            game["players"][user_id]["vote_disabled"] = True

def mark_player_for_death(user_id):
    for game in games.values():
        game["deaths"].append(user_id)

def is_player_protected(user_id):
    # Stub: you could expand this with protection logic
    return False

def get_inventory(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id]["inventory"]
    return []

def remove_item(user_id, item):
    inv = get_inventory(user_id)
    if item in inv:
        inv.remove(item)

def grant_immunity(user_id):
    for game in games.values():
        if user_id in game["players"]:
            game["players"][user_id]["immune"] = True

def get_tasks(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id]["tasks"]
    return []
    
def get_current_task(user_id):
    for chat_id in games:
        player = games[chat_id]["players"].get(user_id)
        if player and player.get("tasks"):
            return player["tasks"][-1]  # Returns the most recent task
    return None
    
def complete_task(user_id, task):
    for game in games.values():
        if user_id in game["players"]:
            game["players"][user_id]["tasks"].remove(task)
            game["players"][user_id]["inventory"].append("relic")  # Example reward

def abandon_current_task(user_id):
    for game in games.values():
        if user_id in game["players"] and game["players"][user_id]["tasks"]:
            game["players"][user_id]["tasks"].clear()
            return True
    return False
# ✅ These are additional helper functions to be added to your existing `database.py`
# Ensure none of these overwrite any existing working logic

# Effect handling for roles like Succubus, Blight Whisperer    
def apply_effect(chat_id, user_id, effect):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id].setdefault("effects", []).append(effect)
        return True
    return False

# Voting override — force a user to vote against their will (Puppetmaster)
def force_vote(chat_id, voter_id, target_id):
    if chat_id in games:
        games[chat_id].setdefault("votes", {})[voter_id] = target_id
        return True
    return False

# Trickster-style vote swap (switches identities)
def swap_votes(chat_id, user_id_1, user_id_2):
    if chat_id not in games:
        return False

    votes = games[chat_id].get("votes", {})
    swapped = {}
    for voter, target in votes.items():
        if target == user_id_1:
            swapped[voter] = user_id_2
        elif target == user_id_2:
            swapped[voter] = user_id_1
        else:
            swapped[voter] = target
    games[chat_id]["votes"] = swapped
    return True

# Get player role safely
def get_player_role(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        return games[chat_id]["players"][user_id].get("role")
    return None

# Used in plot twists to wipe current task
def abandon_current_task(user_id):
    for chat_id in games:
        if user_id in games[chat_id]["players"]:
            games[chat_id]["players"][user_id]["tasks"] = []
            return True
    return False
def reveal_all_roles():
    reveal = []
    for game in games.values():
        for uid, data in game["players"].items():
            reveal.append(f"@{data['name']}: {data['role']}")
    return reveal

def get_alive_players(chat_id):
    return [
        uid for uid, data in games[chat_id]["players"].items()
        if data["alive"]
    ]
def set_username(chat_id, user_id, username):
    if chat_id not in usernames:
        usernames[chat_id] = {}
    usernames[chat_id][user_id] = username
    
def get_username(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id]["name"]
    return "Unknown"

def get_relic_count(user_id):
    inv = get_inventory(user_id)
    return inv.count("relic")

def used_thread(user_id):
    # Stub: implement tracking thread usage
    return False

def check_nexus_control(user_id):
    # Stub: check if Nexus has met win requirements
    return True

def set_nexus_winner(user_id):
    # Stub: could broadcast win or end game
    pass

def trigger_goat_prophecy():
    # Stub for future expansion
    pass

def set_game_start_time(chat_id, timestamp):
    game_start_times[chat_id] = timestamp

def get_game_start_time(chat_id):
    import time
    return game_start_times.get(chat_id, int(time.time()))

def set_timer(chat_id, seconds):
    timers[chat_id] = seconds

def extend_timer(chat_id, seconds):
    if chat_id in timers:
        timers[chat_id] += seconds

def get_timer(chat_id):
    return timers.get(chat_id, 0)

def cancel_game(chat_id):
    games.pop(chat_id, None)
    game_start_times.pop(chat_id, None)
    timers.pop(chat_id, None)

def remove_player(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        del games[chat_id]["players"][user_id]
        return True
    return False


# --- Alliance System ---
alliances = {}

def add_alliance(chat_id, user1, user2):
    pair = tuple(sorted([user1, user2]))
    if chat_id not in alliances:
        alliances[chat_id] = []
    if pair not in alliances[chat_id]:
        alliances[chat_id].append(pair)

def are_allied(chat_id, user1, user2):
    pair = tuple(sorted([user1, user2]))
    return pair in alliances.get(chat_id, [])

def get_allies(chat_id, user_id):
    return [
        other for pair in alliances.get(chat_id, [])
        for other in pair if user_id in pair and other != user_id
    ]

# --- Trade System ---
pending_offers = {}

def offer_item(chat_id, from_user, to_user, item):
    key = (chat_id, from_user, to_user)
    if key not in pending_offers:
        pending_offers[key] = item
        return True
    return False  # Offer already exists

def accept_offer(chat_id, from_user, to_user):
    key = (chat_id, from_user, to_user)
    item = pending_offers.pop(key, None)
    if item:
        if item in games[chat_id]["players"][from_user]["inventory"]:
            games[chat_id]["players"][from_user]["inventory"].remove(item)
            games[chat_id]["players"][to_user]["inventory"].append(item)
            return item
    return None

def get_pending_offers(chat_id, to_user):
    return [
        (from_user, item) for (cid, from_user, target), item in pending_offers.items()
        if cid == chat_id and target == to_user
    ]
# --- Player List Message Tracking ---
game_messages = {}

def set_game_message(chat_id, message_id):
    game_messages[chat_id] = message_id

def get_game_message(chat_id):
    return game_messages.get(chat_id)
