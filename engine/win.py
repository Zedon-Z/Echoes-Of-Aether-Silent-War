from storage import database as db

def check_for_winner(chat_id):
    players = db.get_alive_players(chat_id)
    factions = [db.get_player_faction(pid) for pid in players]
    unique_factions = set(factions)

    # Goat win condition
    if "Goat" in [db.get_user_role(pid) for pid in players] and len(players) <= 3:
        return "🐐 GOAT wins by surviving to final 3!"

    # Solo role conditions
    for pid in players:
        role = db.get_user_role(pid)
        if role == "Archivist" and db.get_relic_count(pid) >= 3:
            return f"📚 Archivist ({db.get_username(pid)}) wins with relics!"
        if role == "Puppetmaster" and db.used_thread(pid):
            return f"🧵 Puppetmaster ({db.get_username(pid)}) wins via control!"

    # Faction win condition (one team left)
    if len(unique_factions) == 1:
        return f"🏁 {unique_factions.pop()} wins! All others eliminated."

    return None  # No winner yet
