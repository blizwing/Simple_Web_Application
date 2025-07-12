import sqlite3
from typing import List, Optional

from models import Item, ItemCreate

DB_FILE = "items.db"

# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------
_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
_conn.row_factory = sqlite3.Row

_conn.execute(
    """CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            locked INTEGER NOT NULL DEFAULT 0
        )"""
)

# Seed default items (id 1..5, locked)
def _ensure_defaults():
    defaults = [
        (1, "Laptop", "High-end gaming laptop", 1500.00),
        (2, "Smartphone", "Latest Android phone", 799.99),
        (3, "Headphones", "Noise-cancelling", 199.50),
        (4, "Backpack", "Waterproof travel pack", 59.99),
        (5, "Coffee Mug", "Ceramic 12oz mug", 12.00),
    ]
    for did, name, desc, price in defaults:
        row = _conn.execute("SELECT id FROM items WHERE id=?", (did,)).fetchone()
        if not row:
            _conn.execute(
                "INSERT INTO items (id, name, description, price, locked) VALUES (?,?,?,?,1)",
                (did, name, desc, price),
            )
    _conn.commit()

_ensure_defaults()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _next_id() -> int:
    row = _conn.execute("SELECT MAX(id) FROM items").fetchone()
    max_id = row[0] if row and row[0] is not None else 0
    return max_id + 1


def list_items() -> List[Item]:
    rows = _conn.execute(
        "SELECT id, name, description, price FROM items ORDER BY id"
    ).fetchall()
    return [Item(**dict(r)) for r in rows]


def create_item(item_data: ItemCreate) -> Item:
    if item_data.id is not None and item_data.id <= 5:
        raise ValueError("Cannot create item with reserved id")

    new_id = item_data.id if item_data.id is not None else _next_id()

    row = _conn.execute("SELECT id FROM items WHERE id=?", (new_id,)).fetchone()
    if row:
        raise ValueError(f"Item with id={new_id} already exists")

    _conn.execute(
        "INSERT INTO items (id, name, description, price, locked) VALUES (?,?,?,?,0)",
        (new_id, item_data.name, item_data.description, item_data.price),
    )
    _conn.commit()

    return Item(id=new_id, name=item_data.name, description=item_data.description, price=item_data.price)


def get_item(item_id: int) -> Optional[Item]:
    row = _conn.execute(
        "SELECT id, name, description, price FROM items WHERE id=?", (item_id,)
    ).fetchone()
    return Item(**dict(row)) if row else None


def _is_locked(item_id: int) -> bool:
    row = _conn.execute("SELECT locked FROM items WHERE id=?", (item_id,)).fetchone()
    return bool(row[0]) if row else False


def update_item(item_id: int, item_data: Item) -> Optional[Item]:
    if _is_locked(item_id):
        return None

    row = _conn.execute("SELECT id FROM items WHERE id=?", (item_id,)).fetchone()
    if not row:
        return None

    _conn.execute(
        "UPDATE items SET name=?, description=?, price=? WHERE id=?",
        (item_data.name, item_data.description, item_data.price, item_id),
    )
    _conn.commit()
    return Item(id=item_id, name=item_data.name, description=item_data.description, price=item_data.price)


def delete_item(item_id: int) -> Optional[Item]:
    if _is_locked(item_id):
        return None

    row = _conn.execute(
        "SELECT id, name, description, price FROM items WHERE id=?", (item_id,)
    ).fetchone()
    if not row:
        return None

    _conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    _conn.commit()
    return Item(**dict(row))
