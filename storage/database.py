# NOTE: For production, replace this with persistent DB

games = {}
game_start_times = {}
timers = {}
usernames = {}
task_progress = {}
alliances = {}
whispers = {}
# --- Alliance Vote Monitoring ---
def notify_allies_vote(chat_id, voter_id, target_id, context):
    for pair in alliances.get(chat_id, []):
        if voter_id in pair:
            ally_id = pair[0] if pair[1] == voter_id else pair[1]
            try:
                context.bot.send_message(
                    chat_id=ally_id,
                    text=f"👁️ Your ally @{get_username(voter_id)} voted for @{get_username(target_id)}."
                )
            except Exception as e:
                print(f"[WARN] Failed to notify ally of vote: {e}")

# --- Bonus Task When Allies Protect Each Other ---
def bonus_task_if_ally_protected(chat_id, protector_id, target_id):
    if are_allied(chat_id, protector_id, target_id):
        games[chat_id]["players"][protector_id]["tasks"].append({
            "code": "ally_bonus",
            "desc": f"Protected your ally @{get_username(target_id)}."
        })

# --- Alliance Core Functions ---
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
    
# --- Alliance Chat System ---
def send_alliance_group_message(chat_id, from_id, message, context):
    if chat_id not in alliances:
        return

    for pair in alliances[chat_id]:
        if from_id in pair:
            for uid in pair:
                if uid != from_id:
                    try:
                        context.bot.send_message(
                            chat_id=uid,
                            text=f"🤐 Alliance Chat | @{get_username(from_id)}:\n{message}"
                        )
                    except Exception as e:
                        print(f"[WARN] Could not deliver alliance group message to {uid}: {e}")
# Existing and updated methods below
# --- Enhanced Task System ---
def record_message(user_id, text):
    for chat_id in games:
        if user_id in games[chat_id]["players"]:
            current_task = get_current_task(user_id)
            if current_task:
                code = current_task.get("code")
                if code == "say_stars" and "stars remember me" in text.lower():
                    task_progress[(chat_id, user_id, code)] = "completed"


def check_abstain(user_id, voted=False):
    for chat_id in games:
        if user_id in games[chat_id]["players"]:
            current_task = get_current_task(user_id)
            if current_task and current_task.get("code") == "no_vote2":
                key = (chat_id, user_id, "no_vote2")
                prev = task_progress.get(key, 0)
                if voted:
                    task_progress[key] = "failed"
                elif prev != "failed":
                    task_progress[key] = prev + 1 if isinstance(prev, int) else 1


def auto_complete_tasks():
    for (chat_id, user_id, code), progress in list(task_progress.items()):
        if code == "no_vote2" and progress == 2:
            complete_task(user_id, {"code": code, "desc": "Avoid voting for two days."})
            task_progress[(chat_id, user_id, code)] = "completed"
        elif progress == "completed":
            task = get_current_task(user_id)
            if task and task.get("code") == code:
                complete_task(user_id, task)
                task_progress[(chat_id, user_id, code)] = "archived"

# --- Game Lifecycle ---
def is_game_active(chat_id):
    return chat_id in games

def has_game_started(chat_id):
    return games.get(chat_id, {}).get("started", False)

def mark_game_started(chat_id):
    if chat_id in games:
        games[chat_id]["started"] = True
        
def get_chat_id_by_user(user_id):
    for chat_id, game in games.items():
        if user_id in game.get("players", {}):
            return chat_id
    return None
    
def start_new_game(chat_id):
    games[chat_id] = {
        "phase": "day",
        "players": {},
        "votes": {},
        "deaths": [],
    }

# --- Phase Control ---
def set_phase(chat_id, phase):
    games[chat_id]["phase"] = phase

def get_phase(chat_id):
    return games[chat_id].get("phase", "day")

# --- Player Management ---
def add_player(chat_id, user_id, full_name):
    if chat_id not in games:
        return False
    if user_id in games[chat_id]["players"]:
        return False
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

def assign_role(chat_id, user_id, role):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["role"] = role

def get_player_role(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        return games[chat_id]["players"][user_id].get("role")
    return None

def get_user_role(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("role")
    return None

# --- Voting ---
def cast_vote(chat_id, voter_id, target_id):
    if chat_id not in games or voter_id == target_id:
        return False
    games[chat_id].setdefault("votes", {})[voter_id] = target_id
    return True

def force_vote(chat_id, voter_id, target_id):
    if chat_id in games:
        games[chat_id].setdefault("votes", {})[voter_id] = target_id
        return True
    return False

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

# --- Role Powers ---
def disable_player_next_vote(user_id):
    for game in games.values():
        if user_id in game["players"]:
            game["players"][user_id]["vote_disabled"] = True

def mark_player_for_death(user_id):
    for game in games.values():
        game["deaths"].append(user_id)

def is_player_protected(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("protected", False)
    return False

def get_player_faction(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("faction", "Unknown")
    return "Unknown"

def curse_alignment(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["faction"] = "Corrupted"

def reveal_alignment(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        return games[chat_id]["players"][user_id].get("faction", "Unknown")
    return "Unknown"

def set_protection(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["protected"] = True

def disable_inventory_item(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        inventory = games[chat_id]["players"][user_id].get("inventory", [])
        if inventory:
            disabled_item = inventory.pop(0)
            games[chat_id]["players"][user_id]["disabled_item"] = disabled_item

def mark_immune(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["immune"] = True

def get_relic_count(user_id):
    inv = get_inventory(user_id)
    return inv.count("relic")

def enable_whisper(chat_id, from_id, to_id):
    if chat_id in games:
        if "whispers" not in games[chat_id]:
            games[chat_id]["whispers"] = []
        games[chat_id]["whispers"].append((from_id, to_id))

# --- Tasks / Inventory ---
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
            return player["tasks"][-1]
    return None

def complete_task(user_id, task):
    for game in games.values():
        if user_id in game["players"]:
            # Remove task
            game["players"][user_id]["tasks"].remove(task)
            
            # Determine item reward based on task code
            code = task.get("code")
            reward_map = {
                "say_stars": "truth_crystal",
                "guard_3rounds": "shadow_ring",
                "no_vote2": "goat_scroll"
            }
            item = reward_map.get(code, "relic")

            # Add reward to inventory
            game["players"][user_id]["inventory"].append(item)

def abandon_current_task(user_id):
    for game in games.values():
        if user_id in game["players"] and game["players"][user_id]["tasks"]:
            game["players"][user_id]["tasks"].clear()
            return True
    return False

# --- Utility ---
def get_user_id_by_name(name):
    for game in games.values():
        for uid, data in game["players"].items():
            if data["name"] == name.replace("@", ""):
                return uid
    return None

def get_username(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id]["name"]
    return "Unknown"

def set_username(chat_id, user_id, username):
    if chat_id not in usernames:
        usernames[chat_id] = {}
    usernames[chat_id][user_id] = username

def get_alive_players(chat_id):
    return [
        uid for uid, data in games[chat_id]["players"].items()
        if data["alive"]
    ]

def reveal_all_roles():
    reveal = []
    for game in games.values():
        for uid, data in game["players"].items():
            reveal.append(f"@{data['name']}: {data['role']}")
    return reveal

# --- Game Message & Timer ---
def set_game_message(chat_id, message_id):
    game_messages[chat_id] = message_id

def get_game_message(chat_id):
    return game_messages.get(chat_id)

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
    return False

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

# --- Thread/Story Mechanics ---
def used_thread(user_id):
    return False

def check_nexus_control(user_id):
    return True

def set_nexus_winner(user_id):
    pass

def trigger_goat_prophecy():
    pass

game_messages = {}

