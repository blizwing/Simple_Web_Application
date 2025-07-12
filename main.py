from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from models import Item, UserCredentials, ItemCreate
import storage

app = FastAPI()

# Allow JMeter (or any client) from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
async def login(creds: UserCredentials):
    # dummy auth: accept any username/password
    return {"token": f"dummy-token-for-{creds.username}"}

@app.get("/items")
async def read_items():
    return storage.list_items()

@app.post("/items", status_code=201, response_model=Item)
async def create_item(item: ItemCreate):
    try:
        return storage.create_item(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    item = storage.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    updated = storage.update_item(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    deleted = storage.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return its size."""
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

@app.get("/slow")
async def slow_endpoint(delay: int = 2):
    """Simulate a slow service that waits for ``delay`` seconds."""
    await asyncio.sleep(delay)
    return {"status": "done", "delay": delay}

@app.get("/")
async def root():
    return {"status": "ok"}
