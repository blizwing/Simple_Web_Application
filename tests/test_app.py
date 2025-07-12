import os
import sys
import pathlib
import sqlite3
import importlib

# ensure project root is on path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import storage
import main
from fastapi.testclient import TestClient


# Fixture to provide a fresh TestClient with isolated database for each test
import pytest

SCHEMA_SQL = """CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        locked INTEGER NOT NULL DEFAULT 0
    )"""

@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "items.db"
    if hasattr(storage, "_conn"):
        try:
            storage._conn.close()
        except Exception:
            pass
    storage.DB_FILE = str(db_path)
    storage._conn = sqlite3.connect(storage.DB_FILE, check_same_thread=False)
    storage._conn.row_factory = sqlite3.Row
    storage._conn.execute(SCHEMA_SQL)
    storage._conn.commit()
    storage._ensure_defaults()
    importlib.reload(main)
    client = TestClient(main.app)
    yield client
    client.close()
    storage._conn.close()

def test_root(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_login(client):
    resp = client.post('/login', json={'username': 'u', 'password': 'p'})
    assert resp.status_code == 200
    assert resp.json()['token'] == 'dummy-token-for-u'


def test_list_defaults(client):
    resp = client.get('/items')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    assert data[0]['id'] == 1


def test_get_item_not_found(client):
    resp = client.get('/items/999')
    assert resp.status_code == 404


def test_get_existing_item(client):
    resp = client.get('/items/1')
    assert resp.status_code == 200
    assert resp.json()['id'] == 1


def test_create_item_success(client):
    new_item = {'name': 'Pen', 'description': 'Blue ink', 'price': 1.5}
    resp = client.post('/items', json=new_item)
    assert resp.status_code == 201
    created = resp.json()
    assert created['id'] > 5
    for k in new_item:
        assert created[k] == new_item[k]


def test_create_item_reserved_id(client):
    resp = client.post('/items', json={'id': 1, 'name': 'X', 'price': 1})
    assert resp.status_code == 400


def test_create_item_duplicate(client):
    resp1 = client.post('/items', json={'id': 10, 'name': 'A', 'price': 2})
    assert resp1.status_code == 201
    resp2 = client.post('/items', json={'id': 10, 'name': 'B', 'price': 3})
    assert resp2.status_code == 400


def test_update_locked_item(client):
    resp = client.put('/items/1', json={'id': 1, 'name': 'X', 'price': 1})
    assert resp.status_code == 404


def test_update_item_success(client):
    create = client.post('/items', json={'name': 'Book', 'price': 5})
    item_id = create.json()['id']
    resp = client.put(f'/items/{item_id}', json={'id': item_id, 'name': 'Book2', 'price': 6})
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Book2'


def test_update_item_not_found(client):
    resp = client.put('/items/999', json={'id': 999, 'name': 'X', 'price': 1})
    assert resp.status_code == 404


def test_delete_locked_item(client):
    resp = client.delete('/items/1')
    assert resp.status_code == 404


def test_delete_item_success(client):
    create = client.post('/items', json={'name': 'Temp', 'price': 1})
    item_id = create.json()['id']
    resp = client.delete(f'/items/{item_id}')
    assert resp.status_code == 204
    resp2 = client.get(f'/items/{item_id}')
    assert resp2.status_code == 404


def test_delete_item_not_found(client):
    resp = client.delete('/items/999')
    assert resp.status_code == 404


def test_upload_file(client):
    resp = client.post('/upload', files={'file': ('test.txt', b'hello')})
    assert resp.status_code == 200
    assert resp.json()['size'] == 5


def test_slow_endpoint(client):
    resp = client.get('/slow', params={'delay': 0})
    assert resp.status_code == 200
    assert resp.json()['delay'] == 0
