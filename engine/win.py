from storage import database as db

def check_for_winner(chat_id):
    players = db.get_alive_players(chat_id)

    if not players:
        return "💀 Everyone perished. The void claims Aether."

    factions = [db.get_player_faction(pid) for pid in players]
    roles = {pid: db.get_user_role(pid) for pid in players}
    unique_factions = set(factions)

    # 🐐 1. GOAT WIN
    for pid in players:
        if roles[pid] == "Goat" and len(players) <= 3:
            return f"🐐 @{db.get_username(pid)} (Goat) wins by surviving to the Final 3!"

    # 📚 2. ARCHIVIST RELIC WIN
    for pid in players:
        if roles[pid] == "Archivist" and db.get_relic_count(pid) >= 3:
            return f"📚 @{db.get_username(pid)} (Archivist) wins by collecting 3 relics!"

    # 🧵 3. PUPPETMASTER THREAD WIN
    for pid in players:
        if roles[pid] == "Puppetmaster" and db.used_thread(pid):
            return f"🧵 @{db.get_username(pid)} (Puppetmaster) wins by total mind control!"

    # 🩸 4. DAGGER PROPHET DEATH WIN
    for pid in players:
        if roles[pid] == "Dagger Prophet" and db.correct_death_prediction(pid):
            return f"🔮 @{db.get_username(pid)} (Dagger Prophet) wins by fulfilling a bloody prophecy!"

    # 🧪 5. BLOOD ALCHEMIST RELIC ABSORB WIN
    for pid in players:
        if roles[pid] == "Blood Alchemist" and db.has_absorbed_relic(pid):
            return f"🧪 @{db.get_username(pid)} (Blood Alchemist) wins by consuming the essence of the fallen."

    # 💋 6. KISS OF ECLIPSE WIN
    for pid in players:
        if roles[pid] == "Kiss Of Eclipse" and db.kissed_all_factions(pid):
            return f"💋 @{db.get_username(pid)} (Kiss of Eclipse) wins by silencing all of Aether... romantically."

    # 🎯 7. ECHO HUNTER LONE WOLF WIN (3-player trigger)
    for pid in players:
        if roles[pid] == "Echo Hunter" and len(players) == 3:
            return f"🎯 @{db.get_username(pid)} (Echo Hunter) claims the hunt — victory under 3 survivors!"
            
    # ❤️ 8. COUPLE WIN ---
    # 💖 Eclipse Couple Win
couples = db.games[chat_id].get("couples", {})
for kisser, kissed in couples.items():
    if kisser in players and kissed in players:
        from engine.animation import eclipse_win_animation
        eclipse_win_animation(db.get_bot(), chat_id, db.get_username(kisser), db.get_username(kissed))
        return f"💞 Lovers of the Eclipse ascend together!"
        
    # ⚙️ 9. CORE REVERSER VICTORY (if a twist round vote shuffle leads to unexpected death and condition met)
    for pid in players:
        if roles[pid] == "Core Reverser" and db.triggered_core_reversal(pid):
            return f"🌀 @{db.get_username(pid)} (Core Reverser) destabilized fate itself. Victory from the shadows!"
     
    # 🟪 10. FACTION WIN (Whispered Blades, Luminae, Nexus, Rogue, etc.)
    if len(unique_factions) == 1:
        faction = unique_factions.pop()
        return f"🏆 {faction} dominates Aether. All others fell before their will."

    # 🌌 11. FINAL ECHO ENDGAME
    if db.is_final_echo_active(chat_id):
        dominant_echo = db.get_dominant_echo_vote(chat_id)
        if dominant_echo == "Destroy":
            top_betrayer = db.get_top_betrayer(chat_id)
            if top_betrayer:
                return f"💥 Chaos wins! @{db.get_username(top_betrayer)} becomes the *True Echo of Destruction*."
            return "💥 Chaos reigns. The world is destroyed. No victors remain."
        elif dominant_echo == "Save":
            return "🕊️ Hope prevails. The Core survives and the Luminae ascend!"
        elif dominant_echo == "Escape":
            escapers = db.get_escapees(chat_id)
            if escapers:
                names = ", ".join(f"@{db.get_username(uid)}" for uid in escapers)
                return f"🚀 Escapees: {names} survived the collapse!"
            return "🚀 A few managed to escape. Aether's future is... unknown."

    # ❌ 12. NO WINNER YET
    return None
