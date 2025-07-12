import random
from storage import database as db
from engine.roles import assign_roles
from engine.tasks import assign_task
from telegram.ext import CallbackContext

twist_counter = {}

def maybe_trigger_plot_twist(chat_id, context: CallbackContext):
    from random import choice, shuffle
    count = twist_counter.get(chat_id, 0) + 1
    twist_counter[chat_id] = count

    if count % 3 != 0:
        return

    twists = [
        "Echo Swap! Roles shuffled among players...",
        "Memory Wipe! All active tasks reset.",
        "False Prophet! Oracle visions are reversed.",
        "Emotional Collapse! Everyone loses 1 item.",
        "Night of Whispers... Votes next round are anonymous."
    ]
    twist = choice(twists)
    context.bot.send_message(chat_id, f"🌪 *Plot Twist!*\n{twist}", parse_mode='Markdown')

    if "Memory Wipe" in twist:
        for user_id in db.get_alive_players(chat_id):
            db.abandon_current_task(user_id)

    elif "Echo Swap" in twist:
        players = list(db.games[chat_id]["players"].keys())
        roles = [db.games[chat_id]["players"][pid]["role"] for pid in players]
        shuffle(roles)
        for pid, new_role in zip(players, roles):
            db.games[chat_id]["players"][pid]["role"] = new_role

def get_dawn_story():
    dawn_lines = [
        "Three bells rang. One for the fallen. One for the forgotten. The third? It rang before it should have.",
        "A letter arrived. No name, only the words: 'It wasn’t supposed to be you.'",
        "The child in the square pointed at you. Then vanished."
    ]
    return random.choice(dawn_lines)

def get_night_story():
    night_lines = [
        "The wind screamed once. Someone screamed louder.",
        "In every mirror, someone different stared back.",
        "Shadows whispered your name. Will you answer?"
    ]
    return random.choice(night_lines)

def begin_game(context: CallbackContext, chat_id):
    if not db.is_game_active(chat_id):
        context.bot.send_message(chat_id, "⚠️ Game was cancelled or never started.")
        return

    if db.has_game_started(chat_id):
        context.bot.send_message(chat_id, "⚠️ Game already started.")
        return

    players = db.get_player_list(chat_id)
    if len(players) < 3:
        context.bot.send_message(chat_id, "❌ Not enough players to begin. Minimum 6 required.")
        return

    db.mark_game_started(chat_id)
    assign_roles(chat_id, players, context)
    context.bot.send_message(chat_id, "🎮 *The game begins!*", parse_mode='Markdown')
    start_day_phase(chat_id, context)

def start_day_phase(chat_id, context: CallbackContext):
    context.bot.send_message(chat_id, "🌅 *Day Phase Begins.*\nDiscuss and find the impostors.", parse_mode='Markdown')
    db.set_phase(chat_id, "day")
    maybe_trigger_plot_twist(chat_id, context)

    for user_id in db.get_alive_players(chat_id):
        task_roll = random.choice(["phrase", "protect", "abstain"])
        if task_roll == "phrase":
            assign_task(user_id, "Say: The stars remember me.", "say_stars")
        elif task_roll == "protect":
            assign_task(user_id, "Keep another player alive for 3 rounds.", "guard_3rounds")
        elif task_roll == "abstain":
            assign_task(user_id, "Avoid voting for two days.", "no_vote2")

        try:
            context.bot.send_message(user_id, "🧾 A new task has been assigned to you.\nUse /mytasks to view it.")
        except Exception as e:
            print(f"Failed to send task to user {user_id}: {e}")
