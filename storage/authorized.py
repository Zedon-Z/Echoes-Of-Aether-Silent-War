import json
import os

FILE_PATH = "storage/authorized_groups.json"

def load_authorized_groups():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def save_authorized_groups(groups):
    with open(FILE_PATH, "w") as f:
        json.dump(groups, f)

def is_group_authorized(chat_id):
    return chat_id in load_authorized_groups()

def add_group(chat_id):
    groups = load_authorized_groups()
    if chat_id not in groups:
        groups.append(chat_id)
        save_authorized_groups(groups)
        return True
    return False

def remove_group(chat_id):
    groups = load_authorized_groups()
    if chat_id in groups:
        groups.remove(chat_id)
        save_authorized_groups(groups)
        return True
    return False
