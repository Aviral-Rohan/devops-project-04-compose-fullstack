import os

from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=2000)
db = client[os.environ.get("MONGO_DB", "brewcart")]

SEED_MENU = [
    {"id": 1, "name": "Espresso", "price": 120},
    {"id": 2, "name": "Cappuccino", "price": 180},
    {"id": 3, "name": "Latte", "price": 170},
    {"id": 4, "name": "Cold Brew", "price": 190},
    {"id": 5, "name": "Mocha", "price": 210},
]


def menu_collection():
    col = db.menu
    if col.estimated_document_count() == 0:
        col.insert_many([dict(item) for item in SEED_MENU])
    return col


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify(status="ok", service="api", db="up")
    except Exception:
        return jsonify(status="error", service="api", db="down"), 503


@app.get("/menu")
def menu():
    return jsonify(list(menu_collection().find({}, {"_id": 0}).sort("id")))


@app.get("/orders")
def list_orders():
    return jsonify(list(db.orders.find({}, {"_id": 0})))


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    item = data.get("item")
    if not item:
        return jsonify(error="item is required"), 400
    order = {"item": item, "qty": int(data.get("qty", 1))}
    db.orders.insert_one(dict(order))
    return jsonify(status="created", **order), 201
