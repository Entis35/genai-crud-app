from fastapi import HTTPException
from ..models.items import Item


# CRUD Operations (Database)
def insert_item(state, db):
    """Inserts a new item into the database."""
    try:
        new_item = Item(name=state["item"]["name"], description=state["item"]["description"])
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        state["result"] = {"message": "Item inserted", "id": new_item.id}
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_one_item(state, db):
    """Retrieves a single item by ID."""
    try:
        item = db.query(Item).filter(Item.id == state["item_id"]).first()
        if not item:
            state["result"] = {"error": "Item not found"}
        else:
            state["result"] = {"id": item.id, "name": item.name, "description": item.description}
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_all_items(state, db):
    """Retrieves all items from the database."""
    try:
        items = db.query(Item).all()
        state["result"] = [{"id": i.id, "name": i.name, "description": i.description} for i in items]
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

  
def update_item(state, db):
    """Updates an existing item by ID."""
    try:
        item = db.query(Item).filter(Item.id == state["item_id"]).first()
        if not item:
            state["result"] = {"error": "Item not found"}
        else:
            item.name = state["item"]["name"]
            item.description = state["item"]["description"]
            db.commit()
            state["result"] = {"message": "Item updated"}
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
