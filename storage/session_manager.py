import json
import os
from pathlib import Path
from config import PROJECT_ROOT

STORAGE_DIR = PROJECT_ROOT / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

MESSAGES_FILE = STORAGE_DIR / "messages.json"
STATE_FILE = STORAGE_DIR / "state.json"


def load_messages() -> dict:
    """Load all messages from disk. Returns nested dict structure."""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_messages(messages: dict):
    """Save all messages to disk."""
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_state() -> dict:
    """Load session state (current KB and role)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_kb_id": None,
        "current_role": "qixia"
    }


def save_state(state: dict):
    """Save session state to disk."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_messages(messages: dict, kb_id: str, role: str) -> list:
    """Get messages for specific KB and role. Returns empty list if not found."""
    return messages.get(kb_id, {}).get(role, [])


def add_message(messages: dict, kb_id: str, role: str, msg: dict):
    """Add a message to the specific KB and role conversation."""
    if kb_id not in messages:
        messages[kb_id] = {}
    if role not in messages[kb_id]:
        messages[kb_id][role] = []
    messages[kb_id][role].append(msg)


def clear_messages_for_context(messages: dict, kb_id: str, role: str):
    """Clear messages for specific KB and role."""
    if kb_id in messages and role in messages[kb_id]:
        messages[kb_id][role] = []


def clear_session():
    """Clear all session data from disk."""
    if os.path.exists(MESSAGES_FILE):
        os.remove(MESSAGES_FILE)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)