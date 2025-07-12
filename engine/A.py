import random from storage import database as db from engine.roles import assign_roles from engine.tasks import assign_task from telegram.ext import CallbackContext

Keeps track of plot twist frequency

twist_counter = {}

def maybe_trigger_plot_twist(chat_id, context: CallbackContext): from random import choice, shuffle count = twist_counter.get(chat_id, 0) + 1 twist_counter[chat_id] = count

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

def get_dawn_story(): dawn_lines = [ "Three bells rang. One for the fallen. One for the forgotten. The third? It rang before it should have.", "A letter arrived. No name, only the words: 'It wasn’t supposed to be you.'", "The child in the square pointed at you. Then vanished." ] return random.choice(dawn_lines)

def get_night_story(): night_lines = [ "The wind screamed once. Someone screamed louder.", "In every mirror, someone different stared back.", "Shadows whispered your name. Will you answer?" ] return random.choice(night_lines)

def begin_game(context: CallbackContext, chat_id): if not db.is_game_active(chat_id): context.bot.send_message(chat_id, "⚠️ Game was cancelled or never started.") return

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

def start_night_phase(chat_id, context: CallbackContext): context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3h4bzF1dzRyb3B4b2Z2cTBoNzF4NmQ1a2htazFjZjk2ZXV6djFmaCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ZVik7pBtu9dNS/giphy.gif') context.bot.send_message( chat_id=chat_id, text="🌌 Night Phase Begins.\nA hush falls over the realm. Darkness cloaks intentions. Roles with night powers may act now.", parse_mode='Markdown' ) db.set_phase(chat_id, "night") maybe_trigger_plot_twist(chat_id, context)

for user_id in db.get_alive_players(chat_id):
    role = db.get_player_role(chat_id, user_id)
    if role in ["Oracle", "Shadeblade", "Succubus", "Trickster"]:
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=f"🔮 As *{role}*, you may now use your power. Use `/usepower @target`.",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"⚠️ Could not DM {user_id} during night phase: {e}")

# Schedule automatic transition to day phase
context.job_queue.run_once(lambda ctx: start_day_phase(chat_id, ctx), 60)

def start_day_phase(chat_id, context: CallbackContext): context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3FhYm5qNTY2bTg2a2s2cDZ2NzY2dTgwbXhmZm9nZTAyazE0cmJ3byZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3oEjHG3rG7HrzUpt7W/giphy.gif') context.bot.send_message( chat_id=chat_id, text=f"🌅 Day Phase Begins.\n{get_dawn_story()}\nThe sun rises. Whispers turn to accusations. Discuss and vote wisely.", parse_mode='Markdown' ) db.set_phase(chat_id, "day") maybe_trigger_plot_twist(chat_id, context)

for user_id in db.get_alive_players(chat_id):
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
            "📟 A new task has been assigned to you.\nUse /mytasks to view it."
        )
    except Exception as e:
        print(f"Failed to send task to user {user_id}: {e}")

# Optional: Automatically transition to next night phase after discussion
context.job_queue.run_once(lambda ctx: start_night_phase(chat_id, ctx), 90)

def tally_votes(chat_id, context: CallbackContext): votes = db.get_all_votes(chat_id) if not votes: context.bot.send_message(chat_id, "⚖️ No votes were cast. No one is eliminated.") return

vote_counts = {}
for voter, target in votes.items():
    vote_counts[target] = vote_counts.get(target, 0) + 1

max_votes = max(vote_counts.values())
top_targets = [pid for pid, count in vote_counts.items() if count == max_votes]

if len(top_targets) > 1:
    context.bot.send_message(chat_id, "🔄 The vote is tied. No one is eliminated.")
    return

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
    context.job_queue.run_once(lambda ctx: start_night_phase(chat_id, ctx), 10)  # quick transition

