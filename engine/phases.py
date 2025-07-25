import random
from collections import Counter
from engine.animation import dark_fantasy_animation
from engine.animation import send_alive_players_animation
from engine.animation import lumen_priest_animation
from engine.win import check_for_winner
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
    if db.get_round(chat_id) == 3: trigger_false_prophecy(chat_id, context)
        
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
    print("[DEBUG] Calling assign_roles...")  # <- add this
    assign_roles(chat_id, players, context)
    context.bot.send_animation(chat_id, animation='https://media.giphy.com/media/QBd2kLB5qDmysEXre9/giphy.gif')
    context.bot.send_message(chat_id, "🎮 *The game begins! Night falls...*", parse_mode='Markdown')
    start_night_phase(chat_id, context)

def start_night_phase(chat_id, context: CallbackContext):
    context.bot.send_animation(
        chat_id,
        animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGRvdzJ1NGdjYzhrYW14M2w4bXBoOXEyZ2Z6aW5nNXRocjByNmp4cyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VbnUQpnihPSIgIXuZv/giphy.gif'
    )
    dark_fantasy_animation(context.bot, chat_id)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🌙 *Night falls.*\n{get_night_story()}\nEach role must act in shadows.",
        parse_mode="Markdown"
    )

    db.set_phase(chat_id, "night")
    # ✅ Optional: Clean night-only buffs
    db.expire_effects(chat_id, phase="night")
    alive_players = db.get_alive_players(chat_id)
    usernames = {uid: db.get_username(uid) or f"user{uid}" for uid in alive_players}

    for user_id in alive_players:
        role = db.get_player_role(chat_id, user_id)

        # Skip roles with no power
        if role in ["Goat"]:
            continue

        # Build buttons for other targets
        buttons = []
        for target_id in alive_players:
            if target_id != user_id:
                target_name = usernames[target_id]
                buttons.append([
                    InlineKeyboardButton(f"Use Power on {target_name}", callback_data=f"usepower_{target_id}")
                ])

        try:
            context.bot.send_message(
                chat_id=user_id,
                text="🔮 Choose a target to use your power on:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            print(f"[WARN] Could not send power buttons to {user_id}: {e}")

    context.job_queue.run_once(lambda ctx: start_day_phase(chat_id, ctx), 90)

def resolve_night(chat_id, context):
    context.bot.send_message(chat_id, f"☀️ The night fades. {get_night_story()}")
    start_day_phase(chat_id, context)

def start_day_phase(chat_id, context: CallbackContext):
    # 💀 Apply Night Deaths
    deaths = db.games[chat_id].pop("deaths", [])
    for uid in deaths:
        db.kill_player(chat_id, uid)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"💀 @{db.get_username(uid)} was found dead at dawn 💀⚰️..."
        )

    # 🌅 Announce Day Phase
    context.bot.send_animation(
        chat_id,
        animation='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3FhYm5qNTY2bTg2a2s2cDZ2NzY2dTgwbXhmZm9nZTAyazE0cmJ3byZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3oEjHG3rG7HrzUpt7W/giphy.gif'
    )
    send_alive_players_animation(chat_id, context.bot)

    # ✅ Phase Update
    db.increment_round(chat_id)
    if db.get_round(chat_id) >= 4: 
        start_final_echo(chat_id, context)
    reveal_false_prophecy(chat_id, context)
    db.set_phase(chat_id, "day")
    maybe_trigger_plot_twist(chat_id, context)
    db.reset_votes(chat_id)
    db.expire_effects(chat_id, phase="day")

    players = db.get_alive_players(chat_id)
    usernames = {uid: db.get_username(uid) or f"user{uid}" for uid in players}

    # 🗳️ Voting (Private DMs)
    for user_id in players:
        vote_buttons = [
            [InlineKeyboardButton(f"Vote: {usernames[tid]}", callback_data=f"vote_{tid}")]
            for tid in players if tid != user_id
        ]
        try:
            context.bot.send_message(
                chat_id=user_id,
                text="🗳️ *Vote privately:* Who should be eliminated?",
                reply_markup=InlineKeyboardMarkup(vote_buttons),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[WARN] Could not send private vote buttons to {user_id}: {e}")

    # 📜 Tasks Allocation
    for user_id in players:
        task_roll = random.choice(["phrase", "protect", "abstain"])
        if task_roll == "phrase":
            assign_task(user_id, "Say: The stars remember me.", "say_stars")
        elif task_roll == "protect":
            assign_task(user_id, "Keep another player alive for 3 rounds.", "guard_3rounds")
        elif task_roll == "abstain":
            assign_task(user_id, "Avoid voting for two days.", "no_vote2")
        try:
            context.bot.send_message(user_id, "📜 A new task has been assigned.\nUse /mytasks to view it.")
        except Exception as e:
            print(f"Task DM error to {user_id}: {e}")

    context.job_queue.run_once(lambda ctx: tally_votes(chat_id, ctx), 90)
    
def tally_votes(chat_id, context: CallbackContext):
    votes = db.games[chat_id].get("votes", {})
    if not votes:
        context.bot.send_message(chat_id, "❌ No votes recorded.")
        return

    tally = Counter()

    # Track abstain task progress
    for voter_id in db.get_alive_players(chat_id):
        voted = voter_id in votes
        db.check_abstain(voter_id, voted)

    # Notify allies
    for voter_id, target_id in votes.items():
        db.notify_allies_vote(chat_id, voter_id, target_id, context)

    # Count valid votes (skip protected targets & disabled voters)
    for voter, target in votes.items():
        if db.is_player_protected(target) or db.is_immune(chat_id, target):
            continue
        if db.is_vote_disabled(chat_id, voter):
            continue
        tally[target] += 1

    if not tally:
        context.bot.send_message(chat_id, "🛡️ All votes were blocked or invalid.")
        return
    # Check if Core Reverser power is active and not used
    core_reverser = db.get_core_reverser(chat_id)
    if core_reverser and not db.has_used_core_shuffle(core_reverser):
        from engine.animation import core_shuffle_animation
        core_shuffle_animation(context.bot, chat_id)

        # Shuffle votes
        shuffled_votes = list(tally.elements())
        random.shuffle(shuffled_votes)
        tally = Counter(shuffled_votes)
    
        # Mark as used
        db.mark_core_shuffle_used(core_reverser)
    
        # Optional: Alert the group
        context.bot.send_message(chat_id, f"🌀 *The Core twists... fate has been shuffled by @{db.get_username(core_reverser)}!*", parse_mode='Markdown')
    
    target_id, count = tally.most_common(1)[0]
    target_username = db.get_username(target_id)

    if db.is_player_protected(target_id):
        lumen_priest_animation(context.bot, chat_id, target_username)
        context.bot.send_message(
            chat_id,
            f"🛡️ @{target_username} was protected! No one is eliminated this round."
        )
        db.clear_votes(chat_id)
        db.auto_complete_tasks()
        # ✨ Check Ascended vote immunity
    elif db.get_user_role(target_id) == "Ascended" and not db.has_used_vote_immunity(target_id):
        db.consume_vote_immunity(target_id)
        context.bot.send_message(chat_id, f"✨ @{target_username} resisted elimination with divine immunity!")
        db.clear_votes(chat_id)
        db.auto_complete_tasks()
    return
    else:
        db.kill_player(chat_id, target_id)
        context.bot.send_message(
            chat_id,
            f"⚖️ @{target_username} eliminated with {count} votes."
        )
        db.clear_votes(chat_id)
        db.auto_complete_tasks()

    # ✅ Only one check for winner after the round resolves
    check_win_conditions(chat_id, context)

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
    
def trigger_false_prophecy(chat_id, context):
    prophecy_lines = [
        "🌫️ *A False Vision descends...* The sky whispers lies.",
        "🪞 *Reality fractures...* Not all victories are as they seem.",
    ]
    context.bot.send_message(chat_id, random.choice(prophecy_lines), parse_mode="Markdown")
    db.games[chat_id]["false_prophecy"] = True

def reveal_false_prophecy(chat_id, user_id, context):
    if db.get_player_role(chat_id, user_id) in ["Oracle", "Light Herald"]:
        context.bot.send_message(user_id, "🔮 You see through the illusion. A false victory looms.")

def start_final_echo(chat_id, context):
    context.bot.send_message(chat_id, "🌌 *The Core fractures. The Final Echo begins.* Choose your destiny in private.", parse_mode="Markdown")
    players = db.get_alive_players(chat_id)
    options = ["Save the Core", "Destroy the Core", "Escape the Core"]
    buttons = [[InlineKeyboardButton(opt, callback_data=f"echo_{opt.lower().replace(' ', '_')}")] for opt in options]
    for uid in players:
        context.bot.send_message(uid, "What will you choose?", reply_markup=InlineKeyboardMarkup(buttons))

def resolve_final_echo(chat_id, context):
    votes = db.games[chat_id].get("echo_votes", {})
    counts = Counter(votes.values())
    dominant = counts.most_common(1)[0][0] if counts else None
    if dominant == "destroy_the_core":
        context.bot.send_message(chat_id, "🔥 *The Core shatters! All alliances crumble.* Only traitors claim glory.")
    elif dominant == "save_the_core":
        context.bot.send_message(chat_id, "🛡️ *The Core stabilizes. Purified forces claim Aether's future.*")
    elif dominant == "escape_the_core":
        context.bot.send_message(chat_id, "🌫️ *You escape the endless loop, vanishing into myth.*")

