from typing import Dict
from models import Item, ItemCreate

# ── STATIC BOOTSTRAP DATA ──────────────────────────────────────────────────────
_items: Dict[int, Item] = {
    1: Item(id=1, name="Laptop",      description="High-end gaming laptop", price=1500.00),
    2: Item(id=2, name="Smartphone",  description="Latest Android phone",    price= 799.99),
    3: Item(id=3, name="Headphones",  description="Noise-cancelling",         price= 199.50),
    4: Item(id=4, name="Backpack",    description="Waterproof travel pack",    price=  59.99),
    5: Item(id=5, name="Coffee Mug",  description="Ceramic 12oz mug",           price=  12.00),
}

# next ID is one more than the highest preloaded key
_next_id = max(_items.keys()) + 1
# ──────────────────────────────────────────────────────────────────────────────

def list_items():
    return list(_items.values())

def create_item(item_data: ItemCreate) -> Item:
    global _next_id

    # 1) Decide the new ID
    if item_data.id is not None:
        new_id = item_data.id
        if new_id in _items:
            raise ValueError(f"Item with id={new_id} already exists")
        # ensure future auto-ids don’t clash
        _next_id = max(_next_id, new_id + 1)
    else:
        new_id = _next_id
        _next_id += 1

    # 2) Build & store
    item = Item(
        id=new_id,
        name=item_data.name,
        description=item_data.description,
        price=item_data.price
    )
    _items[new_id] = item
    return item

def get_item(item_id: int):
    return _items.get(item_id)

def update_item(item_id: int, item_data):
    if item_id in _items:
        updated = Item(id=item_id, **item_data.dict())
        _items[item_id] = updated
        return updated
    return None

def delete_item(item_id: int):
    return _items.pop(item_id, None)
