
from storage import database as db

def use_item(user_id, item_name):
    inventory = db.get_inventory(user_id)

    if item_name not in inventory:
        return "❌ You don’t have that item."

    response = "🌀 Nothing happens. Maybe it’s a fake?"

    if item_name == "truth_crystal":
        all_roles = db.reveal_all_roles()
        response = "🔍 *Truth Revealed:*\n" + "\n".join(all_roles)

    elif item_name == "shadow_ring":
        db.grant_immunity(user_id)
        response = "🕳 You are now immune to death for one night."

    elif item_name == "goat_scroll":
        db.trigger_goat_prophecy()
        response = "🐐 A ghostly goat bellows... destiny shifts."

    elif item_name == "core_key":
        if db.check_nexus_control(user_id):
            db.set_nexus_winner(user_id)
            response = "⚙️ You activated the Core Key. Nexus Guild wins!"
        else:
            response = "The Core is not aligned. The key does nothing..."

    # Remove item after use
    db.remove_item(user_id, item_name)
    return response
