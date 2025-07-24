# NOTE: For production, replace this with persistent DB
game_messages = {}  # <- ✅ Add this
# rest of your variables
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
    "round": 1,
    "echo_votes": {},  # ✅ Echo voting system
    "false_prophecy": False,
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
    
def increment_round(chat_id):
    games[chat_id]["round"] += 1
# --- Voting ---
def force_vote(chat_id, puppet, forced_target):
    """Force a player to vote a specific target."""
    if chat_id not in games:
        return False
    games[chat_id]["votes"][puppet] = forced_target
    games[chat_id]["players"][puppet]["forced_vote"] = forced_target
    return True
    
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
    
def kill_player(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["alive"] = False

def reset_votes(chat_id):
    games[chat_id]["votes"] = {}

def clear_votes(chat_id):
    games[chat_id]["votes"] = {}

def is_vote_disabled(chat_id, user_id):
    return games[chat_id]["players"].get(user_id, {}).get("vote_disabled", False)

def expire_effects(chat_id, phase="day"):
    """
    Removes temporary effects like protection, vote_disable, immune, cursed etc.
    Phase-based expiration: clears certain effects only after day or night.
    """
    if chat_id not in games:
        return

    for user_id, data in games[chat_id]["players"].items():
        # Protection & Immunity expire after night (before day starts)
        if phase == "day":
            data.pop("protected", None)
            data.pop("immune", None)

        # Vote blocks, charm expire after day (before night starts)
        if phase == "night":
            data.pop("vote_disabled", None)
            if "effects" in data:
                # Remove charm, silence, and other day-only effects
                data["effects"] = [e for e in data["effects"] if e not in ["charmed", "silenced"]]
                if not data["effects"]:
                    data.pop("effects", None)

        # Clean disabled items tracker (for sabotage or effects lasting 1 round)
        data.pop("disabled_item", None)
# --- Role Powers ---
def disable_random_item(user_id):
    inv = get_inventory(user_id)
    if inv:
        item = random.choice(list(inv.keys()))
        inv.pop(item)
        return item
    return None
    
def corrupt_task(user_id):
    tasks = get_tasks(user_id)
    if tasks:
        task = tasks[0]
        task["description"] = "❌ [Corrupted] " + task["description"]
        return True
    return False

def grant_random_item(chat_id, user_id):
    items = ["truth_crystal", "shadow_ring", "goat_scroll"]
    item = random.choice(items)
    inv = games[chat_id]["players"][user_id].setdefault("inventory", {})
    inv[item] = inv.get(item, 0) + 1
    return item
    
def protect_player(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["protected"] = True
        return True
    return False

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
        inventory = games[chat_id]["players"][user_id].get("inventory", {})
        if isinstance(inventory, dict):
            if inventory:
                # Disable one random item
                item = random.choice(list(inventory.keys()))
                inventory[item] -= 1
                if inventory[item] <= 0:
                    del inventory[item]
                games[chat_id]["players"][user_id]["disabled_item"] = item
                return item
        elif isinstance(inventory, list):
            if inventory:
                item = inventory.pop(0)
                games[chat_id]["players"][user_id]["disabled_item"] = item
                return item
    return None
def mark_immune(chat_id, user_id):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["immune"] = True
        
def grant_vote_immunity(chat_id, user_id):
    games[chat_id]["players"][user_id]["immune"] = True

def is_immune(chat_id, user_id):
    return games[chat_id]["players"][user_id].get("immune", False)
    
def get_relic_count(user_id):
    inv = get_inventory(user_id)
    return inv.count("relic")

def enable_whisper(chat_id, from_id, to_id):
    if chat_id in games:
        if "whispers" not in games[chat_id]:
            games[chat_id]["whispers"] = []
        games[chat_id]["whispers"].append((from_id, to_id))
def log_death(chat_id, user_id, reason="eliminated"):
    games[chat_id].setdefault("death_log", []).append({"user": user_id, "reason": reason})

def get_recent_death_logs(chat_id):
    return games[chat_id].get("death_log", [])[-3:]  # Last 3 deaths
    
# --- Tasks / Inventory ---
def get_inventory(user_id):
    for game in games.values():
        if user_id in game["players"]:
            return game["players"][user_id].get("inventory", {})
    return {}
    
def remove_item(user_id, item):
    inv = get_inventory(user_id)
    if item in inv:
        inv[item] -= 1
        if inv[item] <= 0:
            del inv[item]

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
            inv = game["players"][user_id].setdefault("inventory", {})
            inv[item] = inv.get(item, 0) + 1

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
    
cooldowns = {}  # key: (user_id, item), value: timestamp

def set_item_cooldown(user_id, item, duration=60):
    import time
    cooldowns[(user_id, item)] = time.time() + duration

def is_item_on_cooldown(user_id, item):
    import time
    return cooldowns.get((user_id, item), 0) > time.time()
# --- Thread/Story Mechanics ---

# Tracks thread usage, prevents spamming prophecy/story triggers
thread_usage = {}

def used_thread(user_id):
    return thread_usage.get(user_id, False)

def mark_thread_used(user_id):
    thread_usage[user_id] = True


def check_nexus_control(user_id):
    """
    Nexus win condition: Check if player holds 3 relics and the core key.
    """
    inv = get_inventory(user_id)
    core_key = "core_key"
    relics = [item for item in inv if item == "relic"]

    if inv.count(core_key) >= 1 and len(relics) >= 3:
        return True
    return False


def set_nexus_winner(user_id):
    """
    Triggers Nexus victory, locks game state.
    """
    for chat_id, game in games.items():
        if user_id in game["players"]:
            game["nexus_winner"] = user_id
            game["phase"] = "ended"
            log_death(chat_id, user_id, reason="⚙️ Nexus Conqueror")
            print(f"[WIN] Nexus win triggered by {user_id}")
            return True
    return False


def trigger_goat_prophecy():
    """
    Special chaotic twist where goat rewrites the endgame scenario.
    """
    for chat_id, game in games.items():
        players = game.get("players", {})
        for uid, data in players.items():
            if data.get("role") == "Goat" and data.get("alive"):
                game.setdefault("goat_prophecy", True)
                game["phase"] = "prophecy"
                print(f"[PROPHECY] Goat prophecy activated in {chat_id}")
                return True
    return False

def resolve_goat_prophecy(chat_id):
    if games[chat_id].get("goat_prophecy"):
        # For example, instant chaos kill random alive
        import random
        alive = get_alive_players(chat_id)
        if alive:
            unlucky = random.choice(alive)
            process_death(chat_id, unlucky, reason="🐐 Goat Prophecy Wrath")
        games[chat_id]["phase"] = "day"
        
def set_echo_vote(chat_id, user_id, choice):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["echo_votes"][user_id] = choice

def get_echo_votes(chat_id):
    return games[chat_id].get("echo_votes", {})

def get_dominant_echo_vote(chat_id):
    from collections import Counter
    votes = get_echo_votes(chat_id).values()
    if not votes:
        return None
    counter = Counter(votes)
    dominant, count = counter.most_common(1)[0]
    return dominant

def process_death(chat_id, user_id, reason="eliminated"):
    if chat_id in games and user_id in games[chat_id]["players"]:
        games[chat_id]["players"][user_id]["alive"] = False
        log_death(chat_id, user_id, reason)

def get_phase(chat_id):
    if chat_id not in games:
        return "day"  # fallback phase
    return games[chat_id].get("phase", "day")
    
def get_round(chat_id):
    if chat_id in games:
        return games[chat_id].get("round", 1)
    return 1
# ✅ DOUBLE vote power (Shadow Fang)
def double_vote_power(user_id):
    games['double_votes'] = games.get('double_votes', {})
    games['double_votes'][user_id] = True

def is_double_vote(user_id):
    return games.get('double_votes', {}).get(user_id, False)

# ✅ GET RECENT TARGET history (Echo Seer)
def get_recent_target_history(user_id):
    return games.get('target_history', {}).get(user_id, [])

# ✅ DEATH prediction (Dagger Prophet)
def set_death_prediction(user_id, predicted_target):
    games['prophecies'] = games.get('prophecies', {})
    games['prophecies'][user_id] = predicted_target

def check_prophecy_success(user_id, actual_death):
    return games.get('prophecies', {}).get(user_id) == actual_death

# ✅ RELIC extraction (Blood Alchemist)
def extract_relic_from_recent_death():
    deaths = games.get('death_log', [])
    if deaths:
        return random.choice(["blood_orb", "memory_fragment"])
    return None
