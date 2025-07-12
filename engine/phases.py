
import random
from storage import database as db
from engine.roles import assign_roles
from engine.tasks import assign_task
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Keeps track of plot twist frequency
twist_counter = {}
# Tracks active vote messages
active_vote_buttons = {}
# Stores power actions to process
pending_powers = {}

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
    return random.choice([
        "Three bells rang. One for the fallen. One for the forgotten. The third? It rang before it should have.",
        "A letter arrived. No name, only the words: 'It wasn’t supposed to be you.'",
        "The child in the square pointed at you. Then vanished."
    ])

def get_night_story():
    return random.choice([
        "The wind screamed once. Someone screamed louder.",
        "In every mirror, someone different stared back.",
        "Shadows whispered your name. Will you answer?"
    ])

def begin_game(context: CallbackContext, chat_id):
    if not db.is_game_active(chat_id):
        context.bot.send_message(chat_id, "⚠️ Game was cancelled or never started.")
        return

    if db.has_game_started(chat_id):
        context.bot.send_message(chat_id, "⚠️ Game already started.")
        return

    players = db.get_player_list(chat_id)
    if len(players) < 3:
        context.bot.send_message(chat_id, "❌ Not enough players to begin. Minimum 3 required.")
        return

    db.mark_game_started(chat_id)
    assign_roles(chat_id, players, context)
    context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/QBd2kLB5qDmysEXre9/giphy.gif')
    context.bot.send_message(chat_id, "🎮 *The game begins! Night falls...*", parse_mode='Markdown')
    start_night_phase(chat_id, context)

def start_night_phase(chat_id, context: CallbackContext):
    context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3h4bzF1dzRyb3B4b2Z2cTBoNzF4NmQ1a2htazFjZjk2ZXV6djFmaCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ZVik7pBtu9dNS/giphy.gif')
    context.bot.send_message(
        chat_id=chat_id,
        text="🌌 *Night Phase Begins.*\nA hush falls over the realm. Darkness cloaks intentions. Roles with night powers may act now.",
        parse_mode='Markdown'
    )
    db.set_phase(chat_id, "night")
    maybe_trigger_plot_twist(chat_id, context)

    for user_id in db.get_alive_players(chat_id):
        role = db.get_player_role(chat_id, user_id)
        if role in ["Oracle", "Shadeblade", "Succubus", "Trickster", "Puppetmaster", "Blight Whisperer"]:
            try:
                context.bot.send_message(
                    chat_id=user_id,
                    text=f"🔮 As *{role}*, you may now use your power. Use `/usepower @target`.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"⚠️ Could not DM {user_id} during night phase: {e}")

    context.job_queue.run_once(lambda ctx: resolve_night(chat_id, ctx), 60)

def resolve_night(chat_id, context):
    context.bot.send_message(chat_id, f"☀️ The night fades. {get_night_story()}")
    start_day_phase(chat_id, context)

def start_day_phase(chat_id, context: CallbackContext):
    context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3FhYm5qNTY2bTg2a2s2cDZ2NzY2dTgwbXhmZm9nZTAyazE0cmJ3byZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3oEjHG3rG7HrzUpt7W/giphy.gif')
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🌅 *Day Phase Begins.*\n{get_dawn_story()}\nThe sun rises. Whispers turn to accusations. Discuss and vote wisely.",
        parse_mode='Markdown'
    )
    db.set_phase(chat_id, "day")
    maybe_trigger_plot_twist(chat_id, context)

    players = db.get_alive_players(chat_id)
    buttons = [[InlineKeyboardButton(f"Vote: {db.get_username(pid)}", callback_data=f"vote_{pid}")] for pid in players]
    markup = InlineKeyboardMarkup(buttons)
    vote_msg = context.bot.send_message(chat_id, "🗳️ *Vote for a player to eliminate:*", parse_mode='Markdown', reply_markup=markup)
    active_vote_buttons[chat_id] = vote_msg.message_id

    for user_id in players:
        task_roll = random.choice(["phrase", "protect", "abstain"])
        if task_roll == "phrase":
            assign_task(user_id, "Say: The stars remember me.", "say_stars")
        elif task_roll == "protect":
            assign_task(user_id, "Keep another player alive for 3 rounds.", "guard_3rounds")
        elif task_roll == "abstain":
            assign_task(user_id, "Avoid voting for two days.", "no_vote2")

        try:
            context.bot.send_message(
                user_id,
                "📜 A new task has been assigned to you.\nUse /mytasks to view it."
            )
        except Exception as e:
            print(f"Failed to send task to user {user_id}: {e}")

    context.job_queue.run_once(lambda ctx: tally_votes(chat_id, ctx), 90)

def tally_votes(chat_id, context: CallbackContext):
    votes = db.get_all_votes(chat_id)
    if not votes:
        context.bot.send_message(chat_id, "⚖️ No votes were cast. No one is eliminated.")
        return start_night_phase(chat_id, context)

    vote_counts = {}
    for voter, target in votes.items():
        vote_counts[target] = vote_counts.get(target, 0) + 1

    max_votes = max(vote_counts.values())
    top_targets = [pid for pid, count in vote_counts.items() if count == max_votes]

    if len(top_targets) > 1:
        context.bot.send_message(chat_id, "🔄 The vote is tied. No one is eliminated.")
        return start_night_phase(chat_id, context)

    eliminated = top_targets[0]
    db.eliminate_player(chat_id, eliminated)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"☠️ <a href='tg://user?id={eliminated}'>A player</a> has been eliminated!",
        parse_mode='HTML'
    )

    if db.check_win_conditions(chat_id):
        context.bot.send_message(chat_id, "🎉 Game over! A faction has won!")
    else:
        start_night_phase(chat_id, context)

def handle_usepower(user_id, target_id, chat_id, context: CallbackContext):
    role = db.get_player_role(chat_id, user_id)
    if role == "Oracle":
        target_role = db.get_player_role(chat_id, target_id)
        context.bot.send_message(user_id, f"🔮 You had a vision. {db.get_username(target_id)} is a *{target_role}*.", parse_mode='Markdown')
    elif role == "Shadeblade":
        db.eliminate_player(chat_id, target_id)
        context.bot.send_message(chat_id, f"🗡️ In the darkness, <a href='tg://user?id={target_id}'>a soul</a> was silently taken.", parse_mode='HTML')
    elif role == "Succubus":
        db.apply_effect(chat_id, target_id, "charmed")
        context.bot.send_message(chat_id, f"💋 A charm spell affects <a href='tg://user?id={target_id}'>someone</a>...", parse_mode='HTML')
    elif role == "Trickster":
        db.swap_votes(chat_id, user_id, target_id)
        context.bot.send_message(chat_id, f"🎭 The Trickster swaps fate... votes may deceive.", parse_mode='Markdown')
    elif role == "Puppetmaster":
        db.force_vote(chat_id, target_id, user_id)
        context.bot.send_message(chat_id, f"🪆 Puppet strings tighten. Someone was forced to vote unwillingly.", parse_mode='Markdown')
    elif role == "Blight Whisperer":
        db.apply_effect(chat_id, target_id, "cursed")
        context.bot.send_message(chat_id, f"🕷️ Blight spreads silently... a player is now cursed.", parse_mode='Markdown')
    return True
